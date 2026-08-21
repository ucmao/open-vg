"""
Utility functions for generating and validating user handles.
"""
import random
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Tuple

# Reserved handles that cannot be used by users
RESERVED_HANDLES = {
    'admin', 'system', 'official', 'artify', 'root', 'api', 'www', 'mail', 'ftp',
    'support', 'help', 'contact', 'about', 'terms', 'privacy', 'blog', 'news',
    'register', 'login', 'signup', 'signin', 'logout', 'profile', 'settings',
    'dashboard', 'home', 'index', 'search', 'explore', 'create', 'generate',
    'user', 'users', 'account', 'accounts', 'follow', 'following', 'followers',
    'like', 'likes', 'favorite', 'favorites', 'comment', 'comments', 'share',
    'upload', 'download', 'media', 'image', 'images', 'video', 'videos',
    'works', 'work', 'gallery', 'galleries', 'post', 'posts', 'tag', 'tags',
    'category', 'categories', 'moderator', 'mod', 'staff', 'team', 'dev',
    'developer', 'test', 'testing', 'demo', 'demo1', 'demo2', 'admin1',
    'null', 'undefined', 'true', 'false', 'none', 'api', 'api1', 'api2'
}


def generate_handle(db: Session, max_attempts: int = 100) -> str:
    """
    Generate a unique handle in format: u_ + 7 random characters (digits + lowercase letters).
    Format: u_XXXXXXX where XXXXXXX is 7 characters from [0-9a-z]
    Example: u_834jds8, u_a1b2c3d
    
    Args:
        db: Database session
        max_attempts: Maximum attempts to generate a unique handle
        
    Returns:
        Unique handle string (format: u_XXXXXXX)
        
    Raises:
        Exception: If unable to generate unique handle after max_attempts
    """
    from ..models.user import User
    
    # Characters pool: digits (0-9) and lowercase letters (a-z)
    chars = '0123456789abcdefghijklmnopqrstuvwxyz'
    
    # Generate handles in format: u_ + 7 random characters
    for _ in range(max_attempts):
        # Generate 7 random characters from the pool
        random_chars = ''.join(random.choice(chars) for _ in range(7))
        handle = f"u_{random_chars}"
        
        # Check if handle already exists (case-insensitive)
        handle_lower = handle.lower()
        existing = db.query(User).filter(func.lower(User.handle) == handle_lower).first()
        if not existing:
            return handle
    
    raise Exception("Unable to generate unique handle after maximum attempts")


def validate_handle(handle: str, db: Session, exclude_user_id: int = None) -> Tuple[bool, str]:
    """
    Validate if a handle is valid and available.
    Case-insensitive uniqueness check.
    
    Args:
        handle: Handle string to validate
        db: Database session
        exclude_user_id: User ID to exclude from uniqueness check (for updates)
        
    Returns:
        Tuple of (is_valid: bool, error_message: str)
    """
    from ..models.user import User
    
    # Length check (6-15 characters)
    if len(handle) < 6 or len(handle) > 15:
        return False, "Handle must be between 6 and 15 characters"
    
    # Must start with a letter
    if not handle[0].isalpha():
        return False, "Handle must start with a letter"
    
    # Format check (letters, numbers, and underscores only)
    if not all(c.isalnum() or c == '_' for c in handle):
        return False, "Handle can only contain letters, numbers, and underscores"
    
    # Check reserved handles (case-insensitive)
    handle_lower = handle.lower()
    if handle_lower in RESERVED_HANDLES:
        return False, "This handle is reserved and cannot be used"
    
    # Check if handle already exists (case-insensitive)
    # Use func.lower() for case-insensitive comparison
    query = db.query(User).filter(func.lower(User.handle) == handle_lower)
    if exclude_user_id:
        query = query.filter(User.id != exclude_user_id)
    
    existing = query.first()
    if existing:
        return False, "This handle is already taken"
    
    return True, ""

