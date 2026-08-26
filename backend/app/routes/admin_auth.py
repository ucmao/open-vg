"""
Admin authentication routes for system administrators.
 admins ，。
"""

from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from pydantic import BaseModel, Field

from ..models.base import get_db
from ..models.admin import Admin
from ..utils.auth import hash_password, verify_password, create_access_token, get_current_admin
from ..utils.responses import success_response, error_response
from ..utils.logger import logger
from ..utils.rate_limit import enforce_rate_limit, env_limit

router = APIRouter()
ADMIN_LOGIN_LIMIT = env_limit("ADMIN_LOGIN_RATE_LIMIT", 5)
ADMIN_LOGIN_WINDOW = env_limit("ADMIN_LOGIN_RATE_WINDOW_SECONDS", 300)


class AdminLoginRequest(BaseModel):
    username: str = Field(..., min_length=1, max_length=255)
    password: str = Field(..., min_length=1)


class AdminLoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict


@router.post("/login")
def admin_login(
    request: AdminLoginRequest,
    http_request: Request,
    db: Session = Depends(get_db),
):
    """
    Admin Login。

    - ：admins
    - ：username  email + password
    - Token：sub  \"admin:<id>\" ，
    """
    enforce_rate_limit(http_request, "admin-auth:login:ip", ADMIN_LOGIN_LIMIT, ADMIN_LOGIN_WINDOW)
    enforce_rate_limit(
        http_request,
        "admin-auth:login:account",
        ADMIN_LOGIN_LIMIT,
        ADMIN_LOGIN_WINDOW,
        identity=f"admin:{request.username}",
    )
    try:
        # Find admin by username or email
        admin = db.query(Admin).filter(
            (Admin.username == request.username) | (Admin.email == request.username)
        ).first()

        if not admin:
            logger.warning(f"Admin login attempt with non-existent username/email: {request.username}")
            return error_response(
                message="Invalid username or password",
                status_code=status.HTTP_401_UNAUTHORIZED,
            )

        if not admin.is_active:
            return error_response(
                message="Account is disabled",
                status_code=status.HTTP_403_FORBIDDEN,
            )

        # Verify password
        if not verify_password(request.password, admin.password_hash):
            logger.warning(f"Failed admin login attempt for: {request.username}")
            return error_response(
                message="Invalid username or password",
                status_code=status.HTTP_401_UNAUTHORIZED,
            )

        # Update last login
        admin.last_login = datetime.now(timezone.utc)
        db.commit()

        # Generate JWT token - sub , token
        access_token = create_access_token(
            data={
                "sub": f"admin:{admin.id}",
                "role": admin.role,
            }
        )

        logger.info(f"Admin logged in: {admin.username}")

        return success_response(
            data={
                "access_token": access_token,
                "token_type": "bearer",
                "user": {
                    "id": admin.id,
                    "username": admin.username,
                    "email": admin.email,
                    "nickname": admin.nickname,
                    "role": admin.role,
                },
            },
            message="Login successful",
        )

    except Exception as e:
        logger.error(f"Error during admin login: {str(e)}")
        return error_response(
            message="An error occurred during login",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@router.get("/me")
def get_current_admin_info(
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Get current admin information.
    Also tries to find corresponding user account by email.
    """
    try:
        admin_data = current_admin.to_dict()
        
        # Try to find corresponding user account by email
        from ..models.user import User
        user = None
        if current_admin.email:
            user = db.query(User).filter(User.email == current_admin.email).first()
        
        # If user found, include user info
        if user:
            admin_data["user"] = {
                "id": user.id,
                "nickname": user.nickname,
                "handle": user.handle,
                "avatar_url": user.avatar_url,
                "email": user.email
            }
        
        return success_response(
            data=admin_data,
            message="Admin info retrieved successfully"
        )
    except Exception as e:
        logger.error(f"Error getting admin info: {str(e)}")
        return error_response(
            message="An error occurred while retrieving admin info",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
