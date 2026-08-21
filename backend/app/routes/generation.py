from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, Body
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from datetime import datetime, timedelta, timezone
from typing import Optional
import json
import os
import asyncio
import httpx
import uuid
from dotenv import load_dotenv

from ..models.base import get_db, SessionLocal
from ..models.user import User
from ..models.work import Work, WorkType, WorkStatus, ShareStatus
from ..services.credit_service import consume_credits as credit_service_consume
from ..services.credit_service import InsufficientCreditsError
from ..models.generation_model import GenerationModel, APILibrary
from ..models.workflow import Workflow
from ..models.schemas import GenerateRequest
from ..models.generation_config import (
    get_available_models,
    get_model_cost,
    validate_params,
    MODELS
)
from ..utils.auth import get_current_active_user, get_current_user_optional
from ..utils.responses import success_response, error_response
from ..utils.logger import logger, log_generation_start
from ..tasks.workflow_tasks import execute_workflow_task
from ..services.providers.factory import ProviderFactory

load_dotenv()

router = APIRouter()

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
REPLICATE_API_KEY = os.getenv("REPLICATE_API_KEY", "")


async def simulate_webhook_call(work_id: int):
    """
    Simulate a Replicate webhook callback for development mode.
    """
    await asyncio.sleep(5)  # Simulate 5 seconds generation time
    
    async with httpx.AsyncClient() as client:
        # Mock payload
        payload = {
            "status": "succeeded",
            "output": "https://picsum.photos/1024/1024",  # A nice random image
            "id": f"mock_{work_id}"
        }
        
        try:
            # Call our own webhook endpoint
            response = await client.post(
                f"{BACKEND_URL}/api/webhook/replicate/{work_id}",
                json=payload
            )
            logger.info(f"Simulated webhook for work {work_id}: {response.status_code}")
        except Exception as e:
            logger.error(f"Failed to simulate webhook: {str(e)}")


