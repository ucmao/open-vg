from fastapi import APIRouter, Depends, HTTPException, status, Request, Body
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Optional

from ..models.base import get_db
from ..models.topic import Topic, TopicStatus
from ..models.user import User
from ..models.admin import Admin
from ..models.generation_model import GenerationModel
from ..models.schemas import TopicResponse, CreateTopicRequest, UpdateTopicRequest
from ..utils.auth import get_current_admin, get_current_user_optional
from ..utils.responses import success_response, error_response, paginated_response
from ..utils.logger import logger

from pydantic import BaseModel, Field

router = APIRouter()

class BatchUpdateTopicRequest(BaseModel):
    """"""
    topic_ids: Optional[List[int]] = Field(None, description="ID")
    status: Optional[str] = Field(None, description="")
    is_featured: Optional[bool] = Field(None, description="")

@router.post("/batch-update")
def batch_update_topics(
    request: BatchUpdateTopicRequest,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """ (Admin only)."""
    if not request.topic_ids:
        return error_response(message="Topic ID list not provided", status_code=400)
    
    try:
        update_data = {}
        if request.status is not None:
            update_data[Topic.status] = TopicStatus(request.status)
        if request.is_featured is not None:
            update_data[Topic.is_featured] = request.is_featured
            
        if not update_data:
            return error_response(message="Update data not provided", status_code=400)
            
        affected = db.query(Topic).filter(Topic.id.in_(request.topic_ids)).update(
            update_data, synchronize_session=False
        )
        db.commit()
        return success_response(message=f"Successfully updated {affected} ")
    except Exception as e:
        db.rollback()
        logger.error(f"Error batch updating topics: {str(e)}")
        return error_response(message=f"Update failed: {str(e)}", status_code=500)

@router.post("/batch-delete")
def batch_delete_topics(
    topic_ids: List[int] = Body(..., embed=True),
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """ (Admin only)."""
    if not topic_ids:
        return error_response(message="ID", status_code=400)
        
    try:
        affected = db.query(Topic).filter(Topic.id.in_(topic_ids)).delete(synchronize_session=False)
        db.commit()
        return success_response(message=f" {affected} ")
    except Exception as e:
        db.rollback()
        logger.error(f"Error batch deleting topics: {str(e)}")
        return error_response(message=f": {str(e)}", status_code=500)

@router.get("")
def get_topics(
    request: Request,
    page: int = 1,
    page_size: int = 20,
    featured_only: bool = False,
    type_filter: Optional[str] = None,  # "topic" | "magic" | "all"
    status_filter: Optional[str] = None,  # "published" | "draft" | "archived"
    db: Session = Depends(get_db)
):
    """Get list of topics. Admins see all, users see published only. type_filter: topic=(magic=, all=)."""
    try:
        # Check if this is an admin path
        is_admin_path = "/api/admin" in request.url.path
        
        query = db.query(Topic)
        
        # If not admin path, only show published
        if not is_admin_path:
            query = query.filter(Topic.status == TopicStatus.PUBLISHED)
        
        # Admin can filter by status
        if is_admin_path and status_filter:
            try:
                status_enum = TopicStatus(status_filter)
                query = query.filter(Topic.status == status_enum)
            except ValueError:
                pass  # Invalid status, ignore filter
        
        if type_filter == "topic":
            query = query.filter(Topic.generation_model_id.is_(None))
        elif type_filter == "magic":
            query = query.filter(Topic.generation_model_id.isnot(None))
        # "all" or None: no filter
        
        if featured_only:
            query = query.filter(Topic.is_featured == True)
            
        total = query.count()
        # Try to order by sort_order if column exists, otherwise fallback
        try:
            topics = query.order_by(Topic.sort_order, desc(Topic.is_featured), desc(Topic.created_at))\
                          .offset((page - 1) * page_size).limit(page_size).all()
        except Exception:
            # Fallback if sort_order column doesn't exist yet
            topics = query.order_by(desc(Topic.is_featured), desc(Topic.created_at))\
                          .offset((page - 1) * page_size).limit(page_size).all()
        
        items = [topic.to_dict() for topic in topics]
        
        return paginated_response(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            message="Topics retrieved successfully"
        )
    except Exception as e:
        logger.error(f"Error in GET topics: {str(e)}")
        return error_response(message=f"Database error occurred: {str(e)}", status_code=500)

@router.get("/slugs-by-model")
def get_topic_slugs_by_model(db: Session = Depends(get_db)):
    """Return { model_key: slug } for all published topics that have generation_model_id (model landing pages). Public."""
    try:
        topics = (
            db.query(Topic)
            .join(GenerationModel, Topic.generation_model_id == GenerationModel.id)
            .filter(
                Topic.status == TopicStatus.PUBLISHED,
                Topic.generation_model_id.isnot(None),
            )
            .all()
        )
        result = { t.generation_model.model_key: t.slug for t in topics if t.generation_model }
        return success_response(data=result, message="OK")
    except Exception as e:
        logger.error(f"Error fetching topic slugs by model: {str(e)}")
        return error_response(message="Failed to fetch", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@router.get("/{id_or_slug}")
def get_topic_detail(
    request: Request,
    id_or_slug: str,
    db: Session = Depends(get_db)
):
    """Get topic details by ID or slug."""
    try:
        if id_or_slug.isdigit():
            topic = db.query(Topic).filter(Topic.id == int(id_or_slug)).first()
        else:
            topic = db.query(Topic).filter(Topic.slug == id_or_slug).first()
        
        if not topic:
            return error_response(message="Topic not found", status_code=status.HTTP_404_NOT_FOUND)
        
        # Check if allowed to view
        is_admin_path = "/api/admin" in request.url.path
        
        if topic.status != TopicStatus.PUBLISHED and not is_admin_path:
            return error_response(message="Topic not found", status_code=status.HTTP_404_NOT_FOUND)
        
        # Increment view count if not admin path
        if not is_admin_path:
            topic.view_count += 1
            db.commit()
        
        return success_response(data=topic.to_dict(), message="Topic retrieved successfully")
    except Exception as e:
        logger.error(f"Error in GET topic detail: {str(e)}")
        return error_response(message=f"Database error occurred: {str(e)}", status_code=500)

# Admin routes for Topic management
@router.post("")
def create_topic(
    request: CreateTopicRequest,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Create a new topic (Admin only)."""
    try:
        # Check if slug exists
        existing = db.query(Topic).filter(Topic.slug == request.slug).first()
        if existing:
            return error_response(message="URL ", status_code=status.HTTP_400_BAD_REQUEST)
        
        if request.generation_model_id is not None:
            other = db.query(Topic).filter(Topic.generation_model_id == request.generation_model_id).first()
            if other:
                return error_response(message="", status_code=status.HTTP_400_BAD_REQUEST)
        
        topic = Topic(
            slug=request.slug,
            title=request.title,
            excerpt=request.excerpt,
            content=request.content or "", # Ensure not None
            meta_title=request.meta_title,
            meta_description=request.meta_description,
            meta_keywords=request.meta_keywords,
            og_image=request.og_image,
            category=request.category,
            category_id=request.category_id,
            tags=request.tags or [],
            featured_image=request.featured_image,
            icon=request.icon,
            config=request.config,
            generation_model_id=request.generation_model_id,
            status=TopicStatus(request.status),
            is_featured=request.is_featured,
            sort_order=request.sort_order,
            published_at=request.published_at
        )
        
        db.add(topic)
        db.commit()
        db.refresh(topic)
        
        return success_response(data=topic.to_dict(), message="")
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating topic: {str(e)}")
        return error_response(message=f": {str(e)}", status_code=500)

@router.put("/{topic_id}")
def update_topic(
    topic_id: int,
    request: UpdateTopicRequest,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Update an existing topic (Admin only)."""
    topic = db.query(Topic).filter(Topic.id == topic_id).first()
    if not topic:
        return error_response(message="Topic not found", status_code=status.HTTP_404_NOT_FOUND)
    
    try:
        update_data = request.model_dump(exclude_unset=True)
        if "generation_model_id" in update_data and update_data["generation_model_id"] is not None:
            other = (
                db.query(Topic)
                .filter(
                    Topic.generation_model_id == update_data["generation_model_id"],
                    Topic.id != topic_id,
                )
                .first()
            )
            if other:
                return error_response(message="Model already has an exclusive page configured", status_code=status.HTTP_400_BAD_REQUEST)
        
        for key, value in update_data.items():
            if key == "status" and value:
                setattr(topic, key, TopicStatus(value))
            elif key == "config" and value is not None:
                setattr(topic, key, value)
            else:
                setattr(topic, key, value)
        
        db.commit()
        db.refresh(topic)
        
        return success_response(data=topic.to_dict(), message="Topic updated successfully")
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating topic: {str(e)}")
        return error_response(message=f"Update failed: {str(e)}", status_code=500)

@router.delete("/{topic_id}")
def delete_topic(
    topic_id: int,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Delete a topic (Admin only)."""
    topic = db.query(Topic).filter(Topic.id == topic_id).first()
    if not topic:
        return error_response(message="", status_code=status.HTTP_404_NOT_FOUND)
    
    try:
        db.delete(topic)
        db.commit()
        return success_response(message="")
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting topic: {str(e)}")
        return error_response(message=f": {str(e)}", status_code=500)

@router.post("/generate-seo")
def generate_topic_seo_from_content(
    request: dict = Body(...),
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Generate SEO title, description, excerpt, and tags for topic content using Gemini API."""
    try:
        from ..services.gemini_service import get_gemini_service
        
        title = request.get("title", "")
        content = request.get("content", "")
        excerpt = request.get("excerpt")
        
        if not title:
            return error_response(
                message="Title is required",
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        # For topics, content might be in config.components format
        # Try to extract text from components if content is empty
        if not content:
            config = request.get("config", {})
            components = config.get("components", [])
            # Extract text from components
            text_parts = []
            for comp in components:
                if comp.get("type") == "heading" and comp.get("text"):
                    text_parts.append(comp.get("text"))
                elif comp.get("type") == "rich_text" and comp.get("content"):
                    # Remove HTML tags
                    import re
                    plain_text = re.sub(r'<[^>]+>', '', comp.get("content", ""))
                    text_parts.append(plain_text)
                elif comp.get("type") == "image_text" and comp.get("content"):
                    text_parts.append(comp.get("content"))
                elif comp.get("type") == "prompts" and comp.get("items"):
                    for item in comp.get("items", []):
                        if item.get("prompt"):
                            text_parts.append(item.get("prompt"))
            content = " ".join(text_parts)
        
        if not content:
            return error_response(
                message="Content is required. Please add some components or content.",
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        # Generate content using Gemini (pass db session)
        gemini_service = get_gemini_service(db_session=db)
        generated = gemini_service.generate_blog_seo(
            title=title,
            content=content,
            excerpt=excerpt
        )
        
        return success_response(
            data=generated,
            message="SEO content generated successfully"
        )
        
    except ValueError as e:
        # API key not configured
        return error_response(
            message=f"Gemini API is not configured: {str(e)}。Please configure it in the Admin Panel.",
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE
        )
    except Exception as e:
        error_message = str(e)
        logger.error(f"Error generating topic SEO content: {error_message}")
        
        # Return appropriate status code based on error type
        status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        if "overloaded" in error_message or "overloaded" in error_message.lower() or "unavailable" in error_message.lower():
            status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        elif "quota" in error_message.lower() or "rate limit" in error_message.lower() or "429" in error_message:
            status_code = status.HTTP_429_TOO_MANY_REQUESTS
        
        return error_response(
            message=f"Generation failed: {error_message}",
            status_code=status_code
        )
