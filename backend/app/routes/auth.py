from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone
import os
import httpx
from dotenv import load_dotenv

from ..models.base import get_db
from ..models.user import User, UserSource
from ..models.credit_record import CreditType
from ..services.credit_service import add_credits as credit_service_add_credits
from ..models.invitation import Invitation
from ..models.schemas import (
    RegisterRequest,
    LoginRequest,
    LoginResponse,
    SendCodeRequest,
    VerifyCodeRequest,
    ForgotPasswordRequest,
    ResetPasswordRequest,
    GoogleCallbackRequest,
)
from ..utils.auth import hash_password, verify_password, create_access_token
from ..utils.responses import success_response, error_response
from ..utils.logger import logger
from ..utils.handle import generate_handle
from ..models.notification import NotificationType
from ..utils.notification import create_notification
from ..services.email import send_verification_code, verify_code, send_welcome_email, send_password_reset_code

load_dotenv()

router = APIRouter()

NEW_USER_CREDITS = int(os.getenv("NEW_USER_CREDITS", "10"))
NEW_USER_CREDITS_EXPIRY_DAYS = int(os.getenv("NEW_USER_CREDITS_EXPIRY_DAYS", "30"))

INVITE_REWARD_INVITER = int(os.getenv("INVITE_REWARD_INVITER", "10"))
INVITE_REWARD_INVITEE = int(os.getenv("INVITE_REWARD_INVITEE", "10"))
INVITE_REWARD_EXPIRY_DAYS = int(os.getenv("INVITE_REWARD_EXPIRY_DAYS", "90"))


