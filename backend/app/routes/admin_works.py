"""
Admin routes for managing all works.
"""
from fastapi import APIRouter, Depends, Query, status as http_status, Body
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from datetime import datetime, timezone
from typing import Optional, List
from pydantic import BaseModel, Field

from ..models.base import get_db
from ..models.admin import Admin
from ..models.work import Work, WorkStatus, ShareStatus
from ..models.moderation import NSFWStatus
from ..models.user import User
from ..models.category_page import CategoryPage
from ..utils.auth import get_current_admin
from ..utils.responses import success_response, error_response, paginated_response
from ..utils.logger import logger
from ..services.storage import get_storage_service
import re

router = APIRouter()


def _parse_iso_datetime(s: Optional[str]):
    """Parse ISO datetime string to timezone-aware datetime for DB comparison."""
    if not s:
        return None
    s = s.strip().replace("Z", "+00:00")
    try:
        return datetime.fromisoformat(s)
    except (ValueError, TypeError):
        return None


def apply_work_filters(query, search=None, author_search=None, status=None, nsfw_status=None, is_banned=None, is_deleted=None, is_featured=None, hidden=None, category=None, user_id=None, has_url=None, share_status=None, work_type=None, model_name=None, is_shared=None, work_id=None, date_from=None, date_to=None):
    """Helper function to apply common work filters to a query."""
    from ..models.user import User
    
    # Apply filters
    filters = []
    
    # Work ID filter (exact match)
    if work_id is not None:
        try:
            wid = int(work_id)
            filters.append(Work.id == wid)
        except (TypeError, ValueError):
            pass
    
    # Search filter (Title/Prompt)
    if search:
        search_term = f"%{search}%"
        filters.append(
            or_(
                Work.title.ilike(search_term),
                Work.share_name.ilike(search_term),
                Work.prompt.ilike(search_term),
                Work.description.ilike(search_term)
            )
        )
    
    # Author Search filter
    if author_search:
        author_term = author_search.strip()
        # If user entered @handle, search specifically for that
        if author_term.startswith('@'):
            handle_val = author_term[1:] # Remove @
            query = query.join(User).filter(User.handle.ilike(f"%{handle_val}%"))
        else:
            # Search both nickname and handle
            search_val = f"%{author_term}%"
            query = query.join(User).filter(
                or_(
                    User.nickname.ilike(search_val),
                    User.handle.ilike(search_val)
                )
            )
    
    # Status filter
    if status:
        try:
            filters.append(Work.status == WorkStatus(status))
        except ValueError:
            pass
    
    # Share status filter
    if share_status:
        try:
            filters.append(Work.share_status == ShareStatus(share_status))
        except ValueError:
            pass
    
    # NSFW status filter
    if nsfw_status:
        filters.append(Work.nsfw_status == nsfw_status)
    
    # Banned filter
    if is_banned is not None:
        filters.append(Work.is_banned == is_banned)
    
    # Deleted filter
    if is_deleted is True:
        filters.append(Work.deleted_at != None)
    elif is_deleted is False:
        filters.append(Work.deleted_at == None)

    # Featured filter
    if is_featured is not None:
        filters.append(Work.is_featured == is_featured)
        
    # Hidden filter
    if hidden is not None:
        filters.append(Work.hidden == hidden)
        
    # Category filter
    if category:
        if category == "__UNCATEGORIZED__":
            # Filter for works with no category (null or empty)
            filters.append(
                or_(
                    Work.category == None,
                    Work.category == ""
                )
            )
        elif "|" in category:
            # Hierarchical: exact match
            filters.append(Work.category == category)
        else:
            # Single level: match both standalone and hierarchical
            filters.append(
                or_(
                    Work.category == category,
                    Work.category.like(f"{category}|%")
                )
            )
    
    # User filter
    if user_id:
        filters.append(Work.user_id == user_id)
    
    # Has URL filter (has url_slug or short_code)
    if has_url:
        filters.append(
            or_(
                Work.url_slug.isnot(None),
                Work.short_code.isnot(None)
            )
        )
    
    # Work type filter
    if work_type:
        try:
            from ..models.work import WorkType
            filters.append(Work.type == WorkType(work_type))
        except ValueError:
            pass
    
    # Model name filter
    if model_name:
        filters.append(Work.model_name == model_name)
    
    # Is shared filter (public/private)
    if is_shared is not None:
        filters.append(Work.is_shared == is_shared)
    
    # Updated date range (filter by Work.updated_at)
    if date_from:
        dt_from = _parse_iso_datetime(date_from)
        if dt_from is not None:
            filters.append(Work.updated_at >= dt_from)
    if date_to:
        dt_to = _parse_iso_datetime(date_to)
        if dt_to is not None:
            filters.append(Work.updated_at <= dt_to)
    
    # Apply all filters
    if filters:
        query = query.filter(and_(*filters))
        
    return query


