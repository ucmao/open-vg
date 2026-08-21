"""
Admin routes for managing users.
"""
from datetime import datetime
from fastapi import APIRouter, Depends, Query, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, func
from typing import Optional

from ..models.base import get_db
from ..models.admin import Admin
from ..models.user import User
from ..models.notification import NotificationType
from ..utils.auth import get_current_admin
from ..utils.responses import success_response, error_response, paginated_response
from ..utils.logger import logger
from ..utils.notification import create_notification
from ..utils.validation import validate_reason_english

router = APIRouter()


class ToggleUserStatusRequest(BaseModel):
    reason: Optional[str] = None  # Optional reason for the status change


@router.get("/users")
def get_all_users(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search_id: Optional[str] = Query(None, description="Search by user ID (exact match)"),
    search_nickname: Optional[str] = Query(None, description="Search by nickname (fuzzy)"),
    search_handle: Optional[str] = Query(None, description="Search by handle (fuzzy)"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    source: Optional[str] = Query(None, description="Filter by customer source: REAL or VIRTUAL"),
    registration_method: Optional[str] = Query(None, description="Filter by registration method: REGISTER, GOOGLE, ADMIN_CREATED, IMPORT"),
    created_after: Optional[str] = Query(None, description="Filter by registration time range start (ISO datetime)"),
    created_before: Optional[str] = Query(None, description="Filter by registration time range end (ISO datetime)"),
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Get all users with search and pagination.
    """
    try:
        # Debug logging
        logger.info(f"Get users - page: {page}, page_size: {page_size}, search_id: {search_id}, search_nickname: {search_nickname}, search_handle: {search_handle}, is_active: {is_active}, source: {source}, registration_method: {registration_method}, created_after: {created_after}, created_before: {created_before}")
        
        query = db.query(User)
        
        filters = []
        if search_id:
            try:
                uid = int(search_id.strip())
                filters.append(User.id == uid)
            except ValueError:
                pass
        if search_nickname:
            filters.append(User.nickname.ilike(f"%{search_nickname.strip()}%"))
        if search_handle:
            filters.append(User.handle.ilike(f"%{search_handle.strip()}%"))
            
        if is_active is not None:
            filters.append(User.is_active == is_active)

        if registration_method or source:
            from ..models.user import UserSource
        if registration_method:
            # Exact registration method ()
            try:
                method_enum = UserSource(registration_method.upper())
                filters.append(User.source == method_enum)
                logger.info(f"Adding registration_method filter: {registration_method} -> {method_enum}")
            except ValueError:
                logger.warning(f"Invalid registration_method: {registration_method}")
        elif source:
            source_upper = source.upper()
            # Handle special source types: REAL (email + google) and VIRTUAL (admin + import)
            if source_upper == 'REAL':
                # Real users: REGISTER (email) and GOOGLE
                filters.append(User.source.in_([UserSource.REGISTER, UserSource.GOOGLE]))
                logger.info(f"Adding source filter: REAL -> REGISTER, GOOGLE")
            elif source_upper == 'VIRTUAL':
                # Virtual users: ADMIN_CREATED and IMPORT
                filters.append(User.source.in_([UserSource.ADMIN_CREATED, UserSource.IMPORT]))
                logger.info(f"Adding source filter: VIRTUAL -> ADMIN_CREATED, IMPORT")
            else:
                # Try to match as a direct UserSource enum value
                try:
                    source_enum = UserSource(source_upper)
                    filters.append(User.source == source_enum)
                    logger.info(f"Adding source filter: {source} -> {source_enum}")
                except ValueError:
                    logger.warning(f"Invalid source value: {source}")
                    pass

        # Registration time range ()
        if created_after:
            try:
                # Parse ISO format (e.g. 2025-02-05T06:00:00.000Z)
                dt = datetime.fromisoformat(created_after.replace("Z", "+00:00"))
                filters.append(User.created_at >= dt)
            except (ValueError, TypeError):
                logger.warning(f"Invalid created_after: {created_after}")
        if created_before:
            try:
                dt = datetime.fromisoformat(created_before.replace("Z", "+00:00"))
                filters.append(User.created_at <= dt)
            except (ValueError, TypeError):
                logger.warning(f"Invalid created_before: {created_before}")
            
        if filters:
            query = query.filter(and_(*filters))
            
        total = query.count()
        
        users = query.order_by(User.id.desc()).offset((page - 1) * page_size).limit(page_size).all()
        
        # Format user data with some stats
        items = []
        for user in users:
            user_dict = user.to_dict(db=db)
            items.append(user_dict)
            
        return paginated_response(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            message="Users retrieved successfully"
        )
    except Exception as e:
        logger.error(f"Error getting users: {str(e)}")
        return error_response(message="Failed to retrieve users", status_code=500)

@router.get("/users/search")
def search_users(
    query: str = Query(..., min_length=1, description="Search query for users"),
    limit: int = Query(10, ge=1, le=50),
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Search users by nickname, email, or handle.
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
        
        user_list = []
        for user in users:
            # Debug logging
            logger.info(f"User {user.id} ({user.email}) total_credits: {user.total_credits}, type: {type(user.total_credits)}")
            user_dict = {
                "id": user.id,
                "nickname": user.nickname,
                "email": user.email,
                "handle": user.handle,
                "avatar_url": user.avatar_url,
                "total_credits": user.total_credits if user.total_credits is not None else 0
            }
            user_list.append(user_dict)
        
        logger.info(f"Returning {len(user_list)} users")
        return success_response(
            data=user_list,
            message="Users found"
        )
    except Exception as e:
        logger.error(f"Error searching users: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return error_response(message="Failed to search users", status_code=500)


@router.get("/users/{user_id}")
def get_user_by_id(
    user_id: int,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Get a single user by ID.
    """
    try:
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user:
            return error_response(
                message="User not found",
                status_code=status.HTTP_404_NOT_FOUND
            )
        
        user_dict = user.to_dict(db=db)
        
        return success_response(
            data=user_dict,
            message="User retrieved successfully"
        )
    except Exception as e:
        logger.error(f"Error getting user: {str(e)}")
        return error_response(message="Failed to retrieve user", status_code=500)


@router.get("/users/virtual/random")
def get_random_virtual_user(
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Get a random virtual user (ADMIN_CREATED or IMPORT).
    """
    try:
        from ..models.user import UserSource
        import random
        
        # Get all virtual users (ADMIN_CREATED or IMPORT)
        virtual_users = db.query(User).filter(
            User.source.in_([UserSource.ADMIN_CREATED, UserSource.IMPORT])
        ).filter(User.is_active == True).all()
        
        if not virtual_users:
            return error_response(
                message="No virtual users found",
                status_code=status.HTTP_404_NOT_FOUND
            )
        
        # Select a random user
        random_user = random.choice(virtual_users)
        user_dict = random_user.to_dict(db=db)
        
        return success_response(
            data=user_dict,
            message="Random virtual user retrieved successfully"
        )
    except Exception as e:
        logger.error(f"Error getting random virtual user: {str(e)}")
        return error_response(message="Failed to retrieve random virtual user", status_code=500)


@router.post("/users/{user_id}/toggle-status")
def toggle_user_status(
    user_id: int,
    request: ToggleUserStatusRequest,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Toggle user active/inactive status.
    Sends a notification to the user about the status change.
    """
    try:
        if request.reason:
            valid, err = validate_reason_english(request.reason)
            if not valid:
                return error_response(message=err or "Invalid reason", status_code=400)

        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return error_response(message="User not found", status_code=404)
        
        user.is_active = not user.is_active
        db.flush()  # Flush to get the new status before creating notification
        
        # Create notification for the user
        status_action = "Enable" if user.is_active else ""
        status_action_en = "activated" if user.is_active else "deactivated"
        
        title = f"{status_action}"
        content = f"Admin{status_action}。"
        
        if request.reason:
            content += f"\n\n：{request.reason}"
        else:
            content += "\n\n，。"
        
        # Create notification
        create_notification(
            db=db,
            user_id=user.id,
            type=NotificationType.ACCOUNT_STATUS_CHANGED,
            title=title,
            content=content,
            link_url="/profile" if user.is_active else None
        )
        
        db.commit()
        
        logger.info(f"Admin {current_admin.username} {status_action_en} user {user.email}" + 
                   (f" (reason: {request.reason})" if request.reason else ""))
        
        return success_response(message=f"User {status_action_en} successfully")
    except Exception as e:
        db.rollback()
        logger.error(f"Error toggling user status: {str(e)}")
        return error_response(message="Failed to update user status")
