from fastapi import APIRouter, Depends, Request, status, WebSocket, WebSocketDisconnect, BackgroundTasks
from sqlalchemy.orm import Session
from datetime import datetime, timezone
import httpx
import re
import os
from io import BytesIO

from ..models.base import get_db, SessionLocal
from ..models.work import Work, WorkStatus, WorkType, ShareStatus
from ..models.credit_record import CreditType
from ..services.credit_service import add_credits as credit_service_add_credits
from ..models.generation_model import GenerationModel, APILibrary
from ..models.workflow import Workflow
from ..models.payment_order import PaymentOrder, PaymentStatus
from ..models.user import User, UserSource
from ..utils.responses import success_response, error_response
from ..utils.logger import logger, log_generation_complete, log_payment
from ..utils.work_metadata import generate_work_metadata
from ..services.storage import get_storage_service
from ..services.websocket import get_connection_manager
from ..services.thumbnail import generate_image_thumbnail, generate_video_thumbnail, generate_image_thumbnail_webp, generate_video_thumbnail_webp, compress_video_h264
from ..models.generation_config import get_model_cost, MODELS
from ..services.providers.factory import ProviderFactory
from ..services.email import send_recharge_success_email
from ..utils.notification import create_notification
from ..models.notification import NotificationType
from ..services.stripe_service import get_stripe_service
from ..utils.auth import decode_access_token

router = APIRouter()


def _ensure_work_has_prompt_url(work: Work, db: Session) -> None:
    """
    Ensure work has short_code and url_slug so prompt page is accessible immediately.
    If missing, generate short_code and set url_slug = short_code (background task will refine url_slug later).
    """
    if work.short_code and work.url_slug:
        return
    import secrets
    import string
    alphabet = string.ascii_letters + string.digits
    if not work.short_code:
        work.short_code = ''.join(secrets.choice(alphabet) for _ in range(11))
    work.url_slug = work.url_slug or work.short_code
    db.commit()
    logger.info(f"Work {work.id} prompt URL assigned: short_code={work.short_code}, url_slug={work.url_slug}")