@router.post("/send-code")
async def send_code(request: SendCodeRequest, db: Session = Depends(get_db)):
    """
    Send verification code to email.
    """
    try:
        # Check if email already exists
        existing_user = db.query(User).filter(User.email == request.email).first()
        if existing_user:
            return error_response(
                message="Email already registered",
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        # Send verification code
        code, error_msg = await send_verification_code(request.email)
        
        if code is None:
            return error_response(
                message=error_msg or "Failed to send verification code. Please check your email settings or try again later.",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        # In development, return the code for testing
        if os.getenv("ENVIRONMENT") == "development":
            logger.debug("Development mode: Verification code generated")
            return success_response(
                data={"code": code, "expires_in": 300},
                message=f"Verification code: {code} (Dev Mode)"
            )
        
        return success_response(
            message="Verification code sent successfully"
        )
        
    except Exception as e:
        logger.error(f"Error sending verification code: {str(e)}")
        return error_response(
            message="An error occurred while sending verification code",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.post("/verify-code")
async def verify_code_endpoint(request: VerifyCodeRequest, db: Session = Depends(get_db)):
    """
    Verify email verification code (without completing registration).
    """
    try:
        # Check if email already exists
        existing_user = db.query(User).filter(User.email == request.email).first()
        if existing_user:
            return error_response(
                message="Email already registered",
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        # Verify code without removing it (so it can be used again in registration)
        from ..services.email import verify_code as verify_code_func
        if not verify_code_func(request.email, request.verification_code, remove_on_success=False):
            return error_response(
                message="Invalid or expired verification code",
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        return success_response(
            message="Verification code is valid"
        )
        
    except Exception as e:
        logger.error(f"Error verifying code: {str(e)}")
        return error_response(
            message="An error occurred while verifying code",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.post("/register")
async def register(request: RegisterRequest, db: Session = Depends(get_db)):
    """
    Register a new user with email verification.
    """
    try:
        # Check if email already exists
        existing_user = db.query(User).filter(User.email == request.email).first()
        if existing_user:
            return error_response(
                message="Email already registered",
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        # Verify code
        if not verify_code(request.email, request.verification_code):
            return error_response(
                message="Invalid or expired verification code",
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        # Generate unique handle
        user_handle = generate_handle(db)
        
        # Create new user
        hashed_password = hash_password(request.password)
        new_user = User(
            handle=user_handle,
            email=request.email,
            password_hash=hashed_password,
            nickname=request.nickname,
            email_verified=True,
            source=UserSource.REGISTER,
            total_credits=0,
        )
        
        db.add(new_user)
        db.flush()  # Get user ID without committing
        
        #  - Process invitation code
        inviter_id = None
        if request.invite_code:
            invitation = db.query(Invitation).filter(
                Invitation.invite_code == request.invite_code.upper(),
                Invitation.status == "pending"
            ).first()
            
            if invitation:
                invitation.invitee_id = new_user.id
                invitation.used_at = datetime.now(timezone.utc)
                invitation.status = "completed"
                inviter_id = invitation.inviter_id
                logger.info(f"User {new_user.id} registered with invitation code: {request.invite_code}")
        
        # Grant welcome credits
        expire_at = datetime.now(timezone.utc) + timedelta(days=NEW_USER_CREDITS_EXPIRY_DAYS)
        credit_service_add_credits(
            db,
            new_user.id,
            NEW_USER_CREDITS,
            CreditType.GIFT,
            f"Welcome bonus - {NEW_USER_CREDITS} credits",
            expire_at=expire_at,
        )
        
        # ， - Grant invitation rewards if applicable
        if inviter_id:
            reward_expiry = datetime.now(timezone.utc) + timedelta(days=INVITE_REWARD_EXPIRY_DAYS)
            
            #  - Invitee reward
            credit_service_add_credits(
                db,
                new_user.id,
                INVITE_REWARD_INVITEE,
                CreditType.GIFT,
                f"Referral bonus - {INVITE_REWARD_INVITEE} credits",
                expire_at=reward_expiry,
            )
            
            #  - Inviter reward
            credit_service_add_credits(
                db,
                inviter_id,
                INVITE_REWARD_INVITER,
                CreditType.GIFT,
                f"Friend referral reward - {INVITE_REWARD_INVITER} credits",
                expire_at=reward_expiry,
            )
            
            invitation.reward_granted = True
            
            logger.info(f"Invitation rewards granted: inviter={inviter_id}, invitee={new_user.id}")
            
            # （）- Bell notification for both (English)
            create_notification(
                db, inviter_id, NotificationType.CREDIT_UPDATE,
                title="Referral reward",
                content=f"Your friend signed up with your invite link. You've received {INVITE_REWARD_INVITER} credits.",
                link_url="/rewards"
            )
            create_notification(
                db, new_user.id, NotificationType.CREDIT_UPDATE,
                title="Referral bonus",
                content=f"Thanks for signing up with an invite code. You've received {INVITE_REWARD_INVITEE} credits.",
                link_url="/rewards"
            )
        
        new_user.last_login = datetime.now(timezone.utc)
        from ..utils.activity import record_user_activity
        record_user_activity(new_user.id, db)
        db.commit()
        db.refresh(new_user)
        
        # Send welcome email (non-blocking)
        try:
            await send_welcome_email(new_user.email, new_user.nickname, NEW_USER_CREDITS)
        except Exception as e:
            logger.error(f"Failed to send welcome email: {str(e)}")
        
        # Generate JWT token
        access_token = create_access_token(data={"sub": new_user.id})
        
        logger.info(f"New user registered: {new_user.email}")
        
        return success_response(
            data={
                "access_token": access_token,
                "token_type": "bearer",
                "user": new_user.to_dict(),
            },
            message="Registration successful",
            status_code=status.HTTP_201_CREATED
        )
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error during registration: {str(e)}")
        return error_response(
            message="An error occurred during registration",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.post("/login")
async def login(request: LoginRequest, db: Session = Depends(get_db)):
    """
    Login with email and password.
    """
    try:
        # Find user by email
        user = db.query(User).filter(User.email == request.email).first()
        
        if not user or not user.password_hash:
            return error_response(
                message="Invalid email or password",
                status_code=status.HTTP_401_UNAUTHORIZED
            )
        
        # Verify password
        if not verify_password(request.password, user.password_hash):
            return error_response(
                message="Invalid email or password",
                status_code=status.HTTP_401_UNAUTHORIZED
            )
        
        # Check if user is active
        if not user.is_active:
            return error_response(
                message="Account is inactive",
                status_code=status.HTTP_403_FORBIDDEN
            )
        
        # Update last login
        user.last_login = datetime.now(timezone.utc)
        from ..utils.activity import record_user_activity
        record_user_activity(user.id, db)
        db.commit()
        
        # Generate JWT token
        access_token = create_access_token(data={"sub": user.id})
        
        logger.info(f"User logged in: {user.email}")
        
        return success_response(
            data={
                "access_token": access_token,
                "token_type": "bearer",
                "user": user.to_dict(),
            },
            message="Login successful"
        )
        
    except Exception as e:
        logger.error(f"Error during login: {str(e)}")
        return error_response(
            message="An error occurred during login",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.get("/google/url")
async def google_auth_url(request: Request):
    """
    Get Google OAuth URL for authentication.
    Redirects to frontend callback page after Google authentication.
    
    Query params:
        redirect: Optional redirect path to return to after login
        invite: Optional invitation code for referral rewards (used when signing up from invite link)
    """
    from urllib.parse import quote
    import json
    
    google_client_id = os.getenv("GOOGLE_CLIENT_ID")
    frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
    redirect_uri = f"{frontend_url}/auth/google/callback"
    
    if not google_client_id:
        return error_response(
            message="Google OAuth not configured",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    
    redirect_path = request.query_params.get("redirect", "/")
    invite = (request.query_params.get("invite") or "").strip().upper() or None
    
    # state: pass both redirect and invite to callback page
    state_obj = {"r": redirect_path, "i": invite or ""}
    state = quote(json.dumps(state_obj))
    
    auth_url = (
        f"https://accounts.google.com/o/oauth2/v2/auth?"
        f"client_id={google_client_id}&"
        f"redirect_uri={redirect_uri}&"
        f"response_type=code&"
        f"scope=openid email profile&"
        f"access_type=offline&"
        f"prompt=consent&"
        f"state={state}"
    )
    
    return success_response(
        data={"url": auth_url},
        message="Google OAuth URL generated"
    )


@router.post("/forgot-password")
async def forgot_password(request: ForgotPasswordRequest, db: Session = Depends(get_db)):
    """
    Send password reset code to user's email.
    """
    try:
        # Check if email exists
        user = db.query(User).filter(User.email == request.email).first()
        if not user:
            # Don't reveal if email exists for security
            return success_response(
                message="If the email exists, a password reset code has been sent"
            )
        
        # Send password reset code
        code, error_msg = await send_password_reset_code(request.email)
        
        if code is None:
            return error_response(
                message=error_msg or "Failed to send password reset code. Please check your email settings or try again later.",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        # In development, return the code for testing
        if os.getenv("ENVIRONMENT") == "development":
            logger.debug("Development mode: Password reset code generated")
            return success_response(
                data={"code": code, "expires_in": 600},
                message=f"Password reset code: {code} (Dev Mode)"
            )
        
        return success_response(
            message="Password reset code sent successfully"
        )
        
    except Exception as e:
        logger.error(f"Error sending password reset code: {str(e)}")
        return error_response(
            message="An error occurred while sending password reset code",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.post("/reset-password")
async def reset_password(request: ResetPasswordRequest, db: Session = Depends(get_db)):
    """
    Reset user password with verification code.
    """
    try:
        # Find user by email
        user = db.query(User).filter(User.email == request.email).first()
        if not user:
            return error_response(
                message="Invalid email or verification code",
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        # Verify code
        if not verify_code(request.email, request.verification_code):
            return error_response(
                message="Invalid or expired verification code",
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        # Update password
        user.password_hash = hash_password(request.new_password)
        db.commit()
        
        logger.info(f"Password reset successful for {user.email}")
        
        return success_response(
            message="Password reset successful"
        )
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error resetting password: {str(e)}")
        return error_response(
            message="An error occurred while resetting password",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.post("/google/callback")
async def google_callback(request: GoogleCallbackRequest, db: Session = Depends(get_db)):
    """
    Handle Google OAuth callback and create/login user.
    
    Expects JSON body with 'code' field containing the authorization code from Google.
    """
    try:
        code = request.code
        if not code:
            return error_response(
                message="Authorization code is required",
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        google_client_id = os.getenv("GOOGLE_CLIENT_ID")
        google_client_secret = os.getenv("GOOGLE_CLIENT_SECRET")
        frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
        redirect_uri = f"{frontend_url}/auth/google/callback"
        
        if not google_client_id or not google_client_secret:
            logger.error("Google OAuth credentials not configured")
            return error_response(
                message="Google OAuth not configured",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        # Exchange authorization code for access token
        token_url = "https://oauth2.googleapis.com/token"
        token_data = {
            "code": code,
            "client_id": google_client_id,
            "client_secret": google_client_secret,
            "redirect_uri": redirect_uri,
            "grant_type": "authorization_code"
        }
        
        async with httpx.AsyncClient() as client:
            token_response = await client.post(token_url, data=token_data)
            token_response.raise_for_status()
            token_info = token_response.json()
        
        access_token = token_info.get("access_token")
        if not access_token:
            logger.error("Failed to get access token from Google")
            return error_response(
                message="Failed to authenticate with Google",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        # Get user info from Google
        user_info_url = "https://www.googleapis.com/oauth2/v2/userinfo"
        headers = {"Authorization": f"Bearer {access_token}"}
        
        async with httpx.AsyncClient() as client:
            user_info_response = await client.get(user_info_url, headers=headers)
            user_info_response.raise_for_status()
            google_user = user_info_response.json()
        
        google_id = google_user.get("id")
        email = google_user.get("email")
        name = google_user.get("name", "")
        picture = google_user.get("picture")
        
        if not google_id or not email:
            logger.error("Missing required user info from Google")
            return error_response(
                message="Failed to get user information from Google",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        # Check if user exists by google_id or email
        user = db.query(User).filter(
            (User.google_id == google_id) | (User.email == email)
        ).first()
        
        if user:
            # ：，、，
            # Existing user: login only, do not process or consume invite_code; code stays available for new users
            if not user.google_id:
                user.google_id = google_id
            if picture and not user.avatar_url:
                user.avatar_url = picture
            if name and not user.nickname:
                user.nickname = name
            user.email_verified = True
            user.last_login = datetime.now(timezone.utc)
            from ..utils.activity import record_user_activity
            record_user_activity(user.id, db)
            db.commit()
            db.refresh(user)
            
            logger.info(f"Google OAuth login: existing user {user.email}")
        else:
            # New user - create account
            handle = generate_handle(db)
            user = User(
                handle=handle,
                email=email,
                google_id=google_id,
                nickname=name or email.split("@")[0],
                avatar_url=picture,
                password_hash=None,  # OAuth users don't have password
                email_verified=True,  # Google emails are verified
                is_active=True,
                source=UserSource.GOOGLE,
                total_credits=0,
            )
            db.add(user)
            db.flush()  #  user.id
            user.last_login = datetime.now(timezone.utc)
            from ..utils.activity import record_user_activity
            record_user_activity(user.id, db)
            db.commit()
            db.refresh(user)
            
            # Add welcome credits
            if NEW_USER_CREDITS > 0:
                credit_service_add_credits(
                    db,
                    user.id,
                    NEW_USER_CREDITS,
                    CreditType.GIFT,
                    f"Welcome bonus ({NEW_USER_CREDITS} credits)",
                    expire_at=datetime.now(timezone.utc) + timedelta(days=NEW_USER_CREDITS_EXPIRY_DAYS) if NEW_USER_CREDITS_EXPIRY_DAYS > 0 else None,
                )
                db.commit()
            
            # （）- Invitation rewards (same as email register)
            if getattr(request, "invite_code", None):
                invitation = db.query(Invitation).filter(
                    Invitation.invite_code == (request.invite_code or "").upper(),
                    Invitation.status == "pending"
                ).first()
                if invitation:
                    invitation.invitee_id = user.id
                    invitation.used_at = datetime.now(timezone.utc)
                    invitation.status = "completed"
                    inviter_id = invitation.inviter_id
                    reward_expiry = datetime.now(timezone.utc) + timedelta(days=INVITE_REWARD_EXPIRY_DAYS)
                    credit_service_add_credits(
                        db,
                        user.id,
                        INVITE_REWARD_INVITEE,
                        CreditType.GIFT,
                        f"Referral bonus - {INVITE_REWARD_INVITEE} credits",
                        expire_at=reward_expiry,
                    )
                    credit_service_add_credits(
                        db,
                        inviter_id,
                        INVITE_REWARD_INVITER,
                        CreditType.GIFT,
                        f"Friend referral reward - {INVITE_REWARD_INVITER} credits",
                        expire_at=reward_expiry,
                    )
                    invitation.reward_granted = True
                    db.commit()
                    db.refresh(user)
                    logger.info(f"Invitation rewards granted (Google signup): inviter={inviter_id}, invitee={user.id}")
                    
                    # （）- Bell notification for both (English)
                    create_notification(
                        db, inviter_id, NotificationType.CREDIT_UPDATE,
                        title="Referral reward",
                        content=f"Your friend signed up with your invite link. You've received {INVITE_REWARD_INVITER} credits.",
                        link_url="/rewards"
                    )
                    create_notification(
                        db, user.id, NotificationType.CREDIT_UPDATE,
                        title="Referral bonus",
                        content=f"Thanks for signing up with an invite code. You've received {INVITE_REWARD_INVITEE} credits.",
                        link_url="/rewards"
                    )
            
            # Send welcome email
            try:
                await send_welcome_email(user.email, user.nickname, NEW_USER_CREDITS)
            except Exception as e:
                logger.warning(f"Failed to send welcome email: {str(e)}")
            
            logger.info(f"Google OAuth registration: new user {user.email}")
        
        # Generate JWT token
        access_token_jwt = create_access_token(data={"sub": user.id})
        
        return success_response(
            data={
                "access_token": access_token_jwt,
                "token_type": "bearer",
                "user": user.to_dict(),
            },
            message="Google authentication successful"
        )
        
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error during Google OAuth: {str(e)}")
        return error_response(
            message="Failed to authenticate with Google. Please try again.",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    except Exception as e:
        logger.error(f"Error during Google OAuth: {str(e)}")
        return error_response(
            message="An error occurred during Google authentication",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

