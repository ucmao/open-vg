from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import StreamingResponse
import httpx
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, func
from typing import Optional

from ..models.base import get_db
from ..models.user import User
from ..models.work import Work, WorkType, WorkStatus, ShareStatus
from ..models.favorite import Favorite
from ..models.like import Like
from ..models.moderation import Report, ReportStatus, ReportType
from ..utils.auth import get_current_active_user, get_current_user_optional
from pydantic import BaseModel, Field
from ..utils.responses import success_response, error_response, paginated_response
from ..utils.logger import logger
from ..utils.work_metadata import generate_work_title, generate_work_description
from ..models.schemas import SubmitShareRequest, UpdateWorkRequest
from ..services.storage import get_storage_service

router = APIRouter()


@router.get("")
def get_works(
    page: int = 1,
    page_size: int = 20,
    type: Optional[str] = None,
    media_type: Optional[str] = None,
    model: Optional[str] = Query(None, description="Filter by model name(s). Support comma-separated values for multiple models."),
    category: Optional[str] = None,
    keyword: Optional[str] = None,
    sort: Optional[str] = "newest",
    include_prompt: bool = Query(True, description="Include prompt in response (for remix functionality)"),
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """
    Get shared works with filters.
    Only returns approved works that are shared.
    Sort options: newest, popular, liked, viewed
    media_type: 'image' or 'video' - filters by media type (groups text2img/img2img as image, text2video/img2video as video)
    type: exact work type filter (for backward compatibility)
    """
    try:
        # Build query
        # Import NSFWStatus for filtering
        from ..models.moderation import NSFWStatus
        from sqlalchemy import or_
        
        query = db.query(Work).filter(
            and_(
                Work.is_shared == True,
                Work.share_status == ShareStatus.APPROVED,
                Work.status == WorkStatus.SUCCESS,
                Work.deleted_at == None,  # Exclude soft deleted works
                Work.hidden == False,  # Exclude hidden works
                # NSFW status check: only show approved or null (for backward compatibility)
                or_(
                    Work.nsfw_status == NSFWStatus.APPROVED.value,
                    Work.nsfw_status == None  # Old works without NSFW status
                )
            )
        )
        
        # Apply filters - media_type takes precedence over type
        if media_type:
            if media_type == 'image':
                query = query.filter(Work.type.in_(['text-to-image', 'image-to-image', 'text2img', 'img2img', 'image-effects', 'img_effects']))
            elif media_type == 'video':
                query = query.filter(Work.type.in_(['text-to-video', 'image-to-video', 'text2video', 'img2video', 'video-effects', 'video_effects']))
        elif type:
            # Backward compatibility: exact type match
            query = query.filter(Work.type == type)
        
        if model:
            if "," in model:
                model_list = [m.strip() for m in model.split(",") if m.strip()]
                if model_list:
                    query = query.filter(Work.model_name.in_(model_list))
            else:
                query = query.filter(Work.model_name == model)
        
        if category:
            # Support hierarchical category matching
            # Category can be:
            # 1. Level 1 only: "Love"
            # 2. Level 1|Level 2: "Love|Romantic Couple"
            # 3. Level 2 only: "Romantic Couple" (if it exists as standalone)
            from ..models.category_page import CategoryPage
            
            # Check if category is in "Level1|Level2" format
            if "|" in category:
                # Parse hierarchical category
                parts = category.split("|", 1)
                level1_name = parts[0].strip()
                level2_name = parts[1].strip() if len(parts) > 1 else None
                
                # Try to find the level 2 category in category_pages
                if level2_name:
                    level2_category = db.query(CategoryPage).filter(
                        CategoryPage.category_name == level2_name,
                        CategoryPage.level == 2,
                        CategoryPage.is_active == True
                    ).first()
                    
                    if level2_category:
                        # Found level 2 category, use exact match for "Level1|Level2" format
                        query = query.filter(Work.category == category)
                    else:
                        # Level 2 not found in category_pages, use exact match anyway (backward compatibility)
                        query = query.filter(Work.category == category)
                else:
                    # Invalid format, use exact match
                    query = query.filter(Work.category == category)
            else:
                # Single category name - check if it exists in category_pages
                category_page = db.query(CategoryPage).filter(
                    CategoryPage.category_name == category,
                    CategoryPage.is_active == True
                ).first()
                
                if category_page:
                    if category_page.level == 1:
                        # Level 1: match level 1 category and all its level 2 children
                        query = query.filter(
                            or_(
                                Work.category == category,  # Exact match for level 1
                                Work.category.like(f"{category}|%")  # All level 2 under this level 1
                            )
                        )
                    else:
                        # Level 2: match both standalone level 2 and hierarchical format
                        # Need to get parent category name to build full path
                        parent_category = None
                        if category_page.parent_id:
                            parent_page = db.query(CategoryPage).filter(
                                CategoryPage.id == category_page.parent_id
                            ).first()
                            if parent_page:
                                parent_category = parent_page.category_name
                        
                        if parent_category:
                            # Match both formats:
                            # 1. Standalone level 2: "Romantic Couple"
                            # 2. Hierarchical format: "Love|Romantic Couple"
                            query = query.filter(
                                or_(
                                    Work.category == category,  # Standalone level 2
                                    Work.category == f"{parent_category}|{category}"  # Hierarchical format
                                )
                            )
                        else:
                            # No parent found, use exact match only
                            query = query.filter(Work.category == category)
                else:
                    # Category not in category_pages, use exact match (backward compatibility)
                    query = query.filter(Work.category == category)
        
        if keyword:
            query = query.filter(Work.prompt.ilike(f"%{keyword}%"))
        
        # Get total count
        total = query.count()
        
        # Apply sorting
        if sort == "popular":
            # Popular = weighted combination of likes, favorites, and views
            order_by_clause = desc(Work.like_count + Work.favorite_count * 2 + Work.view_count * 0.001)
        elif sort == "liked":
            order_by_clause = desc(Work.like_count)
        elif sort == "viewed":
            order_by_clause = desc(Work.view_count)
        else:  # newest (default)
            order_by_clause = desc(Work.created_at)
        
        # Get paginated results
        works = query.order_by(order_by_clause).offset((page - 1) * page_size).limit(page_size).all()
        
        # Batch prefetch auxiliary data to avoid N+1 queries
        from ..models.work import batch_prefetch_work_data
        current_user_id = current_user.id if current_user else None
        prefetched = batch_prefetch_work_data(works, db, current_user_id)
        
        # Format results with author info and like status
        items = [
            work.to_dict(
                include_user=True, 
                include_prompt=include_prompt, 
                current_user_id=current_user_id, 
                db=db,
                prefetched_counts=prefetched['counts'],
                prefetched_likes=prefetched['liked_work_ids'],
                prefetched_follows=prefetched['following_user_ids']
            ) for work in works
        ]
        
        return paginated_response(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            message="Works retrieved successfully"
        )
        
    except Exception as e:
        logger.error(f"Error getting works: {str(e)}")
        return error_response(
            message="An error occurred while retrieving works",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.get("/hot")
def get_hot_works(
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Get featured works for the homepage.
    Now filters by is_featured=True instead of calculating engagement scores.
    """
    try:
        # Import NSFWStatus for filtering
        from ..models.moderation import NSFWStatus
        from sqlalchemy import or_
        
        # Get featured works
        works = db.query(Work).filter(
            and_(
                Work.is_featured == True,
                Work.is_shared == True,
                Work.share_status == ShareStatus.APPROVED,
                Work.status == WorkStatus.SUCCESS,
                Work.deleted_at == None,
                Work.hidden == False,  # Exclude hidden works
                # NSFW status check: only show approved or null (for backward compatibility)
                or_(
                    Work.nsfw_status == NSFWStatus.APPROVED.value,
                    Work.nsfw_status == None  # Old works without NSFW status
                )
            )
        ).order_by(
            desc(Work.updated_at)  # Show most recently updated featured works first
        ).limit(limit).all()
        
        # Batch prefetch auxiliary data to avoid N+1 queries
        from ..models.work import batch_prefetch_work_data
        prefetched = batch_prefetch_work_data(works, db, None)
        
        items = [
            work.to_dict(
                include_user=True, 
                include_prompt=True,
                prefetched_counts=prefetched['counts'],
                prefetched_likes=prefetched['liked_work_ids'],
                prefetched_follows=prefetched['following_user_ids']
            ) for work in works
        ]
        
        return success_response(
            data=items,
            message="Featured works retrieved successfully"
        )
        
    except Exception as e:
        logger.error(f"Error getting hot works: {str(e)}")
        return error_response(
            message="An error occurred while retrieving hot works",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.get("/featured/preview")
def get_featured_preview(
    media_type: Optional[str] = None,  # 'image' or 'video'
    limit: int = 15,
    db: Session = Depends(get_db)
):
    """
    Get random featured works for preview carousel.
    Filters by media_type: 'image' (text2img/img2img) or 'video' (text2video/img2video)
    Returns random featured works for carousel display.
    """
    try:
        from ..models.moderation import NSFWStatus
        
        # Build base query
        query = db.query(Work).filter(
            and_(
                Work.is_featured == True,
                Work.is_shared == True,
                Work.share_status == ShareStatus.APPROVED,
                Work.status == WorkStatus.SUCCESS,
                Work.deleted_at == None,
                Work.hidden == False,
                Work.file_url.isnot(None),  # Must have file_url
                or_(
                    Work.nsfw_status == NSFWStatus.APPROVED.value,
                    Work.nsfw_status == None  # Old works without NSFW status
                )
            )
        )
        
        # Filter by media type
        if media_type == 'image':
            query = query.filter(Work.type.in_([WorkType.TEXT2IMG, WorkType.IMG2IMG]))
        elif media_type == 'video':
            query = query.filter(Work.type.in_([WorkType.TEXT2VIDEO, WorkType.IMG2VIDEO]))
        
        # Random order and limit
        works = query.order_by(func.random()).limit(limit).all()
        
        # Batch prefetch auxiliary data to avoid N+1 queries
        from ..models.work import batch_prefetch_work_data
        prefetched = batch_prefetch_work_data(works, db, None)
        
        # include_prompt=True so prompt
        items = [
            work.to_dict(
                include_user=False, 
                include_prompt=True,
                prefetched_counts=prefetched['counts'],
                prefetched_likes=prefetched['liked_work_ids'],
                prefetched_follows=prefetched['following_user_ids']
            ) for work in works
        ]
        
        return success_response(
            data=items,
            message="Featured preview works retrieved successfully"
        )
        
    except Exception as e:
        logger.error(f"Error getting featured preview works: {str(e)}")
        return error_response(
            message="An error occurred while retrieving featured preview works",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.get("/prompt/{slug}")
def get_work_by_slug(
    slug: str,
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """
    Get work detail by slug (supports both formats):
    - /api/works/prompt/5UWSKI183_s (short_code only - backward compatibility)
    - /api/works/prompt/5UWSKI183_s-ai-artwork (url_slug format - SEO friendly)
    """
    try:
        from ..utils.url_slug import extract_short_code_from_slug
        
        # Extract short_code from slug (handles both formats)
        short_code = extract_short_code_from_slug(slug)
        
        # Try to find by url_slug first (for new format: short_code-title-slug)
        work = db.query(Work).filter(
            Work.url_slug == slug,
            Work.deleted_at == None  # Exclude soft deleted works
        ).first()
        
        # Fallback to short_code (for backward compatibility: just short_code)
        if not work:
            work = db.query(Work).filter(
                Work.short_code == short_code,
                Work.deleted_at == None  # Exclude soft deleted works
            ).first()
        
        if not work:
            return error_response(
                message="Work not found",
                status_code=status.HTTP_404_NOT_FOUND
            )
        
        # Import NSFWStatus for checking
        from ..models.moderation import NSFWStatus
        
        # Check access permissions
        # For public works: must be shared, approved, and NSFW approved (or null for old works)
        is_public = (
            work.is_shared and 
            work.share_status == ShareStatus.APPROVED and
            (work.nsfw_status == NSFWStatus.APPROVED.value or work.nsfw_status == None)
        )
        
        if not is_public:
            # Private work or blocked NSFW - require auth and ownership
            if not current_user or work.user_id != current_user.id:
                return error_response(
                    message="Not authorized to view this work",
                    status_code=status.HTTP_403_FORBIDDEN
                )
            
            # Generate presigned URLs for private files
            storage = get_storage_service()
            work_dict = work.to_dict(include_user=True, include_prompt=True)
            
            if work.file_url:
                # Extract key from URL (flat storage: just the filename)
                file_key = work.file_url.split('/')[-1]
                file_key = file_key.split('?')[0]
                work_dict['file_url'] = storage.generate_presigned_url(file_key)
            
            if work.thumbnail_url:
                thumb_key = work.thumbnail_url.split('/')[-1]
                thumb_key = thumb_key.split('?')[0]
                work_dict['thumbnail_url'] = storage.generate_presigned_url(thumb_key)
            
            # Include parent work info if exists (for attribution/SEO)
            if work.parent_id:
                parent_work = db.query(Work).filter(Work.id == work.parent_id).first()
                if parent_work:
                    work_dict['parent'] = {
                        'id': parent_work.id,
                        'url_slug': parent_work.url_slug,
                        'short_code': parent_work.short_code,
                        'share_name': parent_work.share_name,
                        'title': parent_work.title,
                        'user': {
                            'id': parent_work.user_id,
                            'handle': parent_work.user.handle if parent_work.user else None,
                            'nickname': parent_work.user.nickname if parent_work.user else None,
                        } if parent_work.user else None
                    }
            
            return success_response(
                data=work_dict,
                message="Work retrieved successfully"
            )
        
        # Public work - increment view count
        work.view_count += 1
        db.commit()
        
        # Get user's interaction status if authenticated
        current_user_id = current_user.id if current_user else None
        work_dict = work.to_dict(include_user=True, include_prompt=True, current_user_id=current_user_id, db=db)
        
        # Include parent work info if exists (for attribution/SEO)
        if work.parent_id:
            parent_work = db.query(Work).filter(Work.id == work.parent_id).first()
            if parent_work:
                work_dict['parent'] = {
                    'id': parent_work.id,
                    'url_slug': parent_work.url_slug,
                    'short_code': parent_work.short_code,
                    'share_name': parent_work.share_name,
                    'title': parent_work.title,
                    'user': {
                        'id': parent_work.user_id,
                        'handle': parent_work.user.handle if parent_work.user else None,
                        'nickname': parent_work.user.nickname if parent_work.user else None,
                    } if parent_work.user else None
                }
        
        # Check favorite status
        is_favorited = False
        if current_user:
            favorite = db.query(Favorite).filter(
                and_(
                    Favorite.user_id == current_user.id,
                    Favorite.work_id == work.id
                )
            ).first()
            is_favorited = favorite is not None
        
        work_dict['is_favorited'] = is_favorited
        
        return success_response(
            data=work_dict,
            message="Work retrieved successfully"
        )
        
    except Exception as e:
        logger.error(f"Error getting work by short_code: {str(e)}")
        return error_response(
            message="An error occurred while retrieving work",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.get("/proxy-download")
async def proxy_download(url: str):
    """
    Proxy a file download to bypass CORS for client-side blob generation.
    """
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(url, follow_redirects=True, timeout=60.0)
            resp.raise_for_status()
            
            # Forward the content type
            content_type = resp.headers.get("content-type", "application/octet-stream")
            
            # Use a generator to stream the response
            async def iterate_content():
                async for chunk in resp.aiter_bytes():
                    yield chunk
                    
            return StreamingResponse(
                iterate_content(),
                media_type=content_type
            )
    except Exception as e:
        logger.error(f"Proxy download failed for {url}: {str(e)}")
        raise HTTPException(status_code=400, detail="Failed to proxy file")


@router.get("/{work_id_or_uuid}")
def get_work_detail(
    work_id_or_uuid: str,
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """
    Get work detail with full prompt.
    Supports both numeric ID and UUID (prompt_id).
    Requires auth for non-shared works.
    """
    try:
        # Try to query by ID first if it's numeric, otherwise by prompt_id (UUID)
        if work_id_or_uuid.isdigit():
            work = db.query(Work).filter(
                Work.id == int(work_id_or_uuid),
                Work.deleted_at == None  # Exclude soft deleted works
            ).first()
        else:
            work = db.query(Work).filter(
                Work.prompt_id == work_id_or_uuid,
                Work.deleted_at == None  # Exclude soft deleted works
            ).first()
        
        if not work:
            return error_response(
                message="Work not found",
                status_code=status.HTTP_404_NOT_FOUND
            )
        
        # Import NSFWStatus for checking
        from ..models.moderation import NSFWStatus
        
        # Check access permissions
        # For public works: must be shared, approved, and NSFW approved (or null for old works)
        is_public = (
            work.is_shared and 
            work.share_status == ShareStatus.APPROVED and
            (work.nsfw_status == NSFWStatus.APPROVED.value or work.nsfw_status == None)
        )
        
        if not is_public:
            # Private work or blocked NSFW - require auth and ownership
            if not current_user or work.user_id != current_user.id:
                return error_response(
                    message="Not authorized to view this work",
                    status_code=status.HTTP_403_FORBIDDEN
                )
            
            # Generate presigned URLs for private files
            storage = get_storage_service()
            work_dict = work.to_dict(include_user=True, include_prompt=True)
            
            if work.file_url:
                # Extract key from URL (flat storage: just the filename)
                # URL format: https://cdn.example.com/9kg03zfbcmucrfamc3epkxz4fkhv.jpg
                file_key = work.file_url.split('/')[-1]  # Last part (filename only)
                # Remove query parameters if any
                file_key = file_key.split('?')[0]
                work_dict['file_url'] = storage.generate_presigned_url(file_key)
            
            if work.thumbnail_url:
                thumb_key = work.thumbnail_url.split('/')[-1]  # Last part (filename only)
                thumb_key = thumb_key.split('?')[0]  # Remove query parameters if any
                work_dict['thumbnail_url'] = storage.generate_presigned_url(thumb_key)
            
            # Include parent work info if exists (for attribution/SEO)
            if work.parent_id:
                parent_work = db.query(Work).filter(Work.id == work.parent_id).first()
                if parent_work:
                    work_dict['parent'] = {
                        'id': parent_work.id,
                        'url_slug': parent_work.url_slug,
                        'short_code': parent_work.short_code,
                        'share_name': parent_work.share_name,
                        'title': parent_work.title,
                        'user': {
                            'id': parent_work.user_id,
                            'handle': parent_work.user.handle if parent_work.user else None,
                            'nickname': parent_work.user.nickname if parent_work.user else None,
                        } if parent_work.user else None
                    }
            
            return success_response(
                data=work_dict,
                message="Work retrieved successfully"
            )
        
        # Public work - increment view count
        work.view_count += 1
        db.commit()
        
        # Get user's interaction status if authenticated
        current_user_id = current_user.id if current_user else None
        work_dict = work.to_dict(include_user=True, include_prompt=True, current_user_id=current_user_id, db=db)
        
        # Include parent work info if exists (for attribution/SEO)
        if work.parent_id:
            parent_work = db.query(Work).filter(Work.id == work.parent_id).first()
            if parent_work:
                work_dict['parent'] = {
                    'id': parent_work.id,
                    'url_slug': parent_work.url_slug,
                    'short_code': parent_work.short_code,
                    'share_name': parent_work.share_name,
                    'title': parent_work.title,
                    'user': {
                        'id': parent_work.user_id,
                        'handle': parent_work.user.handle if parent_work.user else None,
                        'nickname': parent_work.user.nickname if parent_work.user else None,
                    } if parent_work.user else None
                }
        
        # Check favorite status
        is_favorited = False
        if current_user:
            favorite = db.query(Favorite).filter(
                and_(
                    Favorite.user_id == current_user.id,
                    Favorite.work_id == work.id
                )
            ).first()
            is_favorited = favorite is not None
        
        work_dict['is_favorited'] = is_favorited
        
        return success_response(
            data=work_dict,
            message="Work retrieved successfully"
        )
        
    except Exception as e:
        logger.error(f"Error getting work detail: {str(e)}")
        return error_response(
            message="An error occurred while retrieving work",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.get("/prompt/{slug}/forks")
def get_work_forks_by_slug(
    slug: str,
    page: int = 1,
    page_size: int = 20,
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """
    Get all public works derived from this work (by slug).
    """
    try:
        from ..utils.url_slug import extract_short_code_from_slug
        
        # Extract short_code from slug
        short_code = extract_short_code_from_slug(slug)
        
        # Find work by url_slug or short_code
        work = db.query(Work).filter(
            Work.url_slug == slug,
            Work.deleted_at == None
        ).first()
        if not work:
            work = db.query(Work).filter(
                Work.short_code == short_code,
                Work.deleted_at == None
            ).first()
        
        if not work:
            return error_response(message="Base work not found", status_code=status.HTTP_404_NOT_FOUND)
        
        base_work_id = work.id
        
        # Query forks
        query = db.query(Work).filter(
            Work.parent_id == base_work_id,
            Work.is_shared == True,
            Work.share_status == ShareStatus.APPROVED,
            Work.status == WorkStatus.SUCCESS,
            Work.deleted_at == None,  # Exclude soft deleted forks
            Work.hidden == False  # Exclude hidden forks
        )

        total = query.count()
        forks = query.order_by(desc(Work.created_at)).offset((page - 1) * page_size).limit(page_size).all()

        # Batch prefetch auxiliary data to avoid N+1 queries
        from ..models.work import batch_prefetch_work_data
        current_user_id = current_user.id if current_user else None
        prefetched = batch_prefetch_work_data(forks, db, current_user_id)
        
        items = [
            work.to_dict(
                include_user=True, 
                include_prompt=False, 
                current_user_id=current_user_id, 
                db=db,
                prefetched_counts=prefetched['counts'],
                prefetched_likes=prefetched['liked_work_ids'],
                prefetched_follows=prefetched['following_user_ids']
            ) for work in forks
        ]

        return paginated_response(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            message="Forks retrieved successfully"
        )
    except Exception as e:
        logger.error(f"Error getting work forks: {str(e)}")
        return error_response(
            message="An error occurred while retrieving forks",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.get("/{work_id_or_uuid}/forks")
def get_work_forks(
    work_id_or_uuid: str,
    page: int = 1,
    page_size: int = 20,
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """
    Get all public works derived from this work.
    """
    try:
        # Get base work ID
        if work_id_or_uuid.isdigit():
            base_work_id = int(work_id_or_uuid)
        else:
            base_work = db.query(Work).filter(
                Work.prompt_id == work_id_or_uuid,
                Work.deleted_at == None
            ).first()
            if not base_work:
                return error_response(message="Base work not found", status_code=status.HTTP_404_NOT_FOUND)
            base_work_id = base_work.id

        # Query forks
        query = db.query(Work).filter(
            Work.parent_id == base_work_id,
            Work.is_shared == True,
            Work.share_status == ShareStatus.APPROVED,
            Work.status == WorkStatus.SUCCESS,
            Work.deleted_at == None,  # Exclude soft deleted forks
            Work.hidden == False  # Exclude hidden forks
        )

        total = query.count()
        forks = query.order_by(desc(Work.created_at)).offset((page - 1) * page_size).limit(page_size).all()

        # Batch prefetch auxiliary data to avoid N+1 queries
        from ..models.work import batch_prefetch_work_data
        current_user_id = current_user.id if current_user else None
        prefetched = batch_prefetch_work_data(forks, db, current_user_id)
        
        items = [
            work.to_dict(
                include_user=True, 
                include_prompt=False, 
                current_user_id=current_user_id, 
                db=db,
                prefetched_counts=prefetched['counts'],
                prefetched_likes=prefetched['liked_work_ids'],
                prefetched_follows=prefetched['following_user_ids']
            ) for work in forks
        ]

        return paginated_response(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            message="Forks retrieved successfully"
        )
    except Exception as e:
        logger.error(f"Error getting work forks: {str(e)}")
        return error_response(
            message="An error occurred while retrieving forks",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.post("/{work_id}/like")
def toggle_like(
    work_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Toggle like status for a work.
    """
    try:
        work = db.query(Work).filter(
            Work.id == work_id,
            Work.deleted_at == None  # Cannot like deleted works
        ).first()
        
        if not work:
            return error_response(
                message="Work not found",
                status_code=status.HTTP_404_NOT_FOUND
            )
        
        # Check if already liked
        like = db.query(Like).filter(
            and_(
                Like.user_id == current_user.id,
                Like.work_id == work_id
            )
        ).first()
        
        if like:
            # Unlike
            db.delete(like)
            work.like_count = max(0, work.like_count - 1)
            is_liked = False
        else:
            # Like
            new_like = Like(
                user_id=current_user.id,
                work_id=work_id
            )
            db.add(new_like)
            work.like_count += 1
            is_liked = True
            
            # Send notification to author if it's not their own work
            if work.user_id != current_user.id:
                from ..utils.notification import create_notification
                from ..models.notification import NotificationType
                create_notification(
                    db=db,
                    user_id=work.user_id,
                    type=NotificationType.NEW_LIKE,
                    title="New Like! ❤️",
                    content=f"{current_user.nickname or current_user.handle} liked your work '{work.share_name or work.title}'",
                    link_url=f"/prompt/{work.url_slug or work.short_code}"
                )
        
        db.commit()
        
        return success_response(
            data={"like_count": work.like_count, "is_liked": is_liked},
            message="Like status updated"
        )
        
    except Exception as e:
        logger.error(f"Error toggling like: {str(e)}")
        return error_response(
            message="An error occurred",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.post("/{work_id}/favorite")
def toggle_favorite(
    work_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Toggle favorite status for a work.
    """
    try:
        work = db.query(Work).filter(
            Work.id == work_id,
            Work.deleted_at == None  # Cannot favorite deleted works
        ).first()
        
        if not work:
            return error_response(
                message="Work not found",
                status_code=status.HTTP_404_NOT_FOUND
            )
        
        # Check if already favorited
        favorite = db.query(Favorite).filter(
            and_(
                Favorite.user_id == current_user.id,
                Favorite.work_id == work_id
            )
        ).first()
        
        if favorite:
            # Unfavorite
            db.delete(favorite)
            work.favorite_count = max(0, work.favorite_count - 1)
            is_favorited = False
        else:
            # Favorite
            new_favorite = Favorite(
                user_id=current_user.id,
                work_id=work_id
            )
            db.add(new_favorite)
            work.favorite_count += 1
            is_favorited = True
        
        db.commit()
        
        return success_response(
            data={
                "favorite_count": work.favorite_count,
                "is_favorited": is_favorited
            },
            message="Favorite status updated"
        )
        
    except Exception as e:
        logger.error(f"Error toggling favorite: {str(e)}")
        return error_response(
            message="An error occurred",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.post("/{work_id}/toggle-share")
def toggle_share(
    work_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Toggle a work between public (shared) and private.
    """
    try:
        work = db.query(Work).filter(
            Work.id == work_id,
            Work.deleted_at == None  # Cannot toggle deleted works
        ).first()
        if not work or work.user_id != current_user.id:
            return error_response(message="Work not found", status_code=status.HTTP_404_NOT_FOUND)

        # Toggle sharing
        work.is_shared = not work.is_shared
        
        if work.is_shared:
            work.share_status = ShareStatus.APPROVED
            # If no title exists, generate one using utility function
            if not work.title:
                work.title = generate_work_title(work.prompt)
                # Don't auto-set category, let user choose
            
            # Set share_name to title if share_name doesn't exist
            if not work.share_name:
                work.share_name = work.title
            
            # If no description exists, generate one using utility function
            if not work.description:
                work.description = generate_work_description(work.prompt, work.model_name)
                # Update canonical_url if storage_key exists
                if work.storage_key and work.title:
                    from ..services.storage import get_storage_service
                    storage = get_storage_service()
                    # Check if it's a video type
                    is_video = work.type in ["text-to-video", "image-to-video"] or "video" in work.type.lower()
                    file_ext = "mp4" if is_video else "jpg"
                    work.canonical_url = storage.generate_canonical_url(work.storage_key, work.title, file_ext)
        else:
            work.share_status = None

        db.commit()
        return success_response(
            data={"is_shared": work.is_shared, "share_status": work.share_status},
            message="Privacy status updated"
        )
    except Exception as e:
        logger.error(f"Error toggling share: {str(e)}")
        return error_response(message="An error occurred")


@router.put("/{work_id}")
def update_work(
    work_id: int,
    request: UpdateWorkRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Update a work (e.g., title).
    """
    try:
        work = db.query(Work).filter(
            Work.id == work_id,
            Work.deleted_at == None  # Cannot update deleted works
        ).first()
        if not work or work.user_id != current_user.id:
            return error_response(message="Work not found", status_code=status.HTTP_404_NOT_FOUND)

        # Update share_name if provided (display title)
        if request.share_name is not None:
            work.share_name = request.share_name
        
        # Update title if provided (SEO title)
        if request.title is not None:
            work.title = request.title
            # Update canonical_url if storage_key exists
            if work.storage_key:
                from ..services.storage import get_storage_service
                storage = get_storage_service()
                # Check if it's a video type
                is_video = work.type in ["text-to-video", "image-to-video"] or "video" in work.type.lower()
                file_ext = "mp4" if is_video else "jpg"
                work.canonical_url = storage.generate_canonical_url(work.storage_key, work.title, file_ext)

        db.commit()
        return success_response(
            data=work.to_dict(include_prompt=True),
            message="Work updated successfully"
        )
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating work: {str(e)}")
        return error_response(message="An error occurred")


@router.delete("/{work_id}")
def delete_work(
    work_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Soft delete a work (only by owner).
    The work will be marked as deleted but not physically removed from database.
    """
    try:
        from datetime import datetime, timezone
        
        work = db.query(Work).filter(
            Work.id == work_id,
            Work.deleted_at == None  # Only allow deleting non-deleted works
        ).first()
        
        if not work or work.user_id != current_user.id:
            return error_response(message="Work not found", status_code=status.HTTP_404_NOT_FOUND)

        # Soft delete: set deleted_at timestamp
        work.deleted_at = datetime.now(timezone.utc)
        work.updated_at = datetime.now(timezone.utc)
        db.commit()
        
        logger.info(f"Work {work_id} soft deleted by user {current_user.id}")
        
        return success_response(
            message="Work deleted successfully"
        )
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting work: {str(e)}")
        return error_response(message="An error occurred")


@router.post("/{work_id}/submit-share")
def submit_share(
    work_id: int,
    request: SubmitShareRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Submit a work for sharing review.
    """
    try:
        work = db.query(Work).filter(
            Work.id == work_id,
            Work.deleted_at == None  # Cannot submit deleted works
        ).first()
        
        if not work:
            return error_response(
                message="Work not found",
                status_code=status.HTTP_404_NOT_FOUND
            )
        
        # Check ownership
        if work.user_id != current_user.id:
            return error_response(
                message="Not authorized",
                status_code=status.HTTP_403_FORBIDDEN
            )
        
        # Check if work is completed
        if work.status != WorkStatus.SUCCESS:
            return error_response(
                message="Only completed works can be shared",
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if already shared
        if work.is_shared:
            return error_response(
                message="Work is already submitted for sharing",
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        # Update work
        work.is_shared = True
        work.share_status = ShareStatus.PENDING
        work.title = request.title
        work.category = request.category
        
        # Update canonical_url if storage_key exists
        if work.storage_key:
            from ..services.storage import get_storage_service
            storage = get_storage_service()
            # Check if it's a video type
            is_video = work.type in ["text-to-video", "image-to-video"] or "video" in work.type.lower()
            file_ext = "mp4" if is_video else "jpg"
            work.canonical_url = storage.generate_canonical_url(work.storage_key, work.title, file_ext)
        
        db.commit()
        
        logger.info(f"Work {work.id} submitted for sharing by user {current_user.id}")
        
        return success_response(
            message="Work submitted for review successfully"
        )
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error submitting work for sharing: {str(e)}")
        return error_response(
            message="An error occurred",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


class ReportWorkRequest(BaseModel):
    """"""
    report_type: str = Field(..., description=": pornography, violence, gore, harassment, spam, copyright, other")
    reason: Optional[str] = Field(None, max_length=500, description="")


@router.post("/{work_id}/report")
def report_work(
    work_id: int,
    request: ReportWorkRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Report work
    """
    try:
        work = db.query(Work).filter(
            Work.id == work_id,
            Work.deleted_at == None
        ).first()
        
        if not work:
            return error_response(
                message="Work not found",
                status_code=status.HTTP_404_NOT_FOUND
            )
        
        # （）
        existing_report = db.query(Report).filter(
            Report.work_id == work_id,
            Report.reporter_id == current_user.id,
            Report.status == ReportStatus.PENDING
        ).first()
        
        if existing_report:
            return error_response(
                message="You have already reported this work",
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        #
        try:
            report_type_enum = ReportType(request.report_type)
        except ValueError:
            return error_response(
                message="Invalid report type",
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        #
        report = Report(
            work_id=work_id,
            reporter_id=current_user.id,
            report_type=report_type_enum,
            reason=request.reason,
            status=ReportStatus.PENDING
        )
        
        db.add(report)
        db.commit()
        db.refresh(report)
        
        logger.info(f"Work {work_id} reported by user {current_user.id}")
        
        return success_response(
            data={"report_id": report.id},
            message="Report submitted successfully"
        )
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error reporting work: {str(e)}")
        return error_response(
            message="An error occurred",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

