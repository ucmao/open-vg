from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func

from .base import Base


class Admin(Base):
    """
    Independent admin user accounts table.
    Isolated from frontend users, used exclusively for Admin Panel authentication.
    """

    __tablename__ = "admins"

    id = Column(Integer, primary_key=True, index=True)

    # Username (must be unique)
    username = Column(String(100), unique=True, index=True, nullable=False)

    # Optional email address
    email = Column(String(255), unique=True, index=True, nullable=True)

    # Password hash
    password_hash = Column(String(255), nullable=False)

    # Display nickname
    nickname = Column(String(100), nullable=False)

    # Role: admin / super_admin / editor
    role = Column(String(50), nullable=False, default="admin")

    # Active status
    is_active = Column(Boolean, default=True, nullable=False)

    # Timestamps
    last_login = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "nickname": self.nickname,
            "role": self.role,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "last_login": self.last_login.isoformat() if self.last_login else None,
        }
