from datetime import datetime, timedelta, timezone
from typing import Optional

from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
import os
from dotenv import load_dotenv

from ..models.base import get_db
from ..models.user import User, UserSource
from ..models.admin import Admin

from ..utils.logger import logger

load_dotenv()

# JWT Configuration
INSECURE_JWT_SECRETS = {
    "your-secret-key-change-in-production",
    "secret",
    "change_me",
    "changeme",
    "jwt_secret",
    "admin123",
    "123456",
    "12345678"
}

_env_mode = os.getenv("ENVIRONMENT", "development").strip().lower()
JWT_SECRET = os.getenv("JWT_SECRET", "").strip()

if _env_mode == "production":
    if not JWT_SECRET or JWT_SECRET in INSECURE_JWT_SECRETS or len(JWT_SECRET) < 16:
        raise RuntimeError(
            "CRITICAL SECURITY ERROR: Insecure or default JWT_SECRET detected in PRODUCTION mode! "
            "Please set a strong JWT_SECRET environment variable (at least 16 characters)."
        )
else:
    if not JWT_SECRET or JWT_SECRET in INSECURE_JWT_SECRETS:
        logger.warning(
            "JWT_SECRET is not set or using insecure default string. Using fallback key for development only. "
            "Set JWT_SECRET in .env for production deployment."
        )
        JWT_SECRET = "your-secret-key-change-in-production"

JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
JWT_EXPIRATION = int(os.getenv("JWT_EXPIRATION", "86400"))  # 24 hours in seconds

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# HTTP Bearer token security
security = HTTPBearer()


def hash_password(password: str) -> str:
    """
    Hash a plain password using bcrypt.
    
    Args:
        password: Plain text password
        
    Returns:
        Hashed password
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain password against a hashed password.
    
    Args:
        plain_password: Plain text password
        hashed_password: Hashed password
        
    Returns:
        True if password matches, False otherwise
    """
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token.
    
    Args:
        data: Dictionary of data to encode in the token
        expires_delta: Optional expiration time delta
        
    Returns:
        Encoded JWT token
    """
    to_encode = data.copy()
    
    # Ensure 'sub' (subject) is a string as per JWT spec
    if "sub" in to_encode and not isinstance(to_encode["sub"], str):
        to_encode["sub"] = str(to_encode["sub"])
    
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(seconds=JWT_EXPIRATION)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)
    
    return encoded_jwt


def decode_access_token(token: str) -> Optional[dict]:
    """
    Decode and verify a JWT access token.
    
    Args:
        token: JWT token string
        
    Returns:
        Decoded token payload or None if invalid
    """
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except JWTError as e:
        logger.error(f"JWT Decode Error: {str(e)}")
        return None


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    """
    Get the current authenticated user from JWT token.
    
    Args:
        credentials: HTTP Bearer credentials
        db: Database session
        
    Returns:
        User object
        
    Raises:
        HTTPException: If token is invalid or user not found
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    token = credentials.credentials
    payload = decode_access_token(token)
    
    if payload is None:
        logger.warning(f"Invalid token payload: {token[:10]}...")
        raise credentials_exception
    
    user_id = payload.get("sub")
    if user_id is None:
        logger.warning(f"Token missing 'sub' claim")
        raise credentials_exception
    
    try:
        # Convert to int to ensure database query works correctly
        user_id = int(user_id)
    except (ValueError, TypeError):
        logger.warning(f"Invalid user_id type in token: {user_id}")
        raise credentials_exception
    
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        logger.warning(f"User not found for ID: {user_id}")
        raise credentials_exception

    # Admin-created virtual users exist only to attribute seeded/community
    # content. They must never become interactive login identities, including
    # through a token issued before this check was added.
    if user.source == UserSource.ADMIN_CREATED:
        logger.warning("Authentication rejected for virtual user ID: %s", user_id)
        raise credentials_exception
    
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Get the current authenticated and active user.
    
    Args:
        current_user: Current user from token
        
    Returns:
        User object
        
    Raises:
        HTTPException: If user is inactive
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )
    
    return current_user


async def get_current_admin_user(
    current_user: User = Depends(get_current_active_user),
) -> User:
    """
    Get the current authenticated admin user.
    
    Args:
        current_user: Current active user
        
    Returns:
        User object
        
    Raises:
        HTTPException: If user is not an admin
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    return current_user


async def get_current_admin(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> Admin:
    """
     JWT  Admin。

    -  sub  \"admin:<id>\"  token
    -  token
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate admin credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    token = credentials.credentials
    payload = decode_access_token(token)

    if payload is None:
        raise credentials_exception

    sub = payload.get("sub")
    if not isinstance(sub, str) or not sub.startswith("admin:"):
        #  token
        raise credentials_exception

    try:
        admin_id = int(sub.split("admin:", 1)[1])
    except (ValueError, IndexError):
        raise credentials_exception

    admin = db.query(Admin).filter(Admin.id == admin_id).first()
    if admin is None or not admin.is_active:
        raise credentials_exception

    return admin


async def get_current_user_or_admin(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    """
    Get the current authenticated user OR admin.
    Returns either a User or an Admin object.
    """
    token = credentials.credentials
    payload = decode_access_token(token)

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    sub = payload.get("sub")
    if sub is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token missing subject",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Check if it's an admin token
    if isinstance(sub, str) and sub.startswith("admin:"):
        try:
            admin_id = int(sub.split("admin:", 1)[1])
            admin = db.query(Admin).filter(Admin.id == admin_id).first()
            if admin and admin.is_active:
                return admin
        except (ValueError, IndexError):
            pass
        
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid admin token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Check if it's a regular user token
    try:
        user_id = int(sub)
        user = db.query(User).filter(User.id == user_id).first()
        if user and user.is_active:
            return user
    except (ValueError, TypeError):
        pass

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid authentication token",
        headers={"WWW-Authenticate": "Bearer"},
    )


# Optional: Function to get user from token without raising exception
async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(
        HTTPBearer(auto_error=False)
    ),
    db: Session = Depends(get_db),
) -> Optional[User]:
    """
    Get the current user if token is provided, None otherwise.
    Useful for endpoints that work both with and without authentication.
    
    Args:
        credentials: Optional HTTP Bearer credentials
        db: Database session
        
    Returns:
        User object or None
    """
    if credentials is None:
        return None
    
    token = credentials.credentials
    payload = decode_access_token(token)
    
    if payload is None:
        return None
    
    user_id: int = payload.get("sub")
    if user_id is None:
        return None
    
    user = db.query(User).filter(User.id == user_id).first()
    return user
