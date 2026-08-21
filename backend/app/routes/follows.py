from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional

from ..models.base import get_db
from ..models.user import User
from ..models.follow import Follow
from ..utils.auth import get_current_user
from ..utils.responses import success_response

router = APIRouter()

@router.post("/{handle}/follow")
def follow_user(
    handle: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Follow a user."""
    target_user = db.query(User).filter(func.lower(User.handle) == handle.lower()).first()
    if not target_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if target_user.id == current_user.id:
        raise HTTPException(status_code=400, detail="You cannot follow yourself")
    
    # Check if already following
    existing_follow = db.query(Follow).filter(
        Follow.follower_id == current_user.id,
        Follow.following_id == target_user.id
    ).first()
    
    if existing_follow:
        return success_response(message="Already following this user")
    
    new_follow = Follow(follower_id=current_user.id, following_id=target_user.id)
    db.add(new_follow)
    db.commit()
    
    # 🔔 Send notification to the target user
    from ..utils.notification import create_notification
    from ..models.notification import NotificationType
    create_notification(
        db=db,
        user_id=target_user.id,
        type=NotificationType.NEW_FOLLOW,
        title="New Follower! 👤",
        content=f"{current_user.nickname or current_user.handle} started following you.",
        link_url=f"/user/{current_user.handle}"
    )
    
    return success_response(message="User followed successfully")

@router.post("/{handle}/unfollow")
def unfollow_user(
    handle: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Unfollow a user."""
    target_user = db.query(User).filter(func.lower(User.handle) == handle.lower()).first()
    if not target_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    follow = db.query(Follow).filter(
        Follow.follower_id == current_user.id,
        Follow.following_id == target_user.id
    ).first()
    
    if not follow:
        return success_response(message="Not following this user")
    
    db.delete(follow)
    db.commit()
    
    return success_response(message="User unfollowed successfully")

@router.post("/remove-follower/{handle}")
def remove_follower(
    handle: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Remove a follower (make someone unfollow you)."""
    target_user = db.query(User).filter(func.lower(User.handle) == handle.lower()).first()
    if not target_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    follow = db.query(Follow).filter(
        Follow.follower_id == target_user.id,
        Follow.following_id == current_user.id
    ).first()
    
    if not follow:
        return success_response(message="This user is not following you")
    
    db.delete(follow)
    db.commit()
    
    return success_response(message="Follower removed successfully")

@router.get("/status/{handle}")
def get_follow_status(
    handle: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Check if the current user is following another user."""
    target_user = db.query(User).filter(func.lower(User.handle) == handle.lower()).first()
    if not target_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    is_following = db.query(Follow).filter(
        Follow.follower_id == current_user.id,
        Follow.following_id == target_user.id
    ).first() is not None
    
    return success_response(data={"is_following": is_following})

@router.get("/following")
def get_following_list(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get the list of users the current user is following."""
    following = db.query(User).join(
        Follow, User.id == Follow.following_id
    ).filter(Follow.follower_id == current_user.id).all()
    
    return success_response(data=[{
        "handle": user.handle,
        "nickname": user.nickname,
        "avatar_url": user.avatar_url,
        "bio": user.bio
    } for user in following])

@router.get("/followers")
def get_followers_list(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get the list of users following the current user."""
    followers = db.query(User).join(
        Follow, User.id == Follow.follower_id
    ).filter(Follow.following_id == current_user.id).all()
    
    return success_response(data=[{
        "handle": user.handle,
        "nickname": user.nickname,
        "avatar_url": user.avatar_url,
        "bio": user.bio
    } for user in followers])