async def process_webhook_success(work_id: int, result: dict, work_type: str, user_id: int, user_handle: str, model_name: str):
    """
    Handle the heavy lifting (metadata generation, download, upload, thumbnail) in a background task.
    In Scenario A: We already set status=SUCCESS and file_url=provider_url in the main webhook.
    
    Execution order:
    1. Initialize variables (storage, is_video, file_ext)
    2. Generate metadata (Gemini AI) - title, description, tags, category
    3. Generate short_code and url_slug, then SAVE metadata to DB (prompt page accessible)
    4. Download file from provider
    5. Upload to R2/OSS (generates storage_key), update file_url
    6. Generate thumbnail (uses OSS URL)
    7. Generate canonical_url and thumbnail_url (needs storage_key + title)
    8. Update database with remaining fields (canonical_url, thumbnail_url, auto_moderated)
    """
    db = SessionLocal()
    try:
        work = db.query(Work).filter(Work.id == work_id).first()
        if not work:
            return
        
        # Check if already fully processed
        if work.status == WorkStatus.FAILED:
            return
        
        if work.storage_key and work.auto_moderated:
            # Already fully processed
            return

        output_url = result.get("file_url")
        storage = get_storage_service()
        is_video = work_type in ["text-to-video", "image-to-video", "text2video", "img2video"]
        file_ext = "mp4" if is_video else "jpg"

        # 1b. URL/Content-Type fallback: infer image vs video from actual URL or response type
        if output_url:
            from urllib.parse import urlparse
            path = urlparse(output_url).path or ""
            path_lower = path.lower()
            video_extensions = (".mp4", ".webm", ".mov", ".avi", ".mkv", ".m4v")
            image_extensions = (".jpg", ".jpeg", ".png", ".webp", ".gif", ".bmp")
            url_suggests_video = any(path_lower.endswith(ext) for ext in video_extensions)
            url_suggests_image = any(path_lower.endswith(ext) for ext in image_extensions)
            if url_suggests_video and not url_suggests_image:
                is_video = True
                file_ext = "mp4"
                logger.info(f"Work {work_id}: URL extension suggests video, using video path")
            elif url_suggests_image and not url_suggests_video:
                is_video = False
                if path_lower.endswith(".png"):
                    file_ext = "png"
                elif path_lower.endswith(".webp"):
                    file_ext = "webp"
                else:
                    file_ext = "jpg"
                logger.info(f"Work {work_id}: URL extension suggests image, using image path (ext={file_ext})")
            elif not url_suggests_video and not url_suggests_image:
                try:
                    async with httpx.AsyncClient() as client:
                        head_resp = await client.head(output_url, timeout=10.0, follow_redirects=True)
                    content_type = (head_resp.headers.get("content-type") or "").split(";")[0].strip().lower()
                    if content_type.startswith("video/"):
                        is_video = True
                        file_ext = "mp4"
                        logger.info(f"Work {work_id}: Content-Type {content_type} suggests video")
                    elif content_type.startswith("image/"):
                        is_video = False
                        file_ext = "jpg"
                        logger.info(f"Work {work_id}: Content-Type {content_type} suggests image")
                except Exception as e:
                    logger.warning(f"Work {work_id}: HEAD request failed for URL fallback: {e}, keeping work_type")
        
        # 2. Generate Metadata:  prompt （Gemini /  / ）
        from ..models.work import ShareStatus
        # Prompt ： Gemini，； 0 「」
        PROMPT_LENGTH_FOR_GEMINI = 80
        prompt_text = (work.prompt or "").strip()
        prompt_len = len(prompt_text)
        
        title = None
        description = None
        tags = []
        category = None
        
        if prompt_len == 0:
            title = "Untitled Work"
            description = "Undefined description"
            tags = []
            category = "photography"
            logger.info(f"Work {work_id}: prompt empty, using default title/description")
        elif prompt_len <= PROMPT_LENGTH_FOR_GEMINI:
            #  prompt： title、description， Gemini
            try:
                title, description = generate_work_metadata(prompt_text, model_name)
            except Exception as e:
                logger.warning(f"Work {work_id}: generate_work_metadata failed: {e}. Using fallback.")
                title = prompt_text[:55] + ("..." if len(prompt_text) > 55 else "")
                description = f"{model_name} Prompt: \"{prompt_text[:100]}...\" Created with VidGen." if len(prompt_text) > 100 else f"{model_name} Prompt: \"{prompt_text}\" Created with VidGen."
            tags = []
            category = "photography"
            logger.info(f"Work {work_id}: prompt length {prompt_len} <= {PROMPT_LENGTH_FOR_GEMINI}, using concatenation for title/description")
        else:
            #  prompt： Gemini  title、description、tags、category
            try:
                from ..services.gemini_service import get_gemini_service
                from ..models.category_page import CategoryPage
                
                all_categories = db.query(CategoryPage).all()
                categories_data = [cat.to_dict(include_children=False) for cat in all_categories]
                
                gemini_service = get_gemini_service(db_session=db)
                generated = gemini_service.generate_all(
                    prompt_content=prompt_text,
                    categories=categories_data
                )
                
                title = generated.get("title", "")
                description = generated.get("description", "")
                tags = generated.get("tags", [])
                category = generated.get("category")
            except Exception as e:
                logger.warning(f"Gemini generation failed for work {work_id}: {str(e)}. Falling back.")
                title, description = generate_work_metadata(prompt_text, model_name)
                tags = []
                category = "photography"
            
            if not title or not title.strip():
                title, description = generate_work_metadata(prompt_text, model_name)
        
        # 3. short_code/url_slug: reuse if already set (so prompt page was available immediately), else generate
        import secrets
        import string
        from ..utils.url_slug import generate_url_slug
        from ..models.moderation import NSFWStatus
        
        if not work.short_code:
            alphabet = string.ascii_letters + string.digits
            short_code = ''.join(secrets.choice(alphabet) for _ in range(11))
            work.short_code = short_code
        url_slug = generate_url_slug(work.short_code, title)
        
        # 🚀 IMMEDIATE UPDATE: Save metadata to DB so prompt page can be accessed
        work.url_slug = url_slug
        work.title = title
        work.description = description
        work.share_name = title if not work.share_name else work.share_name
        work.category = category if category else "photography"
        work.tags = tags
        
        # 🚀 （private）， BLOCKED（BLOCKED ）
        if work.nsfw_status == NSFWStatus.BLOCKED.value:
            # ，
            work.is_shared = False
            work.share_status = None
        else:
            # （）
            work.is_shared = False
            if work.nsfw_status == NSFWStatus.APPROVED.value:
                work.share_status = ShareStatus.APPROVED
            # PENDING  is_shared=False，
        
        db.commit()
        logger.info(f"Work {work_id} metadata saved: short_code={work.short_code}, url_slug={work.url_slug}, title={title}")
        
        # 4. Download file from provider
        async with httpx.AsyncClient() as client:
            response = await client.get(output_url, timeout=60.0)
            response.raise_for_status()
            file_data = response.content
        
        # 5. Upload to R2/OSS
        # Generate storage key
        file_key = storage.generate_key(
            filename=f"output.{file_ext}"
        )
        storage_key = file_key.split('.')[0] if '.' in file_key else file_key
        
        file_obj = BytesIO(file_data)
        new_file_url = storage.upload_file(
            file_obj=file_obj,
            key=file_key,
            content_type="video/mp4" if is_video else "image/jpeg",
            public=False
        )
        
        # 🚀 UPDATE: Switch from Provider URL to R2 URL as soon as upload succeeds
        work.file_url = new_file_url
        work.storage_key = storage_key
        db.commit()
        logger.info(f"Work {work_id} URL switched from Provider to R2: {new_file_url}")

        # 6. THUMBNAIL LOGIC
        thumbnail_url = None
        thumbnail_key_original = None
        try:
            if is_video:
                # 🎬 Video compression
                compressed_video_data = await compress_video_h264(
                    video_url=new_file_url,
                    max_height=480,
                    crf=23
                )
                
                if compressed_video_data:
                    compressed_key = f"{storage_key}.mp4"
                    thumbnail_key_original = compressed_key
                    compressed_obj = BytesIO(compressed_video_data)
                    storage.upload_file(
                        file_obj=compressed_obj,
                        key=compressed_key,
                        content_type="video/mp4",
                        public=False
                    )
                    logger.info(f"Compressed video uploaded for work {work_id}")
            else:
                # 🖼️ Image Thumbnail
                thumbnail_data = await generate_image_thumbnail_webp(
                    image_url=new_file_url,
                    max_width=800,
                    max_height=800,
                    quality=85
                )
                
                thumbnail_key = f"{storage_key}.webp"
                thumbnail_key_original = thumbnail_key
                thumbnail_obj = BytesIO(thumbnail_data)
                storage.upload_file(
                    file_obj=thumbnail_obj,
                    key=thumbnail_key,
                    content_type="image/webp",
                    public=False
                )
                logger.info(f"Image WebP thumbnail uploaded for work {work_id}")
        except Exception as e:
            logger.error(f"Failed to generate thumbnail for work {work_id}: {str(e)}")
        
        # 7. Generate canonical_url and thumbnail_url (needs storage_key from OSS upload)
        canonical_url = storage.generate_canonical_url(storage_key, title, file_ext)
        
        if thumbnail_key_original:
            try:
                thumbnail_url = storage.generate_thumbnail_canonical_url(storage_key, title, is_video)
            except Exception:
                thumbnail_url = storage.get_public_url(thumbnail_key_original)

        # 8. Final DB update - only update remaining fields (metadata already saved in step 3)
        from sqlalchemy import update
        
        #  canonical_url、thumbnail_url  auto_moderated（3）
        update_values = {
            "thumbnail_url": thumbnail_url,
            "canonical_url": canonical_url,
            "auto_moderated": True
        }
        
        db.execute(
            update(Work).where(Work.id == work_id).values(**update_values)
        )
        db.commit()
        
        # Notify via WebSocket for metadata update (optional but good)
        ws_manager = get_connection_manager()
        await ws_manager.send_message(user_id, {
            "type": "work_metadata_updated",
            "work_id": work_id,
            "title": title,
            "url_slug": url_slug
        })
        
        logger.info(f"Background processing complete for work {work_id}")
        
    except Exception as e:
        logger.error(f"Error in background processing: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
    finally:
        db.close()

@router.post("/replicate/{work_id}")
async def replicate_webhook(
    work_id: int,
    request: Request,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Replicate completion callback. For workflow models: run node completion and trigger next node(s).
    When no workflow or no node_id: return 200 so callbacks do not retry.
    """
    try:
        payload = await request.json()
        work = db.query(Work).filter(Work.id == work_id).first()
        if not work:
            return error_response(message="Work not found", status_code=status.HTTP_404_NOT_FOUND)

        if work.status in [WorkStatus.SUCCESS, WorkStatus.FAILED] and work.auto_moderated:
            return success_response(message=f"Work already processed with status: {work.status.value}")

        # Workflow: when Replicate calls with ?node_id=xxx (or final node without node_id), process and trigger next
        generation_model = db.query(GenerationModel).filter(
            GenerationModel.model_key == work.model_key
        ).first()
        if generation_model and generation_model.workflow_id:
            node_id = request.query_params.get("node_id")
            if not node_id:
                # Final node uses webhook_url without node_id; infer last api_call node
                from ..services.workflow_executor import WorkflowExecutor
                workflow = db.query(Workflow).filter(Workflow.id == generation_model.workflow_id).first()
                if workflow:
                    valid_node_types = {'api_call', 'prompt_input', 'image_default', 'video_default', 'param_input', 'prompt_default_hidden', 'media_list_default'}
                    valid_nodes = [n for n in workflow.nodes if n.get("type") in valid_node_types]
                    executor = WorkflowExecutor(db_session=db)
                    execution_order = executor._topological_sort(valid_nodes, workflow.edges or [])
                    for nid in reversed(execution_order or []):
                        node = executor._get_node_by_id(valid_nodes, nid)
                        if node and node.get("type") == "api_call":
                            node_id = nid
                            break
            if node_id:
                logger.info(f"Workflow webhook for work {work_id} node_id={node_id}, processing")
                try:
                    await _handle_workflow_node_webhook(
                        work_id, node_id, payload, work, generation_model, db, background_tasks
                    )
                except Exception as e:
                    logger.error(f"Workflow webhook handling failed for work {work_id} node {node_id}: {e}")
                    import traceback
                    logger.error(traceback.format_exc())
                return success_response(message="OK")

        return success_response(message="OK")

    except Exception as e:
        logger.error(f"Webhook error: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return error_response(message="Internal error")


async def _handle_workflow_node_webhook(
    work_id: int,
    node_id: str,
    payload: dict,
    work: Work,
    generation_model: GenerationModel,
    db: Session,
    background_tasks: BackgroundTasks,
    result_override: dict = None,
):
    """Handle webhook for a workflow intermediate node.
    When result_override is provided (e.g. from polling get_status), use it instead of calling provider.handle_webhook.
    This allows sync providers (e.g. Gemini) to pass get_status result directly when triggered via polling.
    """
    try:
        workflow = db.query(Workflow).filter(Workflow.id == generation_model.workflow_id).first()
        if not workflow:
            logger.error(f"Workflow not found for work {work_id}")
            return error_response(message="Workflow not found")
        
        # Filter valid nodes (same as in executor)
        valid_node_types = {'api_call', 'prompt_input', 'image_default', 'video_default', 'param_input', 'prompt_default_hidden', 'media_list_default'}
        valid_nodes = [
            node for node in workflow.nodes 
            if node.get("type") in valid_node_types
        ]
        
        # Find the node that just completed (must be an api_call node)
        completed_node = None
        for node in workflow.nodes:
            if node.get("id") == node_id and node.get("type") == "api_call":
                completed_node = node
                break
        
        if not completed_node:
            logger.error(f"Node {node_id} not found in workflow {workflow.id}")
            return error_response(message="Node not found in workflow")
        
        # Get API to identify provider
        api_id = completed_node.get("api_id")
        api = db.query(APILibrary).filter(APILibrary.id == api_id).first()
        if not api:
            return error_response(message="API not found for node")
        
        if result_override is not None:
            result = result_override
        else:
            provider = ProviderFactory.get_provider(api.provider)
            result = await provider.handle_webhook(work_id, payload)
        
        if result.get("status") == "success":
            # Store node output in work.params for downstream nodes to access
            # Format: work.params["_workflow_nodes"][node_id] = {output: {...}, status: "success"}
            provider_url = result.get("file_url")
            
            # Get output_type from API configuration to determine output key
            output_type = api.output_type or 'string'
            node_data = completed_node.get("data", {})
            output_type_from_node = node_data.get("output_type") or output_type
            
            # Build output object with appropriate keys based on output_type
            output_obj = {
                "url": provider_url,
                "file_url": provider_url,  # Alias for compatibility
                **result  # Include all result fields
            }
            
            # Add type-specific keys for proper parameter mapping
            if output_type_from_node == "image":
                output_obj["image"] = provider_url
            elif output_type_from_node == "video":
                output_obj["video"] = provider_url
            
            node_output = {
                "output": output_obj,
                "status": "success"
            }
            
            logger.info(f"Storing node output with output_type={output_type_from_node}, keys={list(output_obj.keys())}")
            
            # Initialize workflow_nodes in params if not exists
            if not work.params:
                work.params = {}
            if "_workflow_nodes" not in work.params:
                work.params["_workflow_nodes"] = {}
            
            # Store node output
            work.params["_workflow_nodes"][node_id] = node_output
            
            # Mark params as modified for SQLAlchemy JSON field
            from sqlalchemy.orm.attributes import flag_modified
            flag_modified(work, "params")
            
            db.commit()
            logger.info(f"Stored output for workflow node {node_id} in work {work_id}")
            logger.info(f"Workflow nodes after storage: {list(work.params.get('_workflow_nodes', {}).keys())}")
            
            # Check if this is the final node (last api_call in order; execution_order[-1] may be an input node)
            from ..services.workflow_executor import WorkflowExecutor
            executor = WorkflowExecutor(db_session=db)
            execution_order = executor._topological_sort(valid_nodes, workflow.edges)
            last_api_call_node_id = None
            for nid in reversed(execution_order or []):
                n = executor._get_node_by_id(valid_nodes, nid)
                if n and n.get("type") == "api_call":
                    last_api_call_node_id = nid
                    break
            is_final_node = last_api_call_node_id is not None and node_id == last_api_call_node_id

            if is_final_node:
                # Final node: set file_url to vendor URL immediately so UI can show it; R2 processing will overwrite later
                # Use the same NSFW check logic as single API call
                from ..models.moderation import NSFWStatus
                nsfw_status = work.nsfw_status or NSFWStatus.APPROVED.value
                
                work.status = WorkStatus.SUCCESS
                work.file_url = provider_url
                work.nsfw_status = nsfw_status
                work.completed_at = datetime.now(timezone.utc)
                
                if nsfw_status == NSFWStatus.BLOCKED.value:
                    work.is_shared = False
                    work.share_status = None
                else:
                    work.is_shared = False  # Default to private
                    if nsfw_status == NSFWStatus.APPROVED.value:
                        work.share_status = ShareStatus.APPROVED
                
                _ensure_work_has_prompt_url(work, db)
                
                db.commit()
                
                # WebSocket notification
                ws_manager = get_connection_manager()
                await ws_manager.send_message(work.user_id, {
                    "type": "generation_complete",
                    "work_id": work_id,
                    "status": "success",
                    "file_url": provider_url,
                    "nsfw_status": nsfw_status
                })
                # Create notification so it appears in Notifications dropdown
                slug = work.url_slug or work.short_code
                if slug:
                    create_notification(
                        db,
                        work.user_id,
                        NotificationType.TASK_COMPLETE,
                        title="Your AI creation is ready",
                        content="Your creation has been generated successfully.",
                        link_url=f"/prompt/{slug}",
                    )
                # Background processing (work.type is str, Column String(50))
                background_tasks.add_task(
                    process_webhook_success,
                    work_id,
                    result,
                    work.type,
                    work.user_id,
                    work.user.handle,
                    work.model_name
                )
                return success_response(message="Workflow generation successful, processing metadata in background")
            else:
                # Intermediate node: find and trigger next node(s)
                next_node_ids = executor._get_next_nodes(node_id, workflow.edges)
                logger.info(f"Next node IDs for {node_id}: {next_node_ids}")
                
                if not next_node_ids:
                    logger.warning(f"No next nodes found for node {node_id} in work {work_id}")
                    return success_response(message="Intermediate node completed, but no next nodes found")
                
                # Check which next nodes are ready (all dependencies completed)
                completed_nodes = set(work.params.get("_workflow_nodes", {}).keys())
                completed_nodes.add(node_id)  # Include current node
                logger.info(f"Completed nodes: {list(completed_nodes)}")
                
                ready_nodes = []
                for next_node_id in next_node_ids:
                    is_ready = executor._are_dependencies_ready(next_node_id, workflow.edges, completed_nodes, valid_nodes)
                    logger.info(f"Node {next_node_id} dependencies ready: {is_ready}")
                    if is_ready:
                        ready_nodes.append(next_node_id)
                
                if not ready_nodes:
                    logger.info(f"Next nodes for {node_id} are not ready yet (dependencies pending) in work {work_id}")
                    logger.info(f"  Next node IDs: {next_node_ids}")
                    logger.info(f"  Completed nodes: {list(completed_nodes)}")
                    return success_response(message="Intermediate node completed, waiting for dependencies")
                
                # Execute ready nodes
                webhook_url = f"{os.getenv('BACKEND_URL', 'http://localhost:8000')}/api/webhook/replicate/{work_id}"
                execution_order = executor._topological_sort(valid_nodes, workflow.edges)
                is_final = execution_order and ready_nodes[0] == execution_order[-1]
                
                for next_node_id in ready_nodes:
                    next_node = executor._get_node_by_id(valid_nodes, next_node_id)
                    if not next_node:
                        logger.error(f"Next node {next_node_id} not found in workflow {workflow.id}")
                        continue
                    
                    try:
                        # Prepare context with user input and completed node outputs
                        context = {
                            "user_input": work.params.get("_user_input", {}),
                            "work_id": work_id
                        }
                        
                        # Add input node outputs to context (prompt_default_hidden, prompt_input, image_default, etc.)
                        for node in workflow.nodes:
                            node_type = node.get("type")
                            node_id = node.get("id")
                            node_data = node.get("data", {})
                            
                            if node_type == "prompt_default_hidden":
                                prompt_value = node_data.get("value", "")
                                context[node_id] = {
                                    "output": {
                                        "prompt": prompt_value
                                    }
                                }
                                logger.info(f"Added prompt_default_hidden node {node_id} to context with prompt: {prompt_value[:50] if prompt_value else 'empty'}")
                            elif node_type == "prompt_input":
                                prompt_value = node_data.get("value", "")
                                context[node_id] = {"output": {"prompt": prompt_value}}
                            elif node_type == "image_default":
                                image_value = node_data.get("value", "")
                                context[node_id] = {
                                    "output": {
                                        "image": image_value
                                    }
                                }
                            elif node_type == "video_default":
                                video_value = node_data.get("value", "")
                                context[node_id] = {"output": {"video": video_value}}
                            elif node_type == "media_list_default":
                                media_value = node_data.get("value", [])
                                if isinstance(media_value, str):
                                    try:
                                        import json
                                        media_value = json.loads(media_value) if media_value else []
                                    except (TypeError, ValueError):
                                        media_value = []
                                context[node_id] = {"output": {"array": media_value}}
                            elif node_type == "param_input":
                                # Add paramInput node output to context
                                param_name = node_data.get("param_name", "param")
                                param_value = node_data.get("value", "")
                                context[node_id] = {
                                    "output": {
                                        param_name: param_value
                                    }
                                }
                        
                        # Get execution order to map node IDs to indices (node_0, node_1, etc.)
                        execution_order = executor._topological_sort(valid_nodes, workflow.edges)
                        node_id_to_index = {node_id: f"node_{i}" for i, node_id in enumerate(execution_order)}
                        
                        # Refresh work object to ensure we have the latest workflow nodes data
                        db.refresh(work)
                        
                        # Get workflow nodes from work.params (after refresh)
                        workflow_nodes = work.params.get("_workflow_nodes", {}) if work.params else {}
                        logger.info(f"Workflow nodes from DB for node {next_node_id}: {list(workflow_nodes.keys())}")
                        
                        # Add all completed node outputs to context
                        # Use both actual node ID and indexed format (node_0, node_1) for compatibility
                        for completed_node_id, node_data in workflow_nodes.items():
                            context[completed_node_id] = node_data
                            # Also add with indexed format if available
                            if completed_node_id in node_id_to_index:
                                indexed_key = node_id_to_index[completed_node_id]
                                context[indexed_key] = node_data
                        
                        # Debug: log context keys
                        logger.info(f"Context keys for node {next_node_id}: {list(context.keys())}")
                        logger.info(f"Context node data: {[(k, type(v).__name__) for k, v in context.items() if k.startswith('node_')]}")
                        
                        # Set executor context and workflow before executing node
                        executor.context = context
                        executor.workflow = workflow
                        
                        # Execute next node
                        node_result = await executor._execute_node(
                            next_node,
                            work_id,
                            webhook_url,
                            is_final=is_final
                        )
                        logger.info(f"Triggered next node {next_node_id} for work {work_id}")
                        
                        # Store prediction_id for this node so we can poll its status later
                        prediction_id = node_result.get("prediction_id")
                        if prediction_id:
                            # Refresh work to get latest params
                            db.refresh(work)
                            if not work.params:
                                work.params = {}
                            if "_workflow_nodes" not in work.params:
                                work.params["_workflow_nodes"] = {}
                            
                            # Initialize node entry if not exists
                            if next_node_id not in work.params["_workflow_nodes"]:
                                work.params["_workflow_nodes"][next_node_id] = {}
                            
                            # Store prediction_id for polling
                            work.params["_workflow_nodes"][next_node_id]["prediction_id"] = prediction_id
                            work.params["_workflow_nodes"][next_node_id]["status"] = "processing"
                            
                            # Mark params as modified
                            from sqlalchemy.orm.attributes import flag_modified
                            flag_modified(work, "params")
                            db.commit()
                            logger.info(f"Stored prediction_id {prediction_id} for node {next_node_id} in work {work_id}")
                    except Exception as e:
                        logger.error(f"Failed to execute next node {next_node_id} for work {work_id}: {str(e)}")
                        from ..services.work_failed_service import mark_work_failed, notify_generation_failed
                        mark_work_failed(db, work, f"Failed to execute next node {next_node_id}: {str(e)}")
                        db.commit()
                        notify_generation_failed(db, work.user_id)
                        ws_manager = get_connection_manager()
                        await ws_manager.send_message(work.user_id, {
                            "type": "generation_complete",
                            "work_id": work_id,
                            "status": "failed",
                            "error_message": work.error_message,
                        })
                        return error_response(message=f"Failed to trigger next node: {str(e)}")
                
                return success_response(message=f"Intermediate node completed, triggered {len(ready_nodes)} next node(s)")
        
        elif result.get("status") == "failed":
            error_msg = result.get("error", "Node generation failed")
            from ..services.work_failed_service import mark_work_failed, notify_generation_failed
            mark_work_failed(db, work, f"Workflow node {node_id} failed: {error_msg}")
            db.commit()
            notify_generation_failed(db, work.user_id)
            ws_manager = get_connection_manager()
            await ws_manager.send_message(work.user_id, {
                "type": "generation_complete",
                "work_id": work_id,
                "status": "failed",
                "error_message": work.error_message,
            })
            return success_response(message="Workflow node failure handled")
        
        return success_response(message="Node processing")
        
    except Exception as e:
        logger.error(f"Error handling workflow node webhook: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return error_response(message="Internal error in workflow node webhook")


def _websocket_token(websocket: WebSocket) -> str | None:
    """Extract a bearer token from the WebSocket subprotocol header.

    Browsers cannot set an Authorization header for WebSocket handshakes. The
    client therefore offers ``bearer, <JWT>`` as subprotocols; the server only
    selects ``bearer`` and never places the credential in the URL.
    """
    protocols = [
        item.strip()
        for item in websocket.headers.get("sec-websocket-protocol", "").split(",")
        if item.strip()
    ]
    if len(protocols) != 2 or protocols[0].lower() != "bearer":
        return None
    return protocols[1]


def _websocket_origin_allowed(websocket: WebSocket) -> bool:
    origin = websocket.headers.get("origin")
    if not origin:
        return True
    configured = os.getenv("WEBSOCKET_ALLOWED_ORIGINS", "").strip()
    allowed = {
        item.strip().rstrip("/")
        for item in configured.split(",")
        if item.strip()
    }
    if not allowed:
        allowed = {
            os.getenv("FRONTEND_URL", "http://localhost:3000").rstrip("/"),
            os.getenv("ADMIN_FRONTEND_URL", "http://localhost:3001").rstrip("/"),
        }
    return origin.rstrip("/") in allowed


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    token = _websocket_token(websocket)
    payload = decode_access_token(token) if token else None
    sub = payload.get("sub") if payload else None
    try:
        user_id = int(sub)
    except (TypeError, ValueError):
        await websocket.close(code=1008, reason="Authentication required")
        return

    if not _websocket_origin_allowed(websocket):
        await websocket.close(code=1008, reason="Origin not allowed")
        return

    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if (
            user is None
            or not user.is_active
            or user.source == UserSource.ADMIN_CREATED
        ):
            await websocket.close(code=1008, reason="Authentication required")
            return
    finally:
        db.close()

    ws_manager = get_connection_manager()
    connected = False
    try:
        connected = await ws_manager.connect(user_id, websocket, subprotocol="bearer")
        if not connected:
            return
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        pass
    except Exception as exc:
        logger.warning("WebSocket error for user %s: %s", user_id, exc)
    finally:
        if connected:
            ws_manager.disconnect(user_id, websocket)


def _stripe_obj_to_dict(obj):
    """
    Normalize a Stripe SDK object into a nested plain dict.

    stripe>=8 returns StripeObject instances (e.g. Session) that do NOT support
    dict.get(); calling .get() on them raises AttributeError('get'). This helper
    converts them (and their nested fields like metadata) into plain dicts so the
    rest of the code can safely use .get(). Passes through None and real dicts.
    """
    if obj is None:
        return None
    if isinstance(obj, dict):
        return obj
    # StripeObject (stripe>=8) exposes to_dict(), which also converts nested
    # fields like metadata into plain dicts. NOTE: do NOT use dict(obj) as a
    # fallback — on stripe 15.x it raises KeyError while iterating.
    to_dict = getattr(obj, "to_dict", None)
    if callable(to_dict):
        return to_dict()
    return obj


def _complete_stripe_checkout_session(
    db: Session,
    session: dict,
    background_tasks: BackgroundTasks,
) -> PaymentOrder | None:
    """
    Mark the local order for a paid Stripe Checkout Session as completed.
    Returns None when the session cannot be mapped to a local order.
    """
    if session.get("payment_status") != "paid":
        logger.info(
            f"Stripe session {session.get('id')} ignored because payment_status={session.get('payment_status')}"
        )
        return None

    metadata = session.get("metadata") or {}
    order_id = session.get("client_reference_id") or metadata.get("order_id")
    payment_intent_id = session.get("payment_intent")
    session_id = session.get("id")

    query = db.query(PaymentOrder)
    payment_order = None
    if order_id:
        try:
            payment_order = query.filter(PaymentOrder.id == int(order_id)).first()
        except (TypeError, ValueError):
            logger.warning(f"Invalid Stripe order id on session {session_id}: {order_id}")

    if not payment_order and session_id:
        payment_order = query.filter(PaymentOrder.stripe_session_id == session_id).first()

    if not payment_order:
        logger.error(
            f"Stripe paid session {session_id} could not be mapped to a local order; "
            f"client_reference_id={order_id}, payment_intent={payment_intent_id}"
        )
        return None

    if payment_order.payment_provider != "stripe":
        logger.error(
            f"Stripe session {session_id} mapped to non-stripe order {payment_order.id} "
            f"provider={payment_order.payment_provider}"
        )
        return None

    if session_id:
        payment_order.stripe_session_id = session_id
    if payment_intent_id:
        payment_order.stripe_payment_intent_id = payment_intent_id
    db.flush()

    if payment_order.status == PaymentStatus.COMPLETED:
        logger.info(f"Stripe order {payment_order.id} already completed")
        return payment_order

    from .payment import _complete_payment_order_and_notify

    user = db.query(User).filter(User.id == payment_order.user_id).first()
    if not user:
        logger.error(f"User not found for Stripe order {payment_order.id}")
        return None

    _complete_payment_order_and_notify(
        db,
        payment_order,
        user,
        background_tasks,
    )
    logger.info(f"Stripe payment completed for order {payment_order.id}")
    return payment_order


@router.post("/stripe")
async def stripe_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Stripe payment success callback.
    """
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")
    
    if not sig_header:
        return error_response(message="Missing stripe-signature", status_code=status.HTTP_400_BAD_REQUEST)
        
    try:
        stripe_service = get_stripe_service()
        event = stripe_service.construct_event(payload, sig_header)
        
        # Handle Checkout completion events. async_payment_succeeded covers delayed
        # methods if they are enabled in Stripe.
        if event["type"] in ("checkout.session.completed", "checkout.session.async_payment_succeeded"):
            # stripe SDK (v15+) returns StripeObject, not a plain dict; it has no
            # .get(). Convert to a nested plain dict so downstream .get() calls work.
            session = _stripe_obj_to_dict(event["data"]["object"])
            _complete_stripe_checkout_session(db, session, background_tasks)

        # Fallback: some dashboards/operators naturally subscribe to PaymentIntent
        # events. Resolve the owning Checkout Session, then process the same path.
        elif event["type"] == "payment_intent.succeeded":
            payment_intent = _stripe_obj_to_dict(event["data"]["object"])
            payment_intent_id = payment_intent.get("id")
            if payment_intent_id:
                stripe_service = get_stripe_service()
                session = _stripe_obj_to_dict(
                    stripe_service.retrieve_checkout_session_for_payment_intent(payment_intent_id)
                )
                if session:
                    _complete_stripe_checkout_session(db, session, background_tasks)
                else:
                    logger.warning(f"No Checkout Session found for payment intent {payment_intent_id}")
                    
        return success_response(message="Webhook processed")
        
    except Exception as e:
        logger.error(f"Stripe webhook error: {str(e)}")
        return error_response(message=str(e), status_code=status.HTTP_400_BAD_REQUEST)
