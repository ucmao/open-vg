"""Invitation routes for referral system."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
import random
import string
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

from ..models.base import get_db
from ..models.user import User
from ..models.invitation import Invitation
from ..models.credit_record import CreditRecord, CreditType
from ..utils.auth import get_current_user
from ..utils.responses import success_response, error_response
from ..utils.logger import logger

load_dotenv()

router = APIRouter()

#  - Invitation reward configuration
INVITE_REWARD_INVITER = int(os.getenv("INVITE_REWARD_INVITER", "10"))
INVITE_REWARD_INVITEE = int(os.getenv("INVITE_REWARD_INVITEE", "10"))
INVITE_CODE_LENGTH = int(os.getenv("INVITE_CODE_LENGTH", "8"))
INVITE_REWARD_EXPIRY_DAYS = int(os.getenv("INVITE_REWARD_EXPIRY_DAYS", "90"))


def generate_invite_code(db: Session, length: int = INVITE_CODE_LENGTH) -> str:
    """ - Generate unique invite code."""
    while True:
        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))
        existing = db.query(Invitation).filter(Invitation.invite_code == code).first()
        if not existing:
            return code


@router.post("/invitation/generate")
def generate_invitation(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
     - Generate invitation code for current user.
    
    （100pending）。
    """
    try:
        # pending
        pending_count = db.query(func.count(Invitation.id)).filter(
            Invitation.inviter_id == current_user.id,
            Invitation.status == "pending"
        ).scalar() or 0
        
        if pending_count >= 100:
            return error_response(
                message="You have reached the maximum number of pending invitations (100)",
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        invite_code = generate_invite_code(db)
        
        invitation = Invitation(
            inviter_id=current_user.id,
            invite_code=invite_code,
            status="pending"
        )
        
        db.add(invitation)
        db.commit()
        db.refresh(invitation)
        
        # URL
        frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
        
        logger.info(f"User {current_user.id} generated invitation code: {invite_code}")
        
        return success_response(
            data={
                "invite_code": invite_code,
                "invite_url": f"{frontend_url}/auth/register?invite={invite_code}",
                "created_at": invitation.created_at.isoformat()
            },
            message="Invitation code generated successfully"
        )
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error generating invitation: {str(e)}")
        return error_response(
            message="Failed to generate invitation code",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.get("/invitation/list")
def get_my_invitations(
    page: int = 1,
    page_size: int = 20,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
     - Get my invitation records (paginated).
    
    Returns list of invitations with invitee information if registered.
    """
    try:
        if page < 1:
            page = 1
        if page_size < 1 or page_size > 100:
            page_size = 20
        
        query = db.query(Invitation).filter(
            Invitation.inviter_id == current_user.id
        ).order_by(Invitation.created_at.desc())
        
        total = query.count()
        invitations = query.offset((page - 1) * page_size).limit(page_size).all()
        
        data = []
        for inv in invitations:
            item = inv.to_dict()
            
            if inv.invitee_id:
                invitee = db.query(User).filter(User.id == inv.invitee_id).first()
                if invitee:
                    item["invitee"] = {
                        "id": invitee.id,
                        "nickname": invitee.nickname,
                        "avatar_url": invitee.avatar_url,
                        "created_at": invitee.created_at.isoformat()
                    }
            
            data.append(item)
        
        return success_response(
            data={
                "items": data,
                "total": total,
                "page": page,
                "page_size": page_size,
                "total_pages": (total + page_size - 1) // page_size
            }
        )
        
    except Exception as e:
        logger.error(f"Error getting invitation list: {str(e)}")
        return error_response(
            message="Failed to get invitation list",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.get("/invitation/stats")
def get_invitation_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
     - Get invitation statistics.
    
    Returns:
        - total_invitations:
        - completed_invitations:
        - pending_invitations:
        - total_rewards:
    """
    try:
        total_invitations = db.query(func.count(Invitation.id)).filter(
            Invitation.inviter_id == current_user.id
        ).scalar() or 0
        
        completed_invitations = db.query(func.count(Invitation.id)).filter(
            Invitation.inviter_id == current_user.id,
            Invitation.status == "completed"
        ).scalar() or 0
        
        pending_invitations = db.query(func.count(Invitation.id)).filter(
            Invitation.inviter_id == current_user.id,
            Invitation.status == "pending"
        ).scalar() or 0
        
        total_rewards = completed_invitations * INVITE_REWARD_INVITER
        
        return success_response(
            data={
                "total_invitations": total_invitations,
                "completed_invitations": completed_invitations,
                "pending_invitations": pending_invitations,
                "total_rewards": total_rewards,
                "reward_per_invite": INVITE_REWARD_INVITER
            }
        )
        
    except Exception as e:
        logger.error(f"Error getting invitation stats: {str(e)}")
        return error_response(
            message="Failed to get invitation statistics",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.get("/invitation/verify/{invite_code}")
def verify_invite_code(
    invite_code: str,
    db: Session = Depends(get_db)
):
    """
     - Verify if an invite code is valid.
    
    This endpoint doesn't require authentication (used during registration).
    """
    try:
        invitation = db.query(Invitation).filter(
            Invitation.invite_code == invite_code.upper(),
            Invitation.status == "pending"
        ).first()
        
        if not invitation:
            return error_response(
                message="Invalid or already used invitation code",
                status_code=status.HTTP_404_NOT_FOUND
            )
        
        inviter = db.query(User).filter(User.id == invitation.inviter_id).first()
        
        return success_response(
            data={
                "valid": True,
                "invite_code": invitation.invite_code,
                "inviter_nickname": inviter.nickname if inviter else "Unknown",
                "reward_amount": INVITE_REWARD_INVITEE
            },
            message="Invitation code is valid"
        )
        
    except Exception as e:
        logger.error(f"Error verifying invite code: {str(e)}")
        return error_response(
            message="Failed to verify invitation code",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
