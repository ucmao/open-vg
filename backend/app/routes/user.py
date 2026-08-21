from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from datetime import datetime, timedelta, timezone
from typing import List, Optional

from ..models.base import get_db
from ..models.user import User
from ..models.work import Work, WorkStatus, ShareStatus, WorkType
from ..models.credit_record import CreditRecord
from ..models.favorite import Favorite
from ..models.like import Like
from ..models.follow import Follow
from ..models.schemas import UserResponse, UpdateProfileRequest, CreditRecordResponse, WorkResponse
from ..utils.auth import get_current_active_user, get_current_user_optional
from ..utils.responses import success_response, error_response, paginated_response
from ..utils.logger import logger
from ..utils.handle import validate_handle

router = APIRouter()


@router.get("/space/{handle}")
def get_user_public_space(
    handle: str,
    page: int = 1,
    page_size: int = 20,
    sort: str = "newest",
    work_type: str = "all", # all, image, video
    search: Optional[str] = None,
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """
    Get a user's public space info and their shared works.
    Sort options: newest, most_liked, most_viewed, most_commented
    """
    try:
        # Find user (case-insensitive)
        target_user = db.query(User).filter(func.lower(User.handle) == handle.lower()).first()
        if not target_user:
            return error_response(message="User not found", status_code=status.HTTP_404_NOT_FOUND)

        # Import NSFWStatus for filtering
        from ..models.moderation import NSFWStatus
        
        # Base filters for public works
        base_filters = [
            Work.user_id == target_user.id,
            Work.is_shared == True,
            Work.status == WorkStatus.SUCCESS,
            Work.share_status == ShareStatus.APPROVED,
            Work.deleted_at == None,
            Work.hidden == False,  # Exclude hidden works
            # NSFW status check: only show approved or null (for backward compatibility)
            or_(
                Work.nsfw_status == NSFWStatus.APPROVED.value,
                Work.nsfw_status == None  # Old works without NSFW status
            )
        ]
        
        # Work type filter
        if work_type == "image":
            base_filters.append(Work.type.in_([WorkType.TEXT2IMG, WorkType.IMG2IMG]))
        elif work_type == "video":
            base_filters.append(Work.type.in_([WorkType.TEXT2VIDEO, WorkType.IMG2VIDEO]))
            
        # Search filter
        if search:
            search_query = f"%{search}%"
            base_filters.append(or_(
                Work.prompt.ilike(search_query),
                Work.share_name.ilike(search_query),
                Work.title.ilike(search_query)
            ))

        # Get total count of shared works and aggregate statistics
        query = db.query(Work).filter(and_(*base_filters))
        total = query.count()
        
        # Calculate aggregate statistics: total views, likes, favorites (always for all shared works)
        stats = db.query(
            func.sum(Work.view_count).label('total_views'),
            func.sum(Work.like_count).label('total_likes'),
            func.sum(Work.favorite_count).label('total_favorites')
        ).filter(
            and_(
                Work.user_id == target_user.id,
                Work.is_shared == True,
                Work.status == WorkStatus.SUCCESS,
                Work.share_status == ShareStatus.APPROVED,
                Work.deleted_at == None,
                Work.hidden == False,  # Exclude hidden works
                # NSFW status check: only show approved or null (for backward compatibility)
                or_(
                    Work.nsfw_status == NSFWStatus.APPROVED.value,
                    Work.nsfw_status == None  # Old works without NSFW status
                )
            )
        ).first()

        # Count total remixes of this user's works
        user_work_ids = db.query(Work.id).filter(
            Work.user_id == target_user.id,
            Work.deleted_at == None
        ).subquery()
        total_remixes = db.query(func.count(Work.id)).filter(
            and_(
                Work.parent_id.in_(user_work_ids),
                Work.status == WorkStatus.SUCCESS,
                Work.is_shared == True,
                Work.share_status == ShareStatus.APPROVED,
                Work.deleted_at == None,
                Work.hidden == False,  # Exclude hidden works
                # NSFW status check: only show approved or null (for backward compatibility)
                or_(
                    Work.nsfw_status == NSFWStatus.APPROVED.value,
                    Work.nsfw_status == None  # Old works without NSFW status
                )
            )
        ).scalar() or 0
        
        total_views = int(stats.total_views or 0)
        total_likes = int(stats.total_likes or 0)
        total_favorites = int(stats.total_favorites or 0)

        # Get follow counts
        followers_count = db.query(Follow).filter(Follow.following_id == target_user.id).count()
        following_count = db.query(Follow).filter(Follow.follower_id == target_user.id).count()
        
        # Check if current user is following target user
        is_following = False
        if current_user:
            is_following = db.query(Follow).filter(
                Follow.follower_id == current_user.id,
                Follow.following_id == target_user.id
            ).first() is not None

        # Apply sorting
        from sqlalchemy import desc
        from ..models.comment import Comment
        
        if sort == "most_liked":
            works = query.order_by(desc(Work.like_count)).offset((page - 1) * page_size).limit(page_size).all()
        elif sort == "most_viewed":
            works = query.order_by(desc(Work.view_count)).offset((page - 1) * page_size).limit(page_size).all()
        elif sort == "most_favorited":
            works = query.order_by(desc(Work.favorite_count)).offset((page - 1) * page_size).limit(page_size).all()
        elif sort == "most_commented":
            works = db.query(Work).outerjoin(Comment, Comment.work_id == Work.id).filter(
                and_(*base_filters)
            ).group_by(Work.id).order_by(desc(func.count(Comment.id))).offset((page - 1) * page_size).limit(page_size).all()
        else:  # newest (default)
            works = query.order_by(desc(Work.created_at)).offset((page - 1) * page_size).limit(page_size).all()

        # Batch prefetch auxiliary data to avoid N+1 queries
        from ..models.work import batch_prefetch_work_data
        current_user_id = current_user.id if current_user else None
        prefetched = batch_prefetch_work_data(works, db, current_user_id)
        
        items = [
            work.to_dict(
                include_user=True, 
                include_prompt=True, 
                current_user_id=current_user_id, 
                db=db,
                prefetched_counts=prefetched['counts'],
                prefetched_likes=prefetched['liked_work_ids'],
                prefetched_follows=prefetched['following_user_ids']
            ) for work in works
        ]

        return success_response(
            data={
                "user": {
                    "nickname": target_user.nickname,
                    "avatar_url": target_user.avatar_url,
                    "bio": target_user.bio,
                    "handle": target_user.handle,
                    "location": target_user.location,
                    "gender": target_user.gender.value if target_user.gender else None,
                    "instagram_handle": target_user.instagram_handle,
                    "twitter_handle": target_user.twitter_handle,
                    "discord_handle": target_user.discord_handle,
                    "created_at": target_user.created_at.isoformat()
                },
                "works": items,
                "total": total,
                "stats": {
                    "total_views": total_views,
                    "total_likes": total_likes,
                    "total_favorites": total_favorites,
                    "total_remixes": total_remixes,
                    "followers_count": followers_count,
                    "following_count": following_count,
                    "is_following": is_following
                },
                "page": page,
                "page_size": page_size
            },
            message="User space retrieved"
        )
    except Exception as e:
        logger.error(f"Error getting user space: {str(e)}")
        return error_response(message="An error occurred")


@router.get("/activity")
def activity_heartbeat(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Lightweight heartbeat: updates last_login for active user.
    Frontend calls this periodically (e.g. every 5–10 min) when the user has a token
    and the tab is in focus, so "active users" and "current online" reflect real usage.
    """
    try:
        current_user.last_login = datetime.now(timezone.utc)
        from ..utils.activity import record_user_activity
        record_user_activity(current_user.id, db)
        db.commit()
        return success_response(message="OK")
    except Exception as e:
        logger.error(f"Activity heartbeat error: {str(e)}")
        return error_response(message="An error occurred", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@router.get("/profile")
def get_profile(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get current user profile.
    """
    try:
        return success_response(
            data=current_user.to_dict(db=db),
            message="Profile retrieved successfully"
        )
        
    except Exception as e:
        logger.error(f"Error getting profile: {str(e)}")
        return error_response(
            message="An error occurred while retrieving profile",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.put("/profile")
def update_profile(
    request: UpdateProfileRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Update user profile information.
    """
    try:
        if request.nickname:
            current_user.nickname = request.nickname
        
        if request.handle and request.handle.lower() != current_user.handle.lower():
            # Check if user can change handle (90-day restriction)
            if current_user.handle_updated_at:
                now = datetime.now(timezone.utc)
                days_since_last_change = (now - current_user.handle_updated_at).days
                if days_since_last_change < 90:
                    days_remaining = 90 - days_since_last_change
                    return error_response(
                        message=f"You can only change your handle once every 3 months. Please wait {days_remaining} more days.",
                        status_code=status.HTTP_400_BAD_REQUEST
                    )
            
            # Validate new handle
            is_valid, error_msg = validate_handle(request.handle, db, exclude_user_id=current_user.id)
            if not is_valid:
                return error_response(
                    message=error_msg,
                    status_code=status.HTTP_400_BAD_REQUEST
                )
            current_user.handle = request.handle
            current_user.handle_updated_at = datetime.now(timezone.utc)
        
        if request.avatar_url is not None:
            current_user.avatar_url = request.avatar_url
        
        if request.bio is not None:
            current_user.bio = request.bio
        
        if request.instagram_handle is not None:
            current_user.instagram_handle = request.instagram_handle
            
        if request.twitter_handle is not None:
            current_user.twitter_handle = request.twitter_handle
            
        if request.discord_handle is not None:
            current_user.discord_handle = request.discord_handle
        
        if request.location is not None:
            current_user.location = request.location
        
        if request.gender is not None:
            from app.models.user import Gender
            current_user.gender = Gender(request.gender) if request.gender else None
        
        db.commit()
        db.refresh(current_user)
        
        logger.info(f"User profile updated: {current_user.id}")
        
        return success_response(
            data=current_user.to_dict(db=db),
            message="Profile updated successfully"
        )
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating profile: {str(e)}")
        return error_response(
            message="An error occurred while updating profile",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.get("/credits")
def get_credits(
    page: int = 1,
    page_size: int = 20,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get user's credit transaction history with pagination.
    """
    try:
        # Get total count
        total = db.query(CreditRecord).filter(
            CreditRecord.user_id == current_user.id
        ).count()
        
        # Get paginated records
        records = db.query(CreditRecord).filter(
            CreditRecord.user_id == current_user.id
        ).order_by(
            CreditRecord.created_at.desc()
        ).offset((page - 1) * page_size).limit(page_size).all()
        
        items = [record.to_dict() for record in records]
        
        return paginated_response(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            message="Credits retrieved successfully"
        )
        
    except Exception as e:
        logger.error(f"Error getting credits: {str(e)}")
        return error_response(
            message="An error occurred while retrieving credits",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.get("/works")
def get_user_works(
    page: int = 1,
    page_size: int = 20,
    privacy: str = "all",  # all, public, private
    work_type: str = "all", # all, image, video
    search: Optional[str] = None,
    status: Optional[str] = None,  # all, success, generating, processing, failed
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get user's own works (including non-shared ones).
    Filter out expired works (30 days old and not shared).
    """
    try:
        # Calculate expiration date (30 days ago)
        expiry_date = datetime.now(timezone.utc) - timedelta(days=30)
        
        # Base filters
        filters = [
            Work.user_id == current_user.id,
            Work.deleted_at == None,
        ]
        
        # Status filter: if not specified or "all", include all statuses
        # For generating/processing works, don't apply expiry filter
        if status and status != "all":
            if status == "success":
                filters.append(Work.status == WorkStatus.SUCCESS)
                # For success works, apply expiry filter
                filters.append(
                    or_(
                        Work.is_shared == True,
                        Work.created_at > expiry_date
                    )
                )
            elif status == "generating":
                filters.append(Work.status == WorkStatus.GENERATING)
            elif status == "processing":
                filters.append(Work.status == WorkStatus.PROCESSING)
            elif status == "failed":
                filters.append(Work.status == WorkStatus.FAILED)
        else:
            # If status is "all" or not specified, include all statuses
            # For success works, apply expiry filter; for others, don't
            status_filter = or_(
                and_(
                    Work.status == WorkStatus.SUCCESS,
                    or_(
                        Work.is_shared == True,
                        Work.created_at > expiry_date
                    )
                ),
                Work.status.in_([WorkStatus.GENERATING, WorkStatus.PROCESSING, WorkStatus.FAILED])
            )
            filters.append(status_filter)
        
        # Privacy filter
        if privacy == "public":
            filters.append(Work.is_shared == True)
        elif privacy == "private":
            filters.append(Work.is_shared == False)
            
        # Work type filter
        if work_type == "image":
            filters.append(Work.type.in_([WorkType.TEXT2IMG, WorkType.IMG2IMG]))
        elif work_type == "video":
            filters.append(Work.type.in_([WorkType.TEXT2VIDEO, WorkType.IMG2VIDEO]))
            
        # Search filter
        if search:
            search_query = f"%{search}%"
            filters.append(or_(
                Work.prompt.ilike(search_query),
                Work.share_name.ilike(search_query),
                Work.title.ilike(search_query)
            ))
            
        # Get total count
        total = db.query(Work).filter(and_(*filters)).count()
        
        # Get paginated works
        works = db.query(Work).filter(
            and_(*filters)
        ).order_by(
            Work.created_at.desc()
        ).offset((page - 1) * page_size).limit(page_size).all()
        
        # Batch prefetch auxiliary data to avoid N+1 queries
        from ..models.work import batch_prefetch_work_data
        prefetched = batch_prefetch_work_data(works, db, current_user.id)
        
        items = [
            work.to_dict(
                include_prompt=True, 
                current_user_id=current_user.id, 
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
        logger.error(f"Error getting user works: {str(e)}")
        return error_response(
            message="An error occurred while retrieving works",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.get("/favorites")
def get_favorites(
    page: int = 1,
    page_size: int = 20,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get user's favorited works.
    """
    try:
        # Get total count
        total = db.query(Favorite).filter(
            Favorite.user_id == current_user.id
        ).count()
        
        # Get paginated favorites with work details
        favorites = db.query(Favorite).filter(
            Favorite.user_id == current_user.id
        ).order_by(
            Favorite.created_at.desc()
        ).offset((page - 1) * page_size).limit(page_size).all()
        
        # Extract works and batch prefetch
        works = [f.work for f in favorites if f.work]
        from ..models.work import batch_prefetch_work_data
        prefetched = batch_prefetch_work_data(works, db, current_user.id)
        
        items = []
        for favorite in favorites:
            if favorite.work:
                work_dict = favorite.work.to_dict(
                    include_user=True, 
                    include_prompt=True, 
                    current_user_id=current_user.id, 
                    db=db,
                    prefetched_counts=prefetched['counts'],
                    prefetched_likes=prefetched['liked_work_ids'],
                    prefetched_follows=prefetched['following_user_ids']
                )
                work_dict['favorited_at'] = favorite.created_at.isoformat()
                items.append(work_dict)
        
        return paginated_response(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            message="Favorites retrieved successfully"
        )
        
    except Exception as e:
        logger.error(f"Error getting favorites: {str(e)}")
        return error_response(
            message="An error occurred while retrieving favorites",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.get("/likes")
def get_likes(
    page: int = 1,
    page_size: int = 20,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get works liked by current user.
    """
    try:
        # Get total count
        total = db.query(Like).filter(
            Like.user_id == current_user.id
        ).count()
        
        # Get paginated likes with work details
        likes = db.query(Like).filter(
            Like.user_id == current_user.id
        ).order_by(
            Like.created_at.desc()
        ).offset((page - 1) * page_size).limit(page_size).all()
        
        # Extract works and batch prefetch
        works = [like.work for like in likes if like.work]
        from ..models.work import batch_prefetch_work_data
        prefetched = batch_prefetch_work_data(works, db, current_user.id)
        
        items = []
        for like in likes:
            if like.work:
                work_dict = like.work.to_dict(
                    include_user=True, 
                    include_prompt=True, 
                    current_user_id=current_user.id, 
                    db=db,
                    prefetched_counts=prefetched['counts'],
                    prefetched_likes=prefetched['liked_work_ids'],
                    prefetched_follows=prefetched['following_user_ids']
                )
                work_dict['liked_at'] = like.created_at.isoformat()
                items.append(work_dict)
        
        return paginated_response(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            message="Likes retrieved successfully"
        )
        
    except Exception as e:
        logger.error(f"Error getting likes: {str(e)}")
        return error_response(
            message="An error occurred while retrieving likes",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

