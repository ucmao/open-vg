from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_
from typing import Optional
from datetime import datetime, timezone

from ..models.base import get_db
from ..models.user import User
from ..models.blog import BlogPost, PostStatus
from ..utils.responses import success_response, error_response, paginated_response
from ..utils.logger import logger

router = APIRouter()


def _parse_featured_param(value: Optional[bool]) -> Optional[bool]:
    """Normalize featured query param (handles string 'true'/'1' from some clients)."""
    if value is None:
        return None
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.lower() in ("true", "1", "yes", "on")
    return bool(value)


@router.get("")
def get_blog_posts(
    page: int = 1,
    page_size: int = 12,
    category: Optional[str] = None,
    tag: Optional[str] = None,
    featured: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    """
    Get published blog posts with pagination and filters.
    Only returns posts with status=published and published_at <= now.
    Use featured=true to get posts marked "display on homepage" (is_featured).
    """
    try:
        # Build query for published posts only
        # Use timezone-aware datetime for comparison
        now_utc = datetime.now(timezone.utc)
        query = db.query(BlogPost).filter(
            and_(
                BlogPost.status == PostStatus.PUBLISHED,
                BlogPost.published_at <= now_utc
            )
        )
        
        # Apply filters
        if category:
            query = query.filter(BlogPost.category == category)
        
        if tag:
            query = query.filter(BlogPost.tags.contains([tag]))

        featured_val = _parse_featured_param(featured)
        if featured_val is not None:
            query = query.filter(BlogPost.is_featured == featured_val)
        
        # Get total count
        total = query.count()
        
        # Get paginated results, ordered by published date (newest first)
        posts = query.order_by(
            desc(BlogPost.published_at)
        ).offset((page - 1) * page_size).limit(page_size).all()
        
        # Format results
        items = [post.to_dict(include_content=False, include_author=True) for post in posts]
        
        return paginated_response(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            message="Blog posts retrieved successfully"
        )
        
    except Exception as e:
        logger.error(f"Error getting blog posts: {str(e)}")
        return error_response(
            message="An error occurred while retrieving blog posts",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.get("/{slug}")
def get_blog_post(
    slug: str,
    db: Session = Depends(get_db)
):
    """
    Get a single blog post by slug.
    Only returns published posts.
    """
    try:
        # Use timezone-aware datetime for comparison
        now_utc = datetime.now(timezone.utc)
        post = db.query(BlogPost).filter(
            and_(
                BlogPost.slug == slug,
                BlogPost.status == PostStatus.PUBLISHED,
                BlogPost.published_at <= now_utc
            )
        ).first()
        
        if not post:
            return error_response(
                message="Blog post not found",
                status_code=status.HTTP_404_NOT_FOUND
            )
        
        # Increment view count
        post.view_count += 1
        db.commit()
        db.refresh(post)
        
        return success_response(
            data=post.to_dict(include_content=True, include_author=True),
            message="Blog post retrieved successfully"
        )
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error getting blog post: {str(e)}")
        return error_response(
            message="An error occurred while retrieving blog post",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