@router.post("/prompt-assistant")
async def prompt_assistant(
    request: dict = Body(...),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    AI Prompt Assistant endpoint using Gemini.
    Requires user authentication.
    """
    try:
        from ..services.gemini_service import get_gemini_service
        
        prompt = request.get("prompt", "")
        action = request.get("action", "optimize")
        model_type = request.get("model_type", "text-to-image")
        
        # "generate" action doesn't require prompt input
        if action != "generate" and not prompt:
            return error_response(
                message="Prompt content is required",
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        gemini_service = get_gemini_service(db_session=db)
        result = gemini_service.assist_prompt(
            prompt_content=prompt or "",  # Empty string for "generate" action
            action=action,
            model_type=model_type
        )
        
        return success_response(
            data=result,
            message="AI assistance provided successfully"
        )
        
    except ValueError as e:
        return error_response(
            message=f"Gemini API error: {str(e)}",
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE
        )
    except Exception as e:
        logger.error(f"Error in prompt assistant: {str(e)}")
        return error_response(
            message=f"AI Assistant failed: {str(e)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.get("/models")
async def get_models(
    work_type: str = None,
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """
    Get available models, optionally filtered by type and user visibility.
    """
    try:
        if work_type:
            if work_type not in MODELS:
                return error_response(
                    message=f"Invalid work type: {work_type}",
                    status_code=status.HTTP_400_BAD_REQUEST
                )
            models = get_available_models(work_type)
        else:
            models = MODELS
        
        # 1. Determine user permissions
        is_logged_in = current_user is not None
        is_paid_user = False
        
        if is_logged_in:
            from ..models.payment_order import PaymentOrder, PaymentStatus
            # Check if user has any completed payment orders
            paid_order = db.query(PaymentOrder).filter(
                PaymentOrder.user_id == current_user.id,
                PaymentOrder.status == PaymentStatus.COMPLETED
            ).first()
            is_paid_user = paid_order is not None

        # 2. Format models for response with visibility filtering
        formatted_models = {}
        for wtype, model_list in models.items():
            formatted_models[wtype] = []
            for model_name, config in model_list.items():
                # Visibility filtering logic
                level = config.get("model_level", "public") or "public"
                
                is_visible = False
                if level == "public":
                    is_visible = True
                elif level == "member":
                    is_visible = is_logged_in
                elif level == "premium":
                    is_visible = is_paid_user
                else:
                    is_visible = True # Default to public for unknown levels
                
                if not is_visible:
                    continue

                formatted_models[wtype].append({
                    "name": model_name,
                    "display_name": config["name"],
                    "description": config["description"],
                    "cost": config["cost"],
                    "sort_order": config.get("sort_order", 0),
                    "params": config.get("params", {}),
                    "example_galleries": config.get("example_galleries", []),
                    "category": config.get("category"),
                    "model_level": config.get("model_level"),
                    "is_featured": config.get("is_featured", False),
                    "icon_url": config.get("icon_url"),
                    "badge": config.get("badge"),
                })
        
        return success_response(
            data=formatted_models,
            message="Models retrieved successfully"
        )
        
    except Exception as e:
        logger.error(f"Error getting models: {str(e)}")
        return error_response(
            message="An error occurred while retrieving models",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


def _get_moderation_text_params(
    db: Session,
    model_name: str,
    work_type: str,
    params: dict,
) -> tuple[str, str]:
    """
    「」；。
    ；。
     (prompt_for_check, negative_prompt_for_check)。
    """
    prompt_val = (params or {}).get("prompt", "") or ""
    negative_val = (params or {}).get("negative_prompt", "") or ""
    generation_model = db.query(GenerationModel).filter(
        GenerationModel.model_key == model_name,
        GenerationModel.is_active == True,
    ).first()
    if not generation_model or not generation_model.workflow_id:
        return "", ""
    workflow = db.query(Workflow).filter(Workflow.id == generation_model.workflow_id).first()
    if not workflow:
        return "", ""
    visible_names = set(workflow.get_user_visible_params().keys())
    prompt_for_check = prompt_val if "prompt" in visible_names else ""
    negative_for_check = negative_val if "negative_prompt" in visible_names else ""
    return prompt_for_check, negative_for_check


@router.post("/check-moderation")
async def check_moderation_before_generate(
    request: GenerateRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Pre-generation content moderation check endpoint.
    Checks prompt and parameters for sensitive or policy-violating content.
    """
    try:
        from ..services.moderation import get_moderation_service
        from ..models.moderation import LexiconSeverity
        
        #  prompt/negative_prompt
        prompt, negative_prompt = _get_moderation_text_params(
            db, request.model_name, request.type, request.params or {}
        )
        
        moderation_service = get_moderation_service(db)
        result = moderation_service.check_nsfw(prompt, negative_prompt)
        
        max_severity = "LOW"
        if result.get("flagged_keywords"):
            severities = [kw.get("severity", "LOW") for kw in result["flagged_keywords"]]
            if LexiconSeverity.HIGH.value in severities:
                max_severity = "HIGH"
            elif LexiconSeverity.MEDIUM.value in severities:
                max_severity = "MEDIUM"
            else:
                max_severity = "LOW"
        
        # HIGH，MEDIUMLOW（MEDIUM）
        can_proceed = max_severity != "HIGH"
        
        # ： JSON，
        flagged_keywords = result.get("flagged_keywords") or []
        if flagged_keywords:
            outcome = (
                "blocked"
                if max_severity == "HIGH"
                else ("passed_after_warning" if max_severity == "MEDIUM" else "passed")
            )
            ts = datetime.now(timezone.utc).isoformat()
            for kw in flagged_keywords:
                log_entry = {
                    "ts": ts,
                    "event": "lexicon_hit",
                    "user_id": current_user.id,
                    "lexicon_id": kw.get("lexicon_id"),
                    "word": kw.get("word"),
                    "severity": kw.get("severity", "LOW"),
                    "category": kw.get("category", "OTHER"),
                    "source": "check_moderation",
                    "outcome": outcome,
                }
                logger.info(json.dumps(log_entry, ensure_ascii=False))
        
        return success_response(
            data={
                "has_violation": result.get("is_violation", False),
                "max_severity": max_severity,
                "flagged_keywords": result.get("flagged_keywords", []),
                "nsfw_tags": result.get("nsfw_tags", []),
                "can_proceed": can_proceed,
            },
            message="Moderation check completed"
        )
        
    except Exception as e:
        logger.error(f"Error in moderation check: {str(e)}", exc_info=True)
        # ，（）
        return success_response(
            data={
                "has_violation": False,
                "max_severity": "LOW",
                "flagged_keywords": [],
                "nsfw_tags": [],
                "can_proceed": True,
                "error": "Moderation check failed, proceeding with caution"
            },
            message="Moderation check completed with warnings"
        )


@router.post("")
async def create_generation(
    request: GenerateRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Create a new generation job.
    
    Flow:
    1. Validate user has sufficient credits
    2. Create Work record
    3. Deduct credits
    4. Call Replicate API with webhook (or simulate in dev)
    5. Return work_id
    """
    try:
        from ..models.workflow import Workflow  # ， UnboundLocalError
        # Validate model exists (get base cost for initial check)
        try:
            base_cost = get_model_cost(request.type, request.model_name)
        except ValueError as e:
            return error_response(
                message=str(e),
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        # Extract parent_id BEFORE validation (since it's not a model param)
        parent_id = request.params.pop("parent_id", None) if request.params else None
        
        # Validate and sanitize parameters
        is_valid, result = validate_params(
            request.type,
            request.model_name,
            request.params
        )
        
        if not is_valid:
            return error_response(
                message="Invalid parameters",
                errors=result,
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        sanitized_params = result.copy()
        
        # Calculate final cost with parameter-based additions
        try:
            model_cost = get_model_cost(request.type, request.model_name, sanitized_params)
        except ValueError as e:
            return error_response(
                message=str(e),
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        # Extract core fields for database columns
        prompt_value = sanitized_params.pop("prompt", "")
        negative_prompt_value = sanitized_params.pop("negative_prompt", "")
        
        # Check if user has sufficient credits
        if current_user.total_credits < model_cost:
            return error_response(
                message=f"Insufficient credits. Required: {model_cost}, Available: {current_user.total_credits}",
                status_code=status.HTTP_402_PAYMENT_REQUIRED
            )
        
        # Get GenerationModel to retrieve model_key and name
        # request.model_name is actually the model_key
        generation_model = db.query(GenerationModel).filter(
            GenerationModel.model_key == request.model_name,
            GenerationModel.work_type == request.type,
            GenerationModel.is_active == True
        ).first()
        
        if not generation_model:
            return error_response(
                message=f"Model '{request.model_name}' not found for type '{request.type}'",
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        # Convert work_type string to WorkType enum safely
        # Map string values to enum values (not enum names)
        # ，
        work_type_map = {
            "text2img": WorkType.TEXT2IMG,
            "text-to-image": WorkType.TEXT2IMG,
            "text2video": WorkType.TEXT2VIDEO,
            "text-to-video": WorkType.TEXT2VIDEO,
            "img2img": WorkType.IMG2IMG,
            "image-to-image": WorkType.IMG2IMG,
            "img2video": WorkType.IMG2VIDEO,
            "image-to-video": WorkType.IMG2VIDEO,
            "img_effects": WorkType.IMG_EFFECTS,
            "image-effects": WorkType.IMG_EFFECTS,
            "video_effects": WorkType.VIDEO_EFFECTS,
            "video-effects": WorkType.VIDEO_EFFECTS,
        }
        work_type_enum = work_type_map.get(request.type.lower())
        if not work_type_enum:
            return error_response(
                message=f"Invalid work type: {request.type}",
                status_code=status.HTTP_400_BAD_REQUEST
            )

        # For workflows: set work.type from last node's API output_type so it matches actual output
        if generation_model.workflow_id:
            from ..services.workflow_executor import get_workflow_output_work_type
            workflow = db.query(Workflow).filter(Workflow.id == generation_model.workflow_id).first()
            if workflow:
                effective_work_type = get_workflow_output_work_type(db, workflow)
                if effective_work_type:
                    override_enum = work_type_map.get(effective_work_type.lower())
                    if override_enum:
                        work_type_enum = override_enum
                        logger.info(
                            f"Work type set from workflow last node output: {effective_work_type} for workflow {workflow.id}"
                        )
        
        # Create Work record
        new_work = Work(
            user_id=current_user.id,
            parent_id=parent_id,
            type=work_type_enum.value,
            prompt=prompt_value,
            negative_prompt=negative_prompt_value,
            prompt_id=str(uuid.uuid4()), # Always generate a fresh prompt_id for new works
            model_key=generation_model.model_key,
            model_name=generation_model.name,
            params=sanitized_params,
            status=WorkStatus.GENERATING,
            is_shared=False,  # Default to private
            share_status=None,  # Default to None (private)
        )
        
        db.add(new_work)
        db.flush()  # Get work ID
        
        # Deduct credits (with row lock to prevent over-deduction)
        try:
            remaining_credits = credit_service_consume(
                db,
                current_user.id,
                model_cost,
                f"Generation: {request.type} with {generation_model.name}",
                work_id=new_work.id,
            )
        except InsufficientCreditsError:
            db.rollback()
            return error_response(
                message=f"Insufficient credits. Required: {model_cost}, Available: {current_user.total_credits}",
                status_code=status.HTTP_402_PAYMENT_REQUIRED
            )
        
        db.commit()
        db.refresh(new_work)
        
        # 🔍 NSFW Auto Moderation: 「」；
        from ..services.moderation import get_moderation_service
        from ..models.moderation import ModerationLog, ModerationType, ModerationAction, NSFWStatus, LexiconSeverity
        
        prompt_for_check, negative_for_check = _get_moderation_text_params(
            db, request.model_name, request.type,
            {"prompt": prompt_value, "negative_prompt": negative_prompt_value},
        )
        moderation_service = get_moderation_service(db)
        nsfw_result = moderation_service.check_nsfw(
            prompt=prompt_for_check,
            negative_prompt=negative_for_check,
            work_id=new_work.id
        )
        
        max_severity = "LOW"
        if nsfw_result.get("flagged_keywords"):
            severities = [kw.get("severity", "LOW") for kw in nsfw_result["flagged_keywords"]]
            if LexiconSeverity.HIGH.value in severities:
                max_severity = "HIGH"
            elif LexiconSeverity.MEDIUM.value in severities:
                max_severity = "MEDIUM"
        
        # ：， Provider API
        if max_severity == "HIGH":
            new_work.nsfw_status = NSFWStatus.BLOCKED.value
            new_work.is_shared = False
            new_work.share_status = None
            
            log = ModerationLog(
                work_id=new_work.id,
                moderation_type=ModerationType.NSFW,
                action_type=ModerationAction.AUTO_BLOCKED,
                nsfw_tags=nsfw_result.get('nsfw_tags', []),
                flagged_keywords=nsfw_result.get('flagged_keywords', []),
                reason="Auto-blocked: high-severity content detected before generation"
            )
            db.add(log)
            
            from ..services.work_failed_service import mark_work_failed, notify_generation_failed
            mark_work_failed(db, new_work, "Content blocked by safety policy before generation")
            db.commit()
            notify_generation_failed(db, new_work.user_id)
            # WebSocket: notify user of failure
            from ..services.websocket import get_connection_manager
            ws_manager = get_connection_manager()
            await ws_manager.send_message(current_user.id, {
                "type": "generation_complete",
                "work_id": new_work.id,
                "status": "failed",
                "error_message": new_work.error_message,
            })
            
            high_severity_words = [
                kw.get('word') for kw in nsfw_result.get('flagged_keywords', [])
                if kw.get('severity') == LexiconSeverity.HIGH.value
            ]
            
            return error_response(
                message=f"Content blocked: flagged terms detected ({', '.join(high_severity_words[:5])}). Please adjust your prompt.",
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        # /： PENDING，
        initial_nsfw_status = NSFWStatus.APPROVED.value
        if nsfw_result.get('is_violation', False):
            initial_nsfw_status = NSFWStatus.PENDING.value
            log = ModerationLog(
                work_id=new_work.id,
                moderation_type=ModerationType.NSFW,
                action_type=ModerationAction.AUTO_FLAGGED,
                nsfw_tags=nsfw_result.get('nsfw_tags', []),
                flagged_keywords=nsfw_result.get('flagged_keywords', []),
                reason="Auto-flagged: potential NSFW content detected before generation"
            )
            db.add(log)
        else:
            # ：
            log = ModerationLog(
                work_id=new_work.id,
                moderation_type=ModerationType.NSFW,
                action_type=ModerationAction.AUTO_APPROVED,
                reason="Auto-approved: no violations detected before generation"
            )
            db.add(log)
        
        #  nsfw_status
        new_work.nsfw_status = initial_nsfw_status
        db.commit()
        db.refresh(new_work)
        
        # log_generation_start moved after actual API call success
        
        # Only workflow mode is supported
        if not generation_model.workflow_id:
            return error_response(
                message="Model must use a workflow. This model has no workflow configured.",
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        # Prepare user input for workflow
        user_input = {
            "prompt": prompt_value,
            "negative_prompt": negative_prompt_value,
            **sanitized_params
        }
        
        # Store user_input in work.params for webhook processing
        if not new_work.params:
            new_work.params = {}
        new_work.params["_user_input"] = user_input
        new_work.params["_workflow_nodes"] = {}  # Initialize workflow nodes storage
        db.commit()
        db.refresh(new_work)
        
        #  Celery （）
        try:
            task = execute_workflow_task.delay(
                work_id=new_work.id,
                user_id=current_user.id
            )
            
            #  Celery  ID（，）
            new_work.params["_celery_task_id"] = task.id
            from sqlalchemy.orm.attributes import flag_modified
            flag_modified(new_work, "params")
            db.commit()
            
            logger.info(f"Workflow task queued for work {new_work.id}, celery_task_id={task.id}")
            log_generation_start(current_user.id, request.type, request.model_name)
            
            return success_response(
                data={
                    "work_id": new_work.id,
                    "celery_task_id": task.id,  #  Celery  ID
                    "status": new_work.status.value,
                    "credits_used": model_cost,
                    "remaining_credits": remaining_credits,
                    "workflow_id": generation_model.workflow_id,
                },
                message="Generation task queued successfully",
                status_code=status.HTTP_201_CREATED
            )
            
        except Exception as e:
            from ..services.mock_generation_service import is_mock_generation_enabled, process_mock_generation
            if is_mock_generation_enabled():
                logger.info(f"[MOCK Fallback] Celery queue unavailable. Executing mock generation in BackgroundTasks for work {new_work.id}")
                background_tasks.add_task(process_mock_generation, db, new_work.id)
                return success_response(
                    data={
                        "work_id": new_work.id,
                        "status": new_work.status.value,
                        "credits_used": model_cost,
                        "remaining_credits": remaining_credits,
                        "is_mock": True
                    },
                    message="Mock generation initiated successfully (Mock Mode)",
                    status_code=status.HTTP_201_CREATED
                )

            #  Celery （， Redis ）
            import traceback
            logger.error(
                f"Failed to queue task for work {new_work.id}: {str(e)}\n{traceback.format_exc()}"
            )
            
            try:
                from ..services.work_failed_service import mark_work_failed, notify_generation_failed
                mark_work_failed(db, new_work, f"Failed to queue generation task: {type(e).__name__}")
                db.commit()
                notify_generation_failed(db, new_work.user_id)
            except Exception as refund_error:
                logger.error(f"Failed to refund credits for work {new_work.id}: {refund_error}")
                db.rollback()
            
            return error_response(
                message="Failed to queue generation task. Please try again later.",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
    except Exception as e:
        # This catches any exception before the provider API call
        db.rollback()
        import traceback
        logger.error(
            f"Error creating generation: {str(e)}\nTraceback: {traceback.format_exc()}",
            exc_info=True
        )
        return error_response(
            message="An error occurred while creating generation. Please check the logs for details.",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.get("/{work_id}")
async def get_generation_status(
    work_id: int,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get the status of a generation job.
    """
    try:
        # Get work
        work = db.query(Work).filter(Work.id == work_id).first()
        
        if not work:
            return error_response(
                message="Work not found",
                status_code=status.HTTP_404_NOT_FOUND
            )
        
        # ownership check
        if work.user_id != current_user.id:
            return error_response(
                message="Not authorized to view this work",
                status_code=status.HTTP_403_FORBIDDEN
            )
        
        # Timeout check: if work has been GENERATING for too long (e.g., 10 minutes), mark as failed and refund
        if work.status == WorkStatus.GENERATING and work.created_at:
            timeout_threshold_minutes = 10
            timeout_threshold = timedelta(minutes=timeout_threshold_minutes)
            elapsed = datetime.now(timezone.utc) - work.created_at
            if elapsed > timeout_threshold:
                from ..services.work_failed_service import mark_work_failed, notify_generation_failed
                mark_work_failed(
                    db,
                    work,
                    f"Generation timeout: exceeded {timeout_threshold_minutes} minutes",
                )
                db.commit()
                notify_generation_failed(db, work.user_id)
                from ..services.websocket import get_connection_manager
                ws_manager = get_connection_manager()
                await ws_manager.send_message(work.user_id, {
                    "type": "generation_complete",
                    "work_id": work_id,
                    "status": "failed",
                    "error_message": work.error_message,
                })
                return success_response(
                    data=work.to_dict(include_prompt=True),
                    message="Work status retrieved successfully"
                )
        
        # If still generating, check with provider directly (fallback for local dev/missing webhooks)
        # This handles cases where webhook might not have been triggered
        if work.status == WorkStatus.GENERATING and work.replicate_id:
            try:
                # Check if this is a workflow model
                from ..models.generation_model import GenerationModel
                generation_model = db.query(GenerationModel).filter(
                    GenerationModel.model_key == work.model_key
                ).first()
                
                # Handle workflow models differently
                if generation_model and generation_model.workflow_id:
                    # For workflow models, check all node statuses
                    workflow_nodes = work.params.get("_workflow_nodes", {}) if work.params else {}
                    
                    # Get the workflow to find nodes
                    workflow = db.query(Workflow).filter(Workflow.id == generation_model.workflow_id).first()
                    if workflow:
                        # Filter valid nodes (must match executor and webhook so execution_order is correct)
                        valid_node_types = {'api_call', 'prompt_input', 'image_default', 'video_default', 'param_input', 'prompt_default_hidden', 'media_list_default'}
                        valid_nodes = [
                            node for node in workflow.nodes 
                            if node.get("type") in valid_node_types
                        ]
                        
                        from ..services.workflow_executor import WorkflowExecutor
                        executor = WorkflowExecutor(db_session=db)
                        execution_order = executor._topological_sort(valid_nodes, workflow.edges)
                        
                        if execution_order:
                            # 1.  api_call  ID，（R2）
                            last_api_call_node_id = None
                            for nid in reversed(execution_order):
                                node = executor._get_node_by_id(valid_nodes, nid)
                                if node and node.get("type") == "api_call":
                                    last_api_call_node_id = nid
                                    break

                            # 2. （， 3+ ）
                            class MockBackgroundTasks:
                                def add_task(self, *args, **kwargs): pass

                            for poll_node_id, node_data in workflow_nodes.items():
                                prediction_id = node_data.get("prediction_id")
                                is_success = node_data.get("status") == "success"
                                is_failed = node_data.get("status") == "failed"

                                #  ID
                                if prediction_id and not is_success and not is_failed:
                                    poll_node = executor._get_node_by_id(valid_nodes, poll_node_id)
                                    #  api_id（）， api_id （）
                                    if poll_node and not poll_node.get("api_id"):
                                        for nid in execution_order:
                                            cand = executor._get_node_by_id(valid_nodes, nid)
                                            if cand and cand.get("api_id"):
                                                poll_node = cand
                                                break
                                    
                                    if poll_node and poll_node.get("api_id"):
                                        api_id = poll_node.get("api_id")
                                        from ..models.generation_model import APILibrary
                                        api = db.query(APILibrary).filter(APILibrary.id == api_id).first()
                                        
                                        if api:
                                            provider = ProviderFactory.get_provider(api.provider)
                                            result = await provider.get_status(prediction_id)
                                            
                                            if result.get("status") == "success":
                                                logger.info(f"Workflow node {poll_node_id} completed via polling for work {work_id}")
                                                from ..routes.webhook import _handle_workflow_node_webhook
                                                #  get_status  result ， sync （ Gemini） handle_webhook  text
                                                is_final = poll_node_id == last_api_call_node_id
                                                current_bg_tasks = background_tasks if is_final else MockBackgroundTasks()
                                                try:
                                                    await _handle_workflow_node_webhook(
                                                        work_id,
                                                        poll_node_id,
                                                        {},
                                                        work,
                                                        generation_model,
                                                        db,
                                                        current_bg_tasks,
                                                        result_override=result,
                                                    )
                                                    db.refresh(work)
                                                except Exception as e:
                                                    logger.error(f"Error triggering webhook for node {poll_node_id}: {str(e)}")
                                            
                                            elif result.get("status") == "failed":
                                                from ..services.work_failed_service import mark_work_failed, notify_generation_failed
                                                mark_work_failed(
                                                    db,
                                                    work,
                                                    result.get("error", f"Node {poll_node_id} failed"),
                                                )
                                                db.commit()
                                                notify_generation_failed(db, work.user_id)
                                                from ..services.websocket import get_connection_manager
                                                ws_manager = get_connection_manager()
                                                await ws_manager.send_message(work.user_id, {
                                                    "type": "generation_complete",
                                                    "work_id": work_id,
                                                    "status": "failed",
                                                    "error_message": work.error_message,
                                                })
                                                break #

                            return success_response(
                                data=work.to_dict(include_prompt=True),
                                message="Work status retrieved successfully"
                            )
            except Exception as e:
                import traceback
                logger.error(
                    f"Error checking provider status for work {work_id}: {str(e)}\n"
                    f"Traceback: {traceback.format_exc()}"
                )
        
        return success_response(
            data=work.to_dict(include_prompt=True),
            message="Work status retrieved successfully"
        )
        
    except Exception as e:
        logger.error(f"Error getting generation status: {str(e)}")
        return error_response(
            message="An error occurred while retrieving status",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