@router.get("/works")
def get_all_works(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    work_id: Optional[str] = Query(None, description="Search by work ID (exact)"),
    search: Optional[str] = Query(None, description="Search by title, prompt, or description"),
    author_search: Optional[str] = Query(None, description="Search by author nickname or @handle"),
    status: Optional[str] = Query(None, description="Filter by work status"),
    share_status: Optional[str] = Query(None, description="Filter by share status (pending, approved, rejected)"),
    nsfw_status: Optional[str] = Query(None, description="Filter by NSFW moderation status"),
    is_banned: Optional[bool] = Query(None, description="Filter by banned status"),
    is_deleted: Optional[bool] = Query(None, description="Filter by deleted status (True=only deleted, False=only active, None=all)"),
    is_featured: Optional[bool] = Query(None, description="Filter by featured status"),
    hidden: Optional[bool] = Query(None, description="Filter by hidden status"),
    category: Optional[str] = Query(None, description="Filter by category"),
    user_id: Optional[int] = Query(None, description="Filter by user ID"),
    has_url: Optional[bool] = Query(None, description="Filter by works that have URL (url_slug or short_code)"),
    work_type: Optional[str] = Query(None, description="Filter by work type (text-to-image, text-to-video, image-to-image, image-to-video)"),
    model_name: Optional[str] = Query(None, description="Filter by model name"),
    is_shared: Optional[bool] = Query(None, description="Filter by shared status (True=public, False=private)"),
    date_from: Optional[str] = Query(None, description="Filter by updated_at >= (ISO datetime)"),
    date_to: Optional[str] = Query(None, description="Filter by updated_at <= (ISO datetime)"),
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Get all works with advanced filtering.
    Supports filtering by soft-deleted status and author.
    """
    try:
        # Build base query
        query = db.query(Work)
        
        # Apply filters using helper
        query = apply_work_filters(
            query, search, author_search, status, nsfw_status,
            is_banned, is_deleted, is_featured, hidden, category, user_id, has_url, share_status,
            work_type, model_name, is_shared, work_id, date_from, date_to
        )
        
        # Get total count
        total = query.count()
        
        # Get paginated works
        works = query.order_by(
            Work.id.desc()
        ).offset((page - 1) * page_size).limit(page_size).all()
        
        # Batch prefetch auxiliary data to avoid N+1 queries
        from ..models.work import batch_prefetch_work_data
        prefetched = batch_prefetch_work_data(works, db, None)
        
        # Batch query admin-specific fork counts (all remixes, not just approved)
        work_ids = [w.id for w in works]
        admin_fork_counts = {}
        if work_ids:
            from sqlalchemy.sql import func as sql_func
            admin_fork_results = db.query(
                Work.parent_id,
                sql_func.count(Work.id).label('count')
            ).filter(
                Work.parent_id.in_(work_ids),
                Work.deleted_at == None
            ).group_by(Work.parent_id).all()
            
            for parent_id, count in admin_fork_results:
                admin_fork_counts[parent_id] = count
        
        # Batch query NSFW block reasons for blocked works
        blocked_work_ids = [w.id for w in works if w.nsfw_status == 'BLOCKED']
        nsfw_block_reasons = {}
        if blocked_work_ids:
            from ..models.moderation import ModerationLog, ModerationType, ModerationAction
            # Get latest block log for each blocked work
            for work_id in blocked_work_ids:
                latest_block_log = db.query(ModerationLog).filter(
                    ModerationLog.work_id == work_id,
                    ModerationLog.moderation_type == ModerationType.NSFW,
                    ModerationLog.action_type.in_([ModerationAction.AUTO_BLOCKED, ModerationAction.MANUAL_REJECTED])
                ).order_by(ModerationLog.created_at.desc()).first()
                if latest_block_log and latest_block_log.reason:
                    nsfw_block_reasons[work_id] = latest_block_log.reason
                else:
                    nsfw_block_reasons[work_id] = "NSFW"
        
        # Convert to dict with full information
        items = []
        for work in works:
            work_dict = work.to_dict(
                include_user=True, 
                include_prompt=True, 
                db=db,
                prefetched_counts=prefetched['counts'],
                prefetched_likes=prefetched['liked_work_ids'],
                prefetched_follows=prefetched['following_user_ids']
            )
            # Add additional info
            work_dict['is_banned'] = work.is_banned
            work_dict['is_featured'] = work.is_featured
            work_dict['ban_reason'] = work.ban_reason
            work_dict['deleted_at'] = work.deleted_at.isoformat() if work.deleted_at else None
            
            # Use prefetched NSFW block reason
            work_dict['nsfw_block_reason'] = nsfw_block_reasons.get(work.id)
            
            # Use prefetched admin fork count (all remixes, not just approved)
            work_dict['fork_count'] = admin_fork_counts.get(work.id, 0)
            
            items.append(work_dict)
        
        return paginated_response(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            message="Works retrieved successfully"
        )
        
    except Exception as e:
        logger.error(f"Error getting all works: {str(e)}")
        return error_response(
            message="Failed to retrieve works",
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.get("/works/{work_id}")
def get_work_detail(
    work_id: int,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Get detailed information about a specific work.
    """
    try:
        work = db.query(Work).filter(Work.id == work_id).first()
        
        if not work:
            return error_response(
                message="Work not found",
                status_code=http_status.HTTP_404_NOT_FOUND
            )
        
        work_dict = work.to_dict(include_user=True, include_prompt=True, db=db)
        work_dict['is_banned'] = work.is_banned
        work_dict['ban_reason'] = work.ban_reason
        work_dict['deleted_at'] = work.deleted_at.isoformat() if work.deleted_at else None
        
        return success_response(
            data=work_dict,
            message="Work details retrieved successfully"
        )
        
    except Exception as e:
        logger.error(f"Error getting work detail: {str(e)}")
        return error_response(
            message="Failed to retrieve work details",
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.post("/works/{work_id}/ban")
def ban_work(
    work_id: int,
    reason: str = Query(..., description="Reason for banning (English only)"),
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Ban a work (mark as inappropriate/violating).
    """
    try:
        from ..utils.validation import validate_reason_english
        valid, err = validate_reason_english(reason)
        if not valid:
            return error_response(message=err or "Invalid reason", status_code=400)

        work = db.query(Work).filter(Work.id == work_id).first()
        
        if not work:
            return error_response(
                message="Work not found",
                status_code=http_status.HTTP_404_NOT_FOUND
            )
        
        if work.is_banned:
            return error_response(
                message="Work is already banned",
                status_code=http_status.HTTP_400_BAD_REQUEST
            )
        
        # Ban the work
        work.is_banned = True
        work.ban_reason = reason
        work.updated_at = datetime.now(timezone.utc)
        
        db.commit()
        
        # Send notification to user
        from ..utils.notification import create_notification
        from ..models.notification import NotificationType
        
        create_notification(
            db=db,
            user_id=work.user_id,
            type=NotificationType.SYSTEM,
            title="Work Banned ❌",
            content=f"Your work '{work.share_name or work.title}' has been banned. Reason: {reason}",
            link_url="/profile"
        )
        
        logger.info(f"Admin {current_admin.username} banned work {work_id}: {reason}")
        
        return success_response(
            message="Work banned successfully"
        )
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error banning work: {str(e)}")
        return error_response(
            message="Failed to ban work",
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.post("/works/{work_id}/unban")
def unban_work(
    work_id: int,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Unban a work (restore it).
    """
    try:
        work = db.query(Work).filter(Work.id == work_id).first()
        
        if not work:
            return error_response(
                message="Work not found",
                status_code=http_status.HTTP_404_NOT_FOUND
            )
        
        if not work.is_banned:
            return error_response(
                message="Work is not banned",
                status_code=http_status.HTTP_400_BAD_REQUEST
            )
        
        # Unban the work
        work.is_banned = False
        work.ban_reason = None
        work.updated_at = datetime.now(timezone.utc)
        
        db.commit()
        
        # Send notification to user
        from ..utils.notification import create_notification
        from ..models.notification import NotificationType
        
        create_notification(
            db=db,
            user_id=work.user_id,
            type=NotificationType.SYSTEM,
            title="Work Restored ✅",
            content=f"Your work '{work.share_name or work.title}' has been unbanned and is now accessible again.",
            link_url=f"/prompt/{work.url_slug or work.short_code}"
        )
        
        logger.info(f"Admin {current_admin.username} unbanned work {work_id}")
        
        return success_response(
            message="Work unbanned successfully"
        )
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error unbanning work: {str(e)}")
        return error_response(
            message="Failed to unban work",
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.post("/works/{work_id}/restore")
def restore_work(
    work_id: int,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Restore a soft-deleted work.
    """
    try:
        work = db.query(Work).filter(Work.id == work_id).first()
        
        if not work:
            return error_response(
                message="Work not found",
                status_code=http_status.HTTP_404_NOT_FOUND
            )
        
        if not work.deleted_at:
            return error_response(
                message="Work is not deleted",
                status_code=http_status.HTTP_400_BAD_REQUEST
            )
        
        # Restore the work
        work.deleted_at = None
        work.updated_at = datetime.now(timezone.utc)
        
        db.commit()
        
        # Send notification to user
        from ..utils.notification import create_notification
        from ..models.notification import NotificationType
        
        create_notification(
            db=db,
            user_id=work.user_id,
            type=NotificationType.SYSTEM,
            title="Work Restored ✅",
            content=f"Your work '{work.share_name or work.title}' has been restored by an administrator.",
            link_url=f"/prompt/{work.url_slug or work.short_code}"
        )
        
        logger.info(f"Admin {current_admin.username} restored work {work_id}")
        
        return success_response(
            message="Work restored successfully"
        )
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error restoring work: {str(e)}")
        return error_response(
            message="Failed to restore work",
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.post("/works/{work_id}/toggle-visibility")
def toggle_work_visibility(
    work_id: int,
    make_public: bool = Query(..., description="True to make public, False to make private"),
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Force change work visibility status.
    """
    try:
        work = db.query(Work).filter(Work.id == work_id).first()
        
        if not work:
            return error_response(
                message="Work not found",
                status_code=http_status.HTTP_404_NOT_FOUND
            )
        
        # Toggle visibility
        work.is_shared = make_public
        work.updated_at = datetime.now(timezone.utc)
        
        db.commit()
        
        # Send notification to user
        from ..utils.notification import create_notification
        from ..models.notification import NotificationType
        
        status_text = "public 👁️" if make_public else "private 🔒"
        create_notification(
            db=db,
            user_id=work.user_id,
            type=NotificationType.SYSTEM,
            title=f"Work Visibility Updated",
            content=f"An administrator has set your work '{work.share_name or work.title}' to {status_text}.",
            link_url=f"/prompt/{work.url_slug or work.short_code}"
        )
        
        action = "public" if make_public else "private"
        logger.info(f"Admin {current_admin.username} set work {work_id} to {action}")
        
        return success_response(
            message=f"Work set to {action} successfully"
        )
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error toggling work visibility: {str(e)}")
        return error_response(
            message="Failed to toggle work visibility",
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.post("/works/{work_id}/soft-delete")
def soft_delete_work(
    work_id: int,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Soft delete a work (can be restored later).
    """
    try:
        work = db.query(Work).filter(
            Work.id == work_id,
            Work.deleted_at == None  # Only soft-delete active works
        ).first()
        
        if not work:
            return error_response(
                message="Work not found or already deleted",
                status_code=http_status.HTTP_404_NOT_FOUND
            )
        
        # Soft delete the work
        work.deleted_at = datetime.now(timezone.utc)
        work.updated_at = datetime.now(timezone.utc)
        
        db.commit()
        
        # Send notification to user
        from ..utils.notification import create_notification
        from ..models.notification import NotificationType
        
        create_notification(
            db=db,
            user_id=work.user_id,
            type=NotificationType.SYSTEM,
            title="Work Removed 🗑️",
            content=f"Your work '{work.share_name or work.title}' has been removed by an administrator.",
            link_url="/profile"
        )
        
        logger.info(f"Admin {current_admin.username} soft deleted work {work_id}")
        
        return success_response(
            message="Work soft deleted successfully"
        )
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error soft deleting work: {str(e)}")
        return error_response(
            message="Failed to soft delete work",
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR
        )


def extract_storage_key_from_url(url: str) -> Optional[str]:
    """
    Extract storage key from a URL.
    Handles various URL formats:
    - https://cdn.example.com/{key}
    - https://bucket.endpoint/{key}
    - http://localhost:8000/static/{key}
    - {key} (already a key)
    """
    if not url:
        return None
    
    # If it's already just a key (no http/https)
    if not url.startswith('http'):
        return url.split('?')[0]  # Remove query params
    
    # Remove protocol
    url_path = url.replace('https://', '').replace('http://', '')
    
    # Remove query parameters
    url_path = url_path.split('?')[0]
    
    # Extract the key (last part after /)
    if '/' in url_path:
        key = url_path.split('/')[-1]
    else:
        key = url_path
    
    # Handle canonical formats: {28ID}-{title}_thumb.webp -> {28ID}.webp
    if key.endswith('_thumb.webp'):
        match = re.match(r'^([A-Za-z0-9]{28})(-.*)?_thumb\.webp$', key)
        if match:
            key = f"{match.group(1)}.webp"
    elif key.endswith('_compressed.mp4'):
        match = re.match(r'^([A-Za-z0-9]{28})(-.*)?_compressed\.mp4$', key)
        if match:
            key = f"{match.group(1)}.mp4"
    
    return key


@router.delete("/works/{work_id}")
def delete_work(
    work_id: int,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Permanently delete a work and all related data.
    This will delete:
    - Comments (cascade)
    - Likes (cascade)
    - Favorites (cascade)
    - Moderation logs (cascade)
    - R2 storage files (file_url and thumbnail_url)
    WARNING: This action cannot be undone.
    """
    try:
        work = db.query(Work).filter(Work.id == work_id).first()
        
        if not work:
            return error_response(
                message="Work not found",
                status_code=http_status.HTTP_404_NOT_FOUND
            )
        
        # Store file URLs before deletion for R2 cleanup
        file_url = work.file_url
        thumbnail_url = work.thumbnail_url
        
        # Delete from R2 storage before database deletion
        storage = get_storage_service()
        deleted_files = []
        file_key = None
        
        if file_url:
            try:
                file_key = extract_storage_key_from_url(file_url)
                if file_key and storage.delete_file(file_key):
                    deleted_files.append(file_key)
                    logger.info(f"Deleted R2 file: {file_key}")
                else:
                    logger.warning(f"Failed to delete R2 file or key is None: {file_key}")
            except Exception as e:
                logger.warning(f"Error deleting R2 file_url {file_url}: {str(e)}")
        
        if thumbnail_url:
            try:
                thumb_key = extract_storage_key_from_url(thumbnail_url)
                # Don't delete same file twice (if thumbnail_url and file_url point to same file)
                if thumb_key and thumb_key != file_key:
                    if storage.delete_file(thumb_key):
                        deleted_files.append(thumb_key)
                        logger.info(f"Deleted R2 thumbnail: {thumb_key}")
                    else:
                        logger.warning(f"Failed to delete R2 thumbnail or key is None: {thumb_key}")
            except Exception as e:
                logger.warning(f"Error deleting R2 thumbnail_url {thumbnail_url}: {str(e)}")
        
        # Delete related records manually (even though cascade should handle it, we do it explicitly for clarity)
        # Note: SQLAlchemy cascade will handle:
        # - Comments (cascade="all, delete-orphan")
        # - Likes (ondelete="CASCADE")
        # - Favorites (cascade="all, delete-orphan")
        # - Moderation logs (ondelete="CASCADE")
        
        # Count related records for logging
        from ..models.comment import Comment
        from ..models.like import Like
        from ..models.favorite import Favorite
        from ..models.moderation import ModerationLog
        
        comment_count = db.query(Comment).filter(Comment.work_id == work_id).count()
        like_count = db.query(Like).filter(Like.work_id == work_id).count()
        favorite_count = db.query(Favorite).filter(Favorite.work_id == work_id).count()
        moderation_count = db.query(ModerationLog).filter(ModerationLog.work_id == work_id).count()
        
        # Manually delete moderation_logs first to avoid SQLAlchemy trying to set work_id to NULL
        # This is necessary because the work_id column has NOT NULL constraint
        db.query(ModerationLog).filter(ModerationLog.work_id == work_id).delete(synchronize_session=False)
        
        # Delete the work (cascading will handle other related records)
        db.delete(work)
        db.commit()
        
        logger.warning(
            f"Admin {current_admin.username} permanently deleted work {work_id}. "
            f"Related data deleted: {comment_count} comments, {like_count} likes, "
            f"{favorite_count} favorites, {moderation_count} moderation logs. "
            f"R2 files deleted: {deleted_files}"
        )
        
        return success_response(
            message="Work deleted permanently along with all related data and files"
        )
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting work: {str(e)}")
        import traceback
        logger.error(f"Delete error traceback:\n{traceback.format_exc()}")
        return error_response(
            message="Failed to delete work",
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.get("/users/search")
def search_users(
    query: str = Query(..., min_length=1, description="Search query for users"),
    limit: int = Query(10, ge=1, le=50),
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Search users by nickname, email, or handle for filtering works.
    """
    try:
        search_term = f"%{query}%"
        
        users = db.query(User).filter(
            or_(
                User.nickname.ilike(search_term),
                User.email.ilike(search_term),
                User.handle.ilike(search_term)
            )
        ).limit(limit).all()
        
        user_list = [
            {
                "id": user.id,
                "nickname": user.nickname,
                "email": user.email,
                "handle": user.handle,
                "avatar_url": user.avatar_url,
                "total_credits": user.total_credits if user.total_credits is not None else 0
            }
            for user in users
        ]
        
        return success_response(
            data=user_list,
            message="Users found"
        )
        
    except Exception as e:
        logger.error(f"Error searching users: {str(e)}")
        return error_response(
            message="Failed to search users",
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.post("/works/{work_id}/toggle-featured")
def toggle_featured(
    work_id: int,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Toggle featured status for a work.
    Featured works are shown on the homepage.
    """
    try:
        work = db.query(Work).filter(Work.id == work_id).first()
        
        if not work:
            return error_response(
                message="Work not found",
                status_code=http_status.HTTP_404_NOT_FOUND
            )
        
        # Toggle featured status
        work.is_featured = not work.is_featured
        work.updated_at = datetime.now(timezone.utc)
        
        db.commit()
        
        status_str = "featured" if work.is_featured else "unfeatured"
        logger.info(f"Admin {current_admin.username} set work {work_id} to {status_str}")
        
        # Send notification to user if featured
        if work.is_featured:
            from ..utils.notification import create_notification
            from ..models.notification import NotificationType
            
            create_notification(
                db=db,
                user_id=work.user_id,
                type=NotificationType.FEATURED,
                title="Your work is featured! ⭐",
                content=f"Congratulations! Your work '{work.share_name or work.title}' has been featured on the homepage.",
                link_url=f"/prompt/{work.url_slug or work.short_code}"
            )
        
        return success_response(
            data={"is_featured": work.is_featured},
            message=f"Work {status_str} successfully"
        )
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error toggling featured status: {str(e)}")
        return error_response(
            message="Failed to toggle featured status",
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR
        )


class UpdateWorkCategoryRequest(BaseModel):
    category: Optional[str] = None  # Format: "Level1" or "Level1|Level2"


@router.put("/works/{work_id}/category")
def update_work_category(
    work_id: int,
    request: UpdateWorkCategoryRequest = Body(...),
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Update the category of a work.
    Only allows categories that exist in the CategoryPage system.
    Format: "Level1" or "Level1|Level2"
    """
    try:
        work = db.query(Work).filter(Work.id == work_id).first()
        
        if not work:
            return error_response(
                message="Work not found",
                status_code=http_status.HTTP_404_NOT_FOUND
            )
        
        # If category is None or empty, clear the category
        if not request.category or not request.category.strip():
            work.category = None
            work.updated_at = datetime.now(timezone.utc)
            db.commit()
            logger.info(f"Admin {current_admin.username} cleared category for work {work_id}")
            return success_response(
                data={"category": None},
                message="Work category cleared successfully"
            )
        
        category = request.category.strip()
        
        # Validate category format and existence
        if "|" in category:
            # Hierarchical category: "Level1|Level2"
            parts = category.split("|", 1)
            if len(parts) != 2:
                return error_response(
                    message="Invalid category format. Expected 'Level1|Level2'",
                    status_code=http_status.HTTP_400_BAD_REQUEST
                )
            
            level1_name = parts[0].strip()
            level2_name = parts[1].strip()
            
            # Check if level 1 category exists
            level1_cat = db.query(CategoryPage).filter(
                CategoryPage.category_name == level1_name,
                CategoryPage.level == 1
            ).first()
            
            if not level1_cat:
                return error_response(
                    message=f"Level 1 category '{level1_name}' does not exist",
                    status_code=http_status.HTTP_400_BAD_REQUEST
                )
            
            # Check if level 2 category exists and is a child of level 1
            level2_cat = db.query(CategoryPage).filter(
                CategoryPage.category_name == level2_name,
                CategoryPage.level == 2,
                CategoryPage.parent_id == level1_cat.id
            ).first()
            
            if not level2_cat:
                return error_response(
                    message=f"Level 2 category '{level2_name}' does not exist under '{level1_name}'",
                    status_code=http_status.HTTP_400_BAD_REQUEST
                )
        else:
            # Single level category: "Level1"
            level1_cat = db.query(CategoryPage).filter(
                CategoryPage.category_name == category,
                CategoryPage.level == 1
            ).first()
            
            if not level1_cat:
                return error_response(
                    message=f"Category '{category}' does not exist",
                    status_code=http_status.HTTP_400_BAD_REQUEST
                )
        
        # Update the work category
        work.category = category
        work.updated_at = datetime.now(timezone.utc)
        
        db.commit()
        
        logger.info(f"Admin {current_admin.username} updated category for work {work_id} to '{category}'")
        
        return success_response(
            data={"category": category},
            message="Work category updated successfully"
        )
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating work category: {str(e)}")
        return error_response(
            message="Failed to update work category",
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.get("/works/categories")
def get_work_categories(
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Get all available categories for works (from CategoryPage).
    Returns hierarchical structure with level 1 and level 2 categories.
    """
    try:
        # Get all level 1 categories
        level1_categories = db.query(CategoryPage).filter(
            CategoryPage.level == 1
        ).order_by(CategoryPage.sort_order, CategoryPage.category_name).all()
        
        categories_data = []
        for level1 in level1_categories:
            # Get all level 2 categories under this level 1
            level2_categories = db.query(CategoryPage).filter(
                CategoryPage.level == 2,
                CategoryPage.parent_id == level1.id
            ).order_by(CategoryPage.sort_order, CategoryPage.category_name).all()
            
            categories_data.append({
                "level1": level1.category_name,
                "level2": [cat.category_name for cat in level2_categories]
            })
        
        return success_response(
            data=categories_data,
            message="Categories retrieved successfully"
        )
        
    except Exception as e:
        logger.error(f"Error getting work categories: {str(e)}")
        return error_response(
            message="Failed to retrieve categories",
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR
        )


class UpdateWorkTitleDescriptionRequest(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    url_slug_suffix: Optional[str] = Field(None, description="URL slug suffix (part after short_code-), e.g., 'middle-aged-light-skinned-man'")
    share_name: Optional[str] = Field(None, description="Share name (H1 title displayed on page)")


class UpdateWorkTagsRequest(BaseModel):
    tags: Optional[List[str]] = Field(None, description="List of tags for the work")


class BatchHideRequest(BaseModel):
    work_ids: Optional[List[int]] = None
    hidden: bool
    select_all: Optional[bool] = False
    filters: Optional[dict] = None


class BatchUpdateWorksRequest(BaseModel):
    work_ids: Optional[List[int]] = None
    status: Optional[str] = None
    share_status: Optional[str] = None
    is_featured: Optional[bool] = None
    hidden: Optional[bool] = None
    category: Optional[str] = None
    is_shared: Optional[bool] = None
    nsfw_status: Optional[str] = None
    is_banned: Optional[bool] = None
    select_all: Optional[bool] = False
    filters: Optional[dict] = None


class BatchDeleteWorksRequest(BaseModel):
    work_ids: Optional[List[int]] = None
    permanent: bool = False
    select_all: Optional[bool] = False
    filters: Optional[dict] = None


@router.put("/works/{work_id}/title-description")
def update_work_title_description(
    work_id: int,
    request: UpdateWorkTitleDescriptionRequest = Body(...),
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Update work title, description, and URL slug suffix (admin only).
    """
    try:
        work = db.query(Work).filter(Work.id == work_id).first()
        
        if not work:
            return error_response(
                message="Work not found",
                status_code=http_status.HTTP_404_NOT_FOUND
            )
        
        # Update title if provided
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
        
        # Update description if provided
        if request.description is not None:
            work.description = request.description
        
        # Update share_name if provided
        if request.share_name is not None:
            work.share_name = request.share_name
        
        # Update URL slug suffix if provided
        if request.url_slug_suffix is not None:
            if not work.short_code:
                return error_response(
                    message="Work does not have a short_code, cannot update URL slug",
                    status_code=http_status.HTTP_400_BAD_REQUEST
                )
            
            from ..utils.url_slug import slugify, extract_short_code_from_slug
            
            # Clean the suffix: remove any leading/trailing hyphens and normalize
            suffix = request.url_slug_suffix.strip().strip('-')
            if suffix:
                # Slugify the suffix to ensure it's URL-safe
                suffix = slugify(suffix, max_length=200)
                new_url_slug = f"{work.short_code}-{suffix}"
            else:
                # If suffix is empty, just use short_code
                new_url_slug = work.short_code
            
            # Check for uniqueness (excluding current work)
            existing_work = db.query(Work).filter(
                Work.url_slug == new_url_slug,
                Work.id != work_id
            ).first()
            
            if existing_work:
                return error_response(
                    message=f"URL slug '{new_url_slug}' already exists for another work",
                    status_code=http_status.HTTP_400_BAD_REQUEST
                )
            
            work.url_slug = new_url_slug
        
        work.updated_at = datetime.now(timezone.utc)
        db.commit()
        
        logger.info(f"Admin {current_admin.username} updated title/description/url_slug for work {work_id}")
        
        return success_response(
            data={
                "id": work.id,
                "title": work.title,
                "description": work.description,
                "share_name": work.share_name,
                "url_slug": work.url_slug
            },
            message="Work title, description, share_name, and URL slug updated successfully"
        )
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating work title/description/url_slug: {str(e)}")
        return error_response(
            message="Failed to update work title, description, and URL slug",
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.put("/works/{work_id}/tags")
def update_work_tags(
    work_id: int,
    request: UpdateWorkTagsRequest = Body(...),
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Update tags for a work (admin only).
    """
    try:
        work = db.query(Work).filter(Work.id == work_id).first()
        
        if not work:
            return error_response(
                message="Work not found",
                status_code=http_status.HTTP_404_NOT_FOUND
            )
        
        # Update tags if provided
        if request.tags is not None:
            # Ensure tags is a list and filter out empty strings
            tags = [tag.strip() for tag in request.tags if tag and tag.strip()]
            work.tags = tags
        
        work.updated_at = datetime.now(timezone.utc)
        db.commit()
        
        logger.info(f"Admin {current_admin.username} updated tags for work {work_id}")
        
        return success_response(
            data={
                "id": work.id,
                "tags": work.tags
            },
            message="Work tags updated successfully"
        )
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating work tags: {str(e)}")
        return error_response(
            message="Failed to update work tags",
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.post("/works/{work_id}/generate-seo")
def generate_work_seo(
    work_id: int,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Generate SEO title, description, tags, and category for a work using Gemini API.
    """
    try:
        from ..services.gemini_service import get_gemini_service
        
        work = db.query(Work).filter(Work.id == work_id).first()
        
        if not work:
            return error_response(
                message="Work not found",
                status_code=http_status.HTTP_404_NOT_FOUND
            )
        
        if not work.prompt:
            return error_response(
                message="Work has no prompt content",
                status_code=http_status.HTTP_400_BAD_REQUEST
            )
        
        # Get all categories
        all_categories = db.query(CategoryPage).all()
        categories_data = [cat.to_dict(include_children=False) for cat in all_categories]
        
        # Generate content using Gemini (pass db session)
        gemini_service = get_gemini_service(db_session=db)
        generated = gemini_service.generate_all(
            prompt_content=work.prompt,
            categories=categories_data
        )
        
        return success_response(
            data=generated,
            message="SEO content generated successfully"
        )
        
    except ValueError as e:
        # API key not configured
        return error_response(
            message=f"Gemini API not configured: {str(e)}. Please configure it in admin panel.",
            status_code=http_status.HTTP_503_SERVICE_UNAVAILABLE
        )
    except Exception as e:
        logger.error(f"Error generating SEO content: {str(e)}")
        return error_response(
            message=f"Failed to generate SEO content: {str(e)}",
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.post("/works/{work_id}/apply-generated-seo")
def apply_generated_seo(
    work_id: int,
    request: dict = Body(...),
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Apply generated SEO content to a work.
    """
    try:
        work = db.query(Work).filter(Work.id == work_id).first()
        
        if not work:
            return error_response(
                message="Work not found",
                status_code=http_status.HTTP_404_NOT_FOUND
            )
        
        # Update fields if provided
        if "title" in request and request["title"] is not None:
            work.title = request["title"][:200]  # Enforce max length
            # Update canonical_url if storage_key exists
            if work.storage_key:
                from ..services.storage import get_storage_service
                storage = get_storage_service()
                # Check if it's a video type
                is_video = work.type in ["text-to-video", "image-to-video"] or "video" in work.type.lower()
                file_ext = "mp4" if is_video else "jpg"
                work.canonical_url = storage.generate_canonical_url(work.storage_key, work.title, file_ext)
        
        if "description" in request and request["description"] is not None:
            work.description = request["description"]
        
        if "tags" in request and request["tags"] is not None:
            work.tags = request["tags"]
        
        if "category" in request and request["category"] is not None:
            # Validate category exists
            category = request["category"].strip()
            
            if "|" in category:
                parts = category.split("|", 1)
                level1_name = parts[0].strip()
                level2_name = parts[1].strip()
                
                level1_cat = db.query(CategoryPage).filter(
                    CategoryPage.category_name == level1_name,
                    CategoryPage.level == 1
                ).first()
                
                if level1_cat:
                    level2_cat = db.query(CategoryPage).filter(
                        CategoryPage.category_name == level2_name,
                        CategoryPage.level == 2,
                        CategoryPage.parent_id == level1_cat.id
                    ).first()
                    
                    if level2_cat:
                        work.category = category
            else:
                level1_cat = db.query(CategoryPage).filter(
                    CategoryPage.category_name == category,
                    CategoryPage.level == 1
                ).first()
                
                if level1_cat:
                    work.category = category
        
        work.updated_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(work)
        
        logger.info(f"Admin {current_admin.username} applied generated SEO to work {work_id}")
        
        return success_response(
            data={
                "title": work.title,
                "description": work.description,
                "tags": work.tags,
                "category": work.category
            },
            message="SEO content applied successfully"
        )
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error applying SEO content: {str(e)}")
        return error_response(
            message="Failed to apply SEO content",
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.post("/works/{work_id}/block-nsfw")
def block_work_nsfw(
    work_id: int,
    request: dict = Body(...),
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Block a work by setting NSFW status to BLOCKED.
    Creates moderation log and sends notification to user.
    """
    try:
        work = db.query(Work).filter(Work.id == work_id).first()
        
        if not work:
            return error_response(
                message="Work not found",
                status_code=http_status.HTTP_404_NOT_FOUND
            )
        
        if work.deleted_at:
            return error_response(
                message="Cannot block a deleted work",
                status_code=http_status.HTTP_400_BAD_REQUEST
            )
        
        block_reason = request.get('reason', '') or "Work blocked by admin"
        from ..utils.validation import validate_reason_english
        valid, err = validate_reason_english(block_reason)
        if not valid:
            return error_response(message=err or "Invalid reason", status_code=400)
        
        # Update NSFW status
        work.nsfw_status = NSFWStatus.BLOCKED.value
        work.updated_at = datetime.now(timezone.utc)
        
        # Create moderation log
        from ..models.moderation import ModerationLog, ModerationType, ModerationAction
        log = ModerationLog(
            work_id=work_id,
            moderation_type=ModerationType.NSFW,
            action_type=ModerationAction.MANUAL_REJECTED,
            moderator_id=current_admin.id,
            nsfw_tags=work.nsfw_tags,
            reason=block_reason
        )
        db.add(log)
        
        db.commit()
        
        # Send notification to user
        from ..utils.notification import create_notification
        from ..models.notification import NotificationType
        
        # Build notification content in English
        tags_label = ""
        if work.nsfw_tags:
            tag_labels = {
                "VIOLENCE": "violence",
                "PORNOGRAPHY": "pornography",
                "ILLEGAL": "illegal activity",
                "OTHER": "other"
            }
            tags_list = [tag_labels.get(tag, tag.lower()) for tag in work.nsfw_tags]
            tags_label = ", detected tags: " + ", ".join(tags_list)
        
        work_title = work.share_name or work.title or 'Untitled'
        content = f"Your work '{work_title}' has been blocked by an administrator."
        if tags_label:
            content += tags_label
        if block_reason:
            content += f"\nReason: {block_reason}"
        content += "\nThis work will not be publicly displayed."
        
        # Send notification to user
        notification = create_notification(
            db=db,
            user_id=work.user_id,
            type=NotificationType.NSFW_BLOCKED,
            title="Work Blocked ⚠️",
            content=content,
            link_url=None
        )
        
        if notification:
            logger.info(f"Admin {current_admin.username} blocked work {work_id} (NSFW): {block_reason}. Notification sent to user {work.user_id}")
        else:
            logger.warning(f"Admin {current_admin.username} blocked work {work_id} (NSFW): {block_reason}. Failed to send notification to user {work.user_id}")
        
        return success_response(
            data={"work_id": work_id, "nsfw_status": work.nsfw_status},
            message="Work blocked successfully"
        )
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error blocking work NSFW: {str(e)}")
        return error_response(
            message=f"Failed to block work: {str(e)}",
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.post("/works/batch-update")
def batch_update_works(
    request: BatchUpdateWorksRequest = Body(...),
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Batch update multiple works.
    Supports either a list of IDs or selecting all matching works via filters.
    """
    try:
        update_data = {}
        if request.status is not None:
            try:
                update_data[Work.status] = WorkStatus(request.status)
            except ValueError:
                pass
        if request.share_status is not None:
            try:
                update_data[Work.share_status] = ShareStatus(request.share_status)
            except ValueError:
                pass
        if request.is_featured is not None:
            update_data[Work.is_featured] = request.is_featured
        if request.hidden is not None:
            update_data[Work.hidden] = request.hidden
        if request.category is not None:
            update_data[Work.category] = request.category if request.category else None
        if request.is_shared is not None:
            update_data[Work.is_shared] = request.is_shared
        if request.nsfw_status is not None:
            update_data[Work.nsfw_status] = request.nsfw_status
        if request.is_banned is not None:
            update_data[Work.is_banned] = request.is_banned
            # Clear ban_reason when unbanning, set default reason when banning
            if request.is_banned:
                update_data[Work.ban_reason] = ""
            else:
                update_data[Work.ban_reason] = None
        
        if not update_data:
            return error_response(message="No update data provided", status_code=400)
            
        update_data[Work.updated_at] = datetime.now(timezone.utc)

        # Get work IDs to update for notifications
        work_ids_to_notify = []
        if request.select_all:
            query = db.query(Work)
            if request.filters:
                query = apply_work_filters(
                    query,
                    search=request.filters.get('search'),
                    author_search=request.filters.get('author_search'),
                    status=request.filters.get('status'),
                    share_status=request.filters.get('share_status'),
                    nsfw_status=request.filters.get('nsfw_status'),
                    is_banned=request.filters.get('is_banned'),
                    is_deleted=request.filters.get('is_deleted'),
                    is_featured=request.filters.get('is_featured'),
                    hidden=request.filters.get('hidden'),
                    category=request.filters.get('category'),
                    user_id=request.filters.get('user_id'),
                    work_type=request.filters.get('work_type'),
                    model_name=request.filters.get('model_name'),
                    is_shared=request.filters.get('is_shared'),
                    work_id=request.filters.get('work_id'),
                    date_from=request.filters.get('date_from'),
                    date_to=request.filters.get('date_to')
                )
            # Get work IDs before update for notifications
            if request.is_shared is not None or request.is_featured is not None:
                work_ids_to_notify = [w.id for w in query.all()]
            affected_count = query.update(update_data, synchronize_session=False)
        else:
            if not request.work_ids:
                return error_response(message="No work IDs provided", status_code=400)
            # Get work IDs for notifications
            if request.is_shared is not None or request.is_featured is not None:
                work_ids_to_notify = request.work_ids
            affected_count = db.query(Work).filter(Work.id.in_(request.work_ids)).update(
                update_data, synchronize_session=False
            )
        
        db.commit()
        
        # Send notifications for visibility and featured changes
        if work_ids_to_notify and (request.is_shared is not None or request.is_featured is not None):
            from ..utils.notification import create_notification
            from ..models.notification import NotificationType
            
            # Get updated works after commit
            works_to_notify = db.query(Work).filter(Work.id.in_(work_ids_to_notify)).all()
            
            notification_count = 0
            for work in works_to_notify:
                # Send notification for visibility change
                if request.is_shared is not None:
                    status_text = "public 👁️" if work.is_shared else "private 🔒"
                    create_notification(
                        db=db,
                        user_id=work.user_id,
                        type=NotificationType.SYSTEM,
                        title="Work Visibility Updated",
                        content=f"An administrator has set your work '{work.share_name or work.title}' to {status_text}.",
                        link_url=f"/prompt/{work.url_slug or work.short_code}" if work.url_slug or work.short_code else None
                    )
                    notification_count += 1
                
                # Send notification for featured change (only when set to featured)
                if request.is_featured is not None and work.is_featured:
                    create_notification(
                        db=db,
                        user_id=work.user_id,
                        type=NotificationType.FEATURED,
                        title="Your work is featured! ⭐",
                        content=f"Congratulations! Your work '{work.share_name or work.title}' has been featured on the homepage.",
                        link_url=f"/prompt/{work.url_slug or work.short_code}" if work.url_slug or work.short_code else None
                    )
                    notification_count += 1
            
            if notification_count > 0:
                db.commit()
                logger.info(f"Admin {current_admin.username} batch updated {affected_count} works and sent {notification_count} notifications")
            else:
                logger.info(f"Admin {current_admin.username} batch updated {affected_count} works")
        else:
            logger.info(f"Admin {current_admin.username} batch updated {affected_count} works")
        
        return success_response(message=f"Successfully updated {affected_count} works")
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error in batch update works: {str(e)}")
        return error_response(message=f"Failed to update works: {str(e)}", status_code=500)


@router.post("/works/batch-delete")
def batch_delete_works(
    request: BatchDeleteWorksRequest = Body(...),
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Batch delete multiple works (soft or permanent).
    """
    try:
        if request.permanent:
            work_ids = []
            if request.select_all:
                query = db.query(Work.id)
                if request.filters:
                    query = apply_work_filters(
                        query,
                        search=request.filters.get('search'),
                        author_search=request.filters.get('author_search'),
                        status=request.filters.get('status'),
                        share_status=request.filters.get('share_status'),
                        nsfw_status=request.filters.get('nsfw_status'),
                        is_banned=request.filters.get('is_banned'),
                        is_deleted=request.filters.get('is_deleted'),
                        is_featured=request.filters.get('is_featured'),
                        hidden=request.filters.get('hidden'),
                        category=request.filters.get('category'),
                        user_id=request.filters.get('user_id'),
                        work_type=request.filters.get('work_type'),
                        model_name=request.filters.get('model_name'),
                        is_shared=request.filters.get('is_shared'),
                        work_id=request.filters.get('work_id'),
                        date_from=request.filters.get('date_from'),
                        date_to=request.filters.get('date_to')
                    )
                work_ids = [r[0] for r in query.all()]
            else:
                work_ids = request.work_ids or []

            if not work_ids:
                return error_response(message="No works found to delete", status_code=400)

            success_count = 0
            for wid in work_ids:
                try:
                    work = db.query(Work).filter(Work.id == wid).first()
                    if work:
                        storage = get_storage_service()
                        file_key = extract_storage_key_from_url(work.file_url)
                        if file_key:
                            storage.delete_file(file_key)
                        thumb_key = extract_storage_key_from_url(work.thumbnail_url)
                        if thumb_key and thumb_key != file_key:
                            storage.delete_file(thumb_key)
                        
                        from ..models.moderation import ModerationLog
                        db.query(ModerationLog).filter(ModerationLog.work_id == wid).delete(synchronize_session=False)
                        db.delete(work)
                        success_count += 1
                except Exception as ex:
                    logger.error(f"Failed to permanently delete work {wid}: {str(ex)}")
            
            db.commit()
            return success_response(message=f"Successfully permanently deleted {success_count} works and their files")
            
        else:
            update_data = {
                Work.deleted_at: datetime.now(timezone.utc),
                Work.updated_at: datetime.now(timezone.utc)
            }
            
            if request.select_all:
                query = db.query(Work)
                if request.filters:
                    query = apply_work_filters(
                        query,
                        search=request.filters.get('search'),
                        author_search=request.filters.get('author_search'),
                        status=request.filters.get('status'),
                        share_status=request.filters.get('share_status'),
                        nsfw_status=request.filters.get('nsfw_status'),
                        is_banned=request.filters.get('is_banned'),
                        is_deleted=request.filters.get('is_deleted'),
                        is_featured=request.filters.get('is_featured'),
                        hidden=request.filters.get('hidden'),
                        category=request.filters.get('category'),
                        user_id=request.filters.get('user_id'),
                        work_type=request.filters.get('work_type'),
                        model_name=request.filters.get('model_name'),
                        is_shared=request.filters.get('is_shared'),
                        work_id=request.filters.get('work_id'),
                        date_from=request.filters.get('date_from'),
                        date_to=request.filters.get('date_to')
                    )
                affected_count = query.filter(Work.deleted_at == None).update(update_data, synchronize_session=False)
            else:
                if not request.work_ids:
                    return error_response(message="No work IDs provided", status_code=400)
                affected_count = db.query(Work).filter(
                    Work.id.in_(request.work_ids),
                    Work.deleted_at == None
                ).update(update_data, synchronize_session=False)
                
            db.commit()
            logger.info(f"Admin {current_admin.username} batch soft-deleted {affected_count} works")
            return success_response(message=f"Successfully soft-deleted {affected_count} works")
            
    except Exception as e:
        db.rollback()
        logger.error(f"Error in batch delete works: {str(e)}")
        return error_response(message=f"Failed to delete works: {str(e)}", status_code=500)


@router.post("/works/batch-hide")
def batch_hide_works(
    request: BatchHideRequest = Body(...),
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Batch hide or unhide works.
    Supports either a list of IDs or selecting all matching works via filters.
    """
    try:
        if request.select_all:
            # Apply filters to find all matching works
            query = db.query(Work)
            if request.filters:
                query = apply_work_filters(
                    query,
                    search=request.filters.get('search'),
                    author_search=request.filters.get('author_search'),
                    status=request.filters.get('status'),
                    share_status=request.filters.get('share_status'),
                    nsfw_status=request.filters.get('nsfw_status'),
                    is_banned=request.filters.get('is_banned'),
                    is_deleted=request.filters.get('is_deleted'),
                    is_featured=request.filters.get('is_featured'),
                    hidden=request.filters.get('hidden'),
                    category=request.filters.get('category'),
                    user_id=request.filters.get('user_id'),
                    work_type=request.filters.get('work_type'),
                    model_name=request.filters.get('model_name'),
                    is_shared=request.filters.get('is_shared'),
                    work_id=request.filters.get('work_id'),
                    date_from=request.filters.get('date_from'),
                    date_to=request.filters.get('date_to')
                )
            
            # Perform update
            affected_count = query.update(
                {Work.hidden: request.hidden, Work.updated_at: datetime.now(timezone.utc)},
                synchronize_session=False
            )
        else:
            if not request.work_ids:
                return error_response(
                    message="No work IDs provided",
                    status_code=http_status.HTTP_400_BAD_REQUEST
                )
                
            # Update specific works
            affected_count = db.query(Work).filter(Work.id.in_(request.work_ids)).update(
                {Work.hidden: request.hidden, Work.updated_at: datetime.now(timezone.utc)},
                synchronize_session=False
            )
        
        db.commit()
        
        action = "hidden" if request.hidden else "shown"
        logger.info(f"Admin {current_admin.username} batch set {affected_count} works to {action}")
        
        return success_response(
            message=f"Successfully {action} {affected_count} works"
        )
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error in batch hide works: {str(e)}")
        return error_response(
            message="Failed to update works",
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR
        )
