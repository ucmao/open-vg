"""
Admin routes for managing virtual users (sockpuppets).
"""
import random
import secrets
import string
import os
import json
import psycopg2
from fastapi import APIRouter, Depends, status, Query, UploadFile, File, Form
from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import Optional, List
from pydantic import BaseModel, Field
import httpx
from io import BytesIO
from datetime import datetime, timezone, timedelta
import csv
import pandas as pd

from ..models.base import get_db
from ..models.admin import Admin
from ..models.user import User, UserSource, Gender
from ..models.work import Work, WorkType, WorkStatus, ShareStatus
from ..models.comment import Comment
from ..models.like import Like
from ..models.favorite import Favorite
from ..utils.auth import get_current_admin
from ..utils.handle import generate_handle
from ..utils.responses import success_response, error_response, paginated_response
from ..utils.logger import logger
from ..utils.work_metadata import generate_work_metadata
from ..services.storage import get_storage_service
from ..utils.url_slug import generate_url_slug

try:
    from faker import Faker
    fake = Faker('en_US')
except ImportError:
    raise ImportError("Please install faker: pip install faker")

router = APIRouter()


class CreateVirtualUserRequest(BaseModel):
    """Request model for creating virtual users."""
    count: int = Field(1, ge=1, le=20, description="Number of users to create")
    nickname: Optional[str] = Field(None, description="Custom nickname (only used when count=1)")
    gender: Optional[str] = Field(None, description="Gender: male, female, or random")
    bio: Optional[str] = Field(None, description="Custom bio (only used when count=1)")
    location: Optional[str] = Field(None, description="Custom location (only used when count=1)")


class ImportWorksRequest(BaseModel):
    """Request model for importing works."""
    prompt_ids: Optional[List[int]] = Field(None, description="List of prompt_id to import (optional)")
    user_id: int = Field(..., description="Target virtual user ID")
    model_names: List[str] = Field(..., description="List of model names for replacement")
    count: Optional[int] = Field(None, ge=1, le=10, description="Number of works to import (1-10)")
    media_type: Optional[str] = Field(None, description="Media type filter: image or video")


class EngageWorksRequest(BaseModel):
    """Request model for engaging with works (views, likes, favorites, comments)."""
    user_ids: List[int] = Field(..., description="List of virtual user IDs to engage")
    view_count: int = Field(0, ge=0, le=100, description="Number of works to add views (0-100)")
    favorite_count: int = Field(0, ge=0, le=10, description="Number of works to add favorites (0-10)")
    like_count: int = Field(0, ge=0, le=20, description="Number of works to add likes (0-20)")
    comment_count: int = Field(0, ge=0, le=5, description="Number of works to add comments (0-5)")
    comment_contents: List[str] = Field(default_factory=list, description="List of comment contents to randomly select from")


def get_origin_db_connection():
    """Get connection to origin database."""
    origin_db_url = os.getenv("ORIGIN_DATABASE_URL")
    if not origin_db_url:
        raise Exception("ORIGIN_DATABASE_URL not configured")
    return psycopg2.connect(origin_db_url)


async def download_and_upload_avatar(user_id: int) -> Optional[str]:
    """
    Download avatar from pravatar.cc and upload to R2.
    
    Args:
        user_id: User ID (unique number, better for pravatar)
    
    Returns:
        Avatar URL in R2, or None if upload fails
    """
    try:
        # Use user ID directly (pravatar works better with numbers)
        avatar_url = f"https://i.pravatar.cc/150?u={user_id}"
        
        # Download avatar
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(avatar_url)
            response.raise_for_status()
            avatar_data = response.content
            
            # Detect content type from response
            content_type = response.headers.get('content-type', 'image/jpeg')
        
        # Upload to R2
        storage = get_storage_service()
        # Determine extension from content type
        ext = 'jpg'
        if 'png' in content_type:
            ext = 'png'
        elif 'gif' in content_type:
            ext = 'gif'
        elif 'webp' in content_type:
            ext = 'webp'
        
        key = storage.generate_key(filename=f"avatar.{ext}")
        
        # Convert bytes to BytesIO
        avatar_file = BytesIO(avatar_data)
        avatar_url_r2 = storage.upload_file(
            file_obj=avatar_file,
            key=key,
            content_type=content_type,
            public=False
        )
        
        logger.info(f"Avatar uploaded for virtual user {user_id}: {avatar_url_r2}")
        return avatar_url_r2
        
    except Exception as e:
        logger.error(f"Failed to upload avatar for virtual user {user_id}: {str(e)}")
        # Return None if upload fails (avatar_url will be None)
        return None


def generate_virtual_user_data(db: Session, custom_nickname: Optional[str] = None, 
                               custom_gender: Optional[str] = None,
                               custom_bio: Optional[str] = None,
                               custom_location: Optional[str] = None) -> dict:
    """
    Generate virtual user data using Faker.
    
    Args:
        db: Database session for handle generation
        custom_nickname: Optional custom nickname
        custom_gender: Optional gender (male/female)
        custom_bio: Optional custom bio
        custom_location: Optional custom location
    
    Returns:
        Dictionary with user data including created_at
    """
    # Determine gender
    if custom_gender and custom_gender in ['male', 'female']:
        gender = custom_gender
    else:
        gender = random.choice(['male', 'female'])
    
    # Generate name based on gender
    if custom_nickname:
        nickname = custom_nickname
    else:
        nickname = fake.name_male() if gender == 'male' else fake.name_female()
    
    # Generate other fields
    bio = custom_bio if custom_bio else fake.paragraph(nb_sentences=2)
    location = custom_location if custom_location else fake.city()
    
    # Generate unique email with popular domains (gmail, outlook, yahoo, hotmail, etc.)
    popular_domains = ['gmail.com', 'outlook.com', 'yahoo.com', 'hotmail.com', 'icloud.com', 'aol.com']
    max_email_attempts = 50
    email = None
    for _ in range(max_email_attempts):
        # Generate username part
        username = fake.user_name()
        # Use random popular domain
        domain = random.choice(popular_domains)
        candidate_email = f"{username}@{domain}"
        
        # Check database for uniqueness
        existing = db.query(User).filter(User.email == candidate_email).first()
        if not existing:
            email = candidate_email
            break
    
    if not email:
        raise Exception("Unable to generate unique email after maximum attempts")
    
    # Generate unique handle
    handle = generate_handle(db)
    
    # Generate random created_at time (between 30 days ago and now)
    now = datetime.now(timezone.utc)
    start_date = now - timedelta(days=30)
    created_at = fake.date_time_between(start_date=start_date, end_date=now)
    # Ensure timezone-aware datetime
    if created_at.tzinfo is None:
        created_at = created_at.replace(tzinfo=timezone.utc)
    
    return {
        "handle": handle,
        "email": email,
        "nickname": nickname,
        "gender": gender,
        "bio": bio,
        "location": location,
        "created_at": created_at,
    }


@router.post("/sockpuppets")
async def create_virtual_users(
    request: CreateVirtualUserRequest,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Create virtual users (sockpuppets).
    """
    try:
        created_users = []
        failed_count = 0
        
        for i in range(request.count):
            try:
                # Generate user data
                user_data = generate_virtual_user_data(
                    db=db,
                    custom_nickname=request.nickname if request.count == 1 else None,
                    custom_gender=request.gender,
                    custom_bio=request.bio if request.count == 1 else None,
                    custom_location=request.location if request.count == 1 else None
                )
                
                # Create user in database first (to get user ID)
                new_user = User(
                    handle=user_data["handle"],
                    email=user_data["email"],
                    nickname=user_data["nickname"],
                    bio=user_data["bio"],
                    location=user_data["location"],
                    gender=Gender(user_data["gender"]),
                    source=UserSource.ADMIN_CREATED,
                    # Virtual users attribute curated content only and cannot log in.
                    password_hash=None,
                    is_active=True,
                    email_verified=True,
                    total_credits=0,
                    created_at=user_data["created_at"],  # Set random creation time
                )
                
                db.add(new_user)
                db.flush()  # Get user ID without committing
                
                # Download and upload avatar (use user ID for better variety)
                avatar_url = await download_and_upload_avatar(
                    user_id=new_user.id
                )
                
                # Update avatar URL
                if avatar_url:
                    new_user.avatar_url = avatar_url
                
                db.flush()
                created_users.append(new_user.to_dict(db=db))
                
            except Exception as e:
                logger.error(f"Error creating virtual user {i+1}/{request.count}: {str(e)}")
                failed_count += 1
                # Continue with next user (don't rollback here, commit successful ones)
                continue
        
        # Commit all successful creations
        db.commit()
        
        logger.info(f"Admin {current_admin.id} created {len(created_users)} virtual users (failed: {failed_count})")
        
        return success_response(
            data={
                "created_count": len(created_users),
                "failed_count": failed_count,
                "users": created_users
            },
            message=f"Successfully created {len(created_users)} virtual user(s)" + (f" ({failed_count} failed)" if failed_count > 0 else ""),
            status_code=status.HTTP_201_CREATED
        )
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating virtual users: {str(e)}")
        return error_response(
            message="Failed to create virtual users",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.get("/sockpuppets")
async def get_virtual_users(
    page: int = 1,
    page_size: int = 20,
    search: Optional[str] = None,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Get list of virtual users (admin created users).
    """
    try:
        query = db.query(User).filter(User.source == UserSource.ADMIN_CREATED)
        
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                (User.nickname.ilike(search_term)) |
                (User.handle.ilike(search_term)) |
                (User.email.ilike(search_term))
            )
        
        total = query.count()
        
        users = query.order_by(User.id.desc()).offset((page - 1) * page_size).limit(page_size).all()
        
        items = [user.to_dict(db=db) for user in users]
        
        return paginated_response(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            message="Virtual users retrieved successfully"
        )
        
    except Exception as e:
        logger.error(f"Error getting virtual users: {str(e)}")
        return error_response(
            message="Failed to retrieve virtual users",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.delete("/sockpuppets/{user_id}")
async def delete_virtual_user(
    user_id: int,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Delete a virtual user.
    """
    try:
        user = db.query(User).filter(
            and_(User.id == user_id, User.source == UserSource.ADMIN_CREATED)
        ).first()
        
        if not user:
            return error_response(
                message="Virtual user not found",
                status_code=status.HTTP_404_NOT_FOUND
            )
        
        db.delete(user)
        db.commit()
        
        logger.info(f"Admin {current_admin.id} deleted virtual user {user_id}")
        
        return success_response(message="Virtual user deleted successfully")
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting virtual user: {str(e)}")
        return error_response(
            message="Failed to delete virtual user",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.get("/sockpuppets/import-works/stats")
async def get_import_works_stats(
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Get statistics of unimported works from origin database (count by media_type: image and video).
    """
    try:
        conn = get_origin_db_connection()
        cur = conn.cursor()
        
        # Count unimported image prompts
        image_count_sql = """
            SELECT COUNT(DISTINCT p.prompt_id)
            FROM prompts p
            JOIN assets a ON a.prompt_id = p.prompt_id
            WHERE p.is_imported = FALSE AND a.media_type = 'image'
        """
        cur.execute(image_count_sql)
        image_count = cur.fetchone()[0]
        
        # Count unimported video prompts
        video_count_sql = """
            SELECT COUNT(DISTINCT p.prompt_id)
            FROM prompts p
            JOIN assets a ON a.prompt_id = p.prompt_id
            WHERE p.is_imported = FALSE AND a.media_type = 'video'
        """
        cur.execute(video_count_sql)
        video_count = cur.fetchone()[0]
        
        cur.close()
        conn.close()
        
        return success_response(
            data={
                "image_count": image_count,
                "video_count": video_count,
                "total_count": image_count + video_count
            },
            message="Import statistics retrieved successfully"
        )
        
    except Exception as e:
        logger.error(f"Error getting import works statistics: {str(e)}")
        return error_response(
            message=f"Failed to get import statistics: {str(e)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.get("/sockpuppets/import-works/query")
async def query_origin_works(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: Optional[str] = Query(None),
    media_type: Optional[str] = Query(None),
    sort_by: Optional[str] = Query("view_count"),
    category: Optional[str] = Query(None),
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Query works from origin database for import.
    """
    try:
        conn = get_origin_db_connection()
        cur = conn.cursor()
        
        # Build query
        where_clauses = []
        params = []
        
        if media_type:
            where_clauses.append("a.media_type = %s")
            params.append(media_type)
        else:
            where_clauses.append("a.media_type IN ('image', 'video')")
        
        if category:
            where_clauses.append("p.category = %s")
            params.append(category)
        
        if search:
            where_clauses.append("(p.title ILIKE %s OR p.prompt_content ILIKE %s)")
            search_term = f"%{search}%"
            params.extend([search_term, search_term])
        
        where_sql = " AND ".join(where_clauses) if where_clauses else "1=1"
        
        # Sort order
        order_by_map = {
            "view_count": "p.view_count DESC",
            "fav_count": "p.fav_count DESC",
            "featured": "p.featured DESC, p.view_count DESC",
        }
        order_by = order_by_map.get(sort_by, "p.view_count DESC")
        
        # Count total
        count_sql = f"""
            SELECT COUNT(DISTINCT p.prompt_id)
            FROM prompts p
            JOIN assets a ON a.prompt_id = p.prompt_id
            WHERE {where_sql}
        """
        cur.execute(count_sql, params)
        total = cur.fetchone()[0]
        
        # Fetch data - use window function to get first asset per prompt
        # This avoids DISTINCT ON ordering issues
        query_sql = f"""
            SELECT DISTINCT ON (p.prompt_id)
                p.prompt_id,
                p.prompt_content,
                p.negative_prompt,
                p.title,
                p.model_used,
                p.tags,
                p.view_count,
                p.fav_count,
                p.featured,
                p.category,
                a.url as media_url,
                a.media_type,
                p.original_created_at
            FROM prompts p
            JOIN assets a ON a.prompt_id = p.prompt_id
            WHERE {where_sql}
            ORDER BY p.prompt_id, {order_by.split()[0]} DESC
            LIMIT %s OFFSET %s
        """
        
        # For sorting, we need to wrap in subquery if order by doesn't match distinct on
        # Simplified: just order by the first field in order_by
        first_order_field = order_by.split()[0] if order_by else "p.view_count"
        if first_order_field != "p.prompt_id":
            # Use subquery to handle ordering
            query_sql = f"""
                SELECT * FROM (
                    SELECT DISTINCT ON (p.prompt_id)
                        p.prompt_id,
                        p.prompt_content,
                        p.negative_prompt,
                        p.title,
                        p.model_used,
                        p.tags,
                        p.view_count,
                        p.fav_count,
                        p.featured,
                        p.category,
                        a.url as media_url,
                        a.media_type,
                        p.original_created_at
                    FROM prompts p
                    JOIN assets a ON a.prompt_id = p.prompt_id
                    WHERE {where_sql}
                    ORDER BY p.prompt_id
                ) sub
                ORDER BY {order_by}
                LIMIT %s OFFSET %s
            """
        
        offset = (page - 1) * page_size
        cur.execute(query_sql, params + [page_size, offset])
        rows = cur.fetchall()
        
        # Format results
        items = []
        for row in rows:
            (prompt_id, prompt_content, negative_prompt, title, model_used,
             tags, view_count, fav_count, featured, category, media_url,
             media_type, created_at) = row
            
            items.append({
                "prompt_id": prompt_id,
                "prompt": prompt_content or "",
                "negative_prompt": negative_prompt,
                "title": title or "",
                "model_used": model_used,
                "tags": tags or [],
                "view_count": view_count or 0,
                "fav_count": fav_count or 0,
                "featured": bool(featured),
                "category": category or "",
                "media_url": media_url,
                "media_type": media_type,
                "created_at": created_at.isoformat() if created_at else None,
            })
        
        cur.close()
        conn.close()
        
        return paginated_response(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            message="Origin works retrieved successfully"
        )
        
    except Exception as e:
        logger.error(f"Error querying origin works: {str(e)}")
        return error_response(
            message=f"Failed to query origin works: {str(e)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


async def download_and_import_work(
    db: Session,
    storage,
    prompt_id: int,
    work_data: dict,
    user_id: int,
    model_name: str,
    client: httpx.AsyncClient
) -> dict:
    """
    Download and import a single work.
    Returns result dict with success status.
    """
    logger.info(f"[DOWNLOAD] Starting download_and_import_work for prompt_id={prompt_id}, user_id={user_id}, model_name={model_name}")
    try:
        # Check if already exists
        logger.info(f"[DOWNLOAD] Checking if prompt_id {prompt_id} already exists")
        existing = db.query(Work).filter(Work.prompt_id == str(prompt_id)).first()
        if existing:
            logger.warning(f"[DOWNLOAD] prompt_id {prompt_id} already exists as work_id {existing.id}")
            return {"success": False, "reason": f"prompt_id {prompt_id} already exists", "prompt_id": prompt_id}
        logger.info(f"[DOWNLOAD] prompt_id {prompt_id} does not exist, proceeding")
        
        # Get user to get their registration time
        logger.info(f"[DOWNLOAD] Fetching user {user_id}")
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            logger.error(f"[DOWNLOAD] User {user_id} not found")
            return {"success": False, "reason": "User not found", "prompt_id": prompt_id}
        logger.info(f"[DOWNLOAD] User found: {user.nickname} (@{user.handle}), created_at: {user.created_at}")
        
        # Generate random created_at between user registration time and now
        user_created_at = user.created_at
        if user_created_at.tzinfo is None:
            user_created_at = user_created_at.replace(tzinfo=timezone.utc)
        
        now = datetime.now(timezone.utc)
        # Generate random time between user registration and now
        time_diff = (now - user_created_at).total_seconds()
        if time_diff > 0:
            random_seconds = random.uniform(0, time_diff)
            work_created_at = user_created_at + timedelta(seconds=random_seconds)
        else:
            # If user was just created, use current time
            work_created_at = now
        
        # Download file
        media_url = work_data["media_url"]
        logger.info(f"[DOWNLOAD] Starting download from URL: {media_url}")
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "Accept": "image/*,video/*,*/*",
            }
            logger.debug(f"[DOWNLOAD] Download headers: {headers}")
            resp = await client.get(media_url, headers=headers, follow_redirects=True, timeout=60.0)
            logger.info(f"[DOWNLOAD] Download response status: {resp.status_code}, content-type: {resp.headers.get('content-type')}")
            resp.raise_for_status()
            file_data = resp.content
            file_size = len(file_data)
            logger.info(f"[DOWNLOAD] Downloaded file size: {file_size} bytes")
            
            if file_size < 2000:
                logger.warning(f"[DOWNLOAD] File too small: {file_size} bytes < 2000 bytes")
                return {"success": False, "reason": "File too small", "prompt_id": prompt_id}
            logger.info(f"[DOWNLOAD] File size check passed: {file_size} bytes")
                
        except Exception as e:
            logger.error(f"[DOWNLOAD] Failed to download {media_url}: {str(e)}")
            import traceback
            logger.error(f"[DOWNLOAD] Download error traceback:\n{traceback.format_exc()}")
            return {"success": False, "reason": f"Download failed: {str(e)}", "prompt_id": prompt_id}
        
        # Prepare storage
        is_video = work_data["media_type"] == "video"
        file_ext = "mp4" if is_video else "jpg"
        logger.info(f"[DOWNLOAD] Media type: {work_data['media_type']}, is_video: {is_video}, file_ext: {file_ext}")
        
        file_key = storage.generate_key(filename=f"imported.{file_ext}")
        storage_key = file_key.split('.')[0]
        logger.info(f"[DOWNLOAD] Generated storage key: {file_key}, storage_key: {storage_key}")
        
        # Upload to storage
        logger.info(f"[DOWNLOAD] Uploading file to storage...")
        try:
            new_url = storage.upload_file(
                file_obj=BytesIO(file_data),
                key=file_key,
                content_type="video/mp4" if is_video else "image/jpeg"
            )
            logger.info(f"[DOWNLOAD] File uploaded successfully, new_url: {new_url}")
        except Exception as e:
            logger.error(f"[DOWNLOAD] Failed to upload file to storage: {str(e)}")
            import traceback
            logger.error(f"[DOWNLOAD] Upload error traceback:\n{traceback.format_exc()}")
            return {"success": False, "reason": f"Upload failed: {str(e)}", "prompt_id": prompt_id}
        
        # Generate SEO fields
        alphabet = string.ascii_letters + string.digits
        short_code = ''.join(secrets.choice(alphabet) for _ in range(11))
        
        prompt_clean = work_data.get("prompt") or ""
        
        # Handle thumbnail
        thumbnail_url = None
        if "aliyuncs.com" in new_url:
            sep = "&" if "?" in new_url else "?"
            if is_video:
                thumbnail_url = f"{new_url}{sep}x-oss-process=video/snapshot,t_0,f_jpg,w_480"
            else:
                thumbnail_url = f"{new_url}{sep}x-oss-process=image/resize,w_480"
        
        # Generate title and description using utility functions
        logger.info(f"[DOWNLOAD] Generating work metadata...")
        title, description = generate_work_metadata(prompt_clean, model_name)
        share_name = title  # share_name and title are the same
        logger.info(f"[DOWNLOAD] Generated title: {title[:50]}..., description length: {len(description)}")
        
        canonical_url = storage.generate_canonical_url(storage_key, title, file_ext)
        url_slug = generate_url_slug(short_code, title)
        logger.info(f"[DOWNLOAD] Generated canonical_url: {canonical_url}, url_slug: {url_slug}")
        
        # Create Work record
        # Use the random created_at generated above (between user registration and now)
        logger.info(f"[DOWNLOAD] Creating Work record with model_name: {model_name} (original was: {work_data.get('model_used')})")
        logger.info(f"[DOWNLOAD] Work created_at: {work_created_at}")
        
        # Get params from work_data (extracted from metadata)
        params = work_data.get("params")
        if params:
            logger.info(f"[DOWNLOAD] Found params in work_data for prompt_id={prompt_id}, params keys: {list(params.keys()) if isinstance(params, dict) else 'N/A'}")
        else:
            logger.debug(f"[DOWNLOAD] No params found in work_data for prompt_id={prompt_id}")
        
        try:
            work = Work(
            user_id=user_id,
            type=WorkType.TEXT2VIDEO if is_video else WorkType.TEXT2IMG,
            prompt=prompt_clean,
            prompt_id=str(prompt_id),  # Store as string
            negative_prompt=work_data.get("negative_prompt"),
            model_name=model_name,  # Randomly selected model name (replaces original)
            model_key="legacy_import",  # Placeholder
            params=params,  # Import params from metadata
            file_url=new_url,
            thumbnail_url=thumbnail_url,
            storage_key=storage_key,
            canonical_url=canonical_url,
            short_code=short_code,
            url_slug=url_slug,
            status=WorkStatus.SUCCESS,
            is_shared=True,
            share_status=ShareStatus.APPROVED,
            share_name=title,
            title=title,
            description=description,
            category=None,  #  category
            view_count=work_data.get("view_count") or 0,
            like_count=work_data.get("fav_count") or 0,
            favorite_count=work_data.get("fav_count") or 0,
            tags=work_data.get("tags") or [],
            created_at=work_created_at,  # Random time between user registration and now
            completed_at=work_created_at,  # Same as created_at for imported works
                source="PGC"
            )
            
            logger.info(f"[DOWNLOAD] Work object created, adding to database...")
            db.add(work)
            db.commit()
            db.refresh(work)
            logger.info(f"[DOWNLOAD] Work record created successfully: work_id={work.id}, prompt_id={prompt_id}")
            
            return {"success": True, "work_id": work.id, "prompt_id": prompt_id}
        except Exception as e:
            db.rollback()
            logger.error(f"[DOWNLOAD] Failed to create Work record: {str(e)}")
            import traceback
            logger.error(f"[DOWNLOAD] Work creation error traceback:\n{traceback.format_exc()}")
            return {"success": False, "reason": f"Database error: {str(e)}", "prompt_id": prompt_id}
        
    except Exception as e:
        db.rollback()
        logger.error(f"[DOWNLOAD] CRITICAL ERROR importing work {prompt_id}: {str(e)}")
        import traceback
        logger.error(f"[DOWNLOAD] Critical error traceback:\n{traceback.format_exc()}")
        return {"success": False, "reason": str(e), "prompt_id": prompt_id}


@router.post("/sockpuppets/import-works")
async def import_works(
    request: ImportWorksRequest,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Import works from origin database.
    Can import by prompt_ids list or by count (auto-select from origin DB).
    """
    try:
        # Log received parameters for debugging
        logger.info(f"[IMPORT] Starting import works request - user_id: {request.user_id}, model_names: {request.model_names}, count: {request.count}, prompt_ids: {request.prompt_ids}, media_type: {request.media_type}")
        
        # Verify target user
        logger.info(f"[IMPORT] Verifying target user {request.user_id}")
        target_user = db.query(User).filter(
            and_(User.id == request.user_id, User.source == UserSource.ADMIN_CREATED)
        ).first()
        if not target_user:
            logger.error(f"[IMPORT] Target virtual user {request.user_id} not found or not ADMIN_CREATED")
            return error_response(
                message="Target virtual user not found",
                status_code=status.HTTP_404_NOT_FOUND
            )
        logger.info(f"[IMPORT] Target user verified: {target_user.nickname} (@{target_user.handle})")
        
        # Get origin database connection
        logger.info(f"[IMPORT] Connecting to origin database...")
        try:
            conn = get_origin_db_connection()
            cur = conn.cursor()
            logger.info(f"[IMPORT] Successfully connected to origin database")
        except Exception as e:
            logger.error(f"[IMPORT] Failed to connect to origin database: {str(e)}")
            raise
        
        # Determine which works to import
        if request.count and request.count > 0:
            logger.info(f"[IMPORT] Import mode: BY COUNT (count={request.count})")
            # Import by count - fetch from origin DB
            where_clauses = []
            params = []
            
            # Filter by is_imported = FALSE (only import not-yet-imported works)
            where_clauses.append("p.is_imported = FALSE")
            
            if request.media_type:
                where_clauses.append("a.media_type = %s")
                params.append(request.media_type)
                logger.info(f"[IMPORT] Media type filter: {request.media_type}")
            else:
                where_clauses.append("a.media_type IN ('image', 'video')")
                logger.info(f"[IMPORT] Media type filter: image or video")
            
            where_sql = " AND ".join(where_clauses) if where_clauses else "1=1"
            logger.info(f"[IMPORT] WHERE clause: {where_sql}")
            
            # Fetch works from origin, ordered by rank_score DESC
            query_sql = f"""
                SELECT DISTINCT ON (p.prompt_id)
                    p.prompt_id,
                    p.prompt_content,
                    p.negative_prompt,
                    p.title,
                    p.model_used,
                    p.tags,
                    p.view_count,
                    p.fav_count,
                    p.featured,
                    p.category,
                    a.url as media_url,
                    a.media_type,
                    p.original_created_at,
                    p.rank_score,
                    p.metadata
                FROM prompts p
                JOIN assets a ON a.prompt_id = p.prompt_id
                WHERE {where_sql}
                ORDER BY p.prompt_id, p.rank_score DESC
            """
            
            # Use subquery for final ordering by rank_score DESC
            query_sql = f"""
                SELECT * FROM (
                    {query_sql}
                ) sub
                ORDER BY rank_score DESC
                LIMIT %s
            """
            params.append(request.count)
            
            logger.info(f"[IMPORT] Executing query with params: {params}")
            logger.debug(f"[IMPORT] Query SQL: {query_sql}")
            try:
                cur.execute(query_sql, params)
                rows = cur.fetchall()
                logger.info(f"[IMPORT] Query executed successfully, returned {len(rows)} rows")
            except Exception as e:
                logger.error(f"[IMPORT] Query execution failed: {str(e)}")
                logger.error(f"[IMPORT] Query was: {query_sql}")
                logger.error(f"[IMPORT] Params were: {params}")
                raise
            
            # Extract prompt_ids
            prompt_ids = [row[0] for row in rows]
            logger.info(f"[IMPORT] Extracted {len(prompt_ids)} prompt_ids: {prompt_ids[:10]}{'...' if len(prompt_ids) > 10 else ''}")
            
        elif request.prompt_ids and len(request.prompt_ids) > 0:
            logger.info(f"[IMPORT] Import mode: BY PROMPT_IDS (count={len(request.prompt_ids)})")
            # Import by prompt_ids list
            prompt_ids = request.prompt_ids
            logger.info(f"[IMPORT] Prompt IDs to import: {prompt_ids}")
            placeholders = ','.join(['%s'] * len(prompt_ids))
            query_sql = f"""
                SELECT DISTINCT ON (p.prompt_id)
                    p.prompt_id,
                    p.prompt_content,
                    p.negative_prompt,
                    p.title,
                    p.model_used,
                    p.tags,
                    p.view_count,
                    p.fav_count,
                    p.featured,
                    p.category,
                    a.url as media_url,
                    a.media_type,
                    p.original_created_at,
                    p.metadata
                FROM prompts p
                JOIN assets a ON a.prompt_id = p.prompt_id
                WHERE p.prompt_id IN ({placeholders})
                ORDER BY p.prompt_id, a.asset_id
            """
            logger.info(f"[IMPORT] Executing query for prompt_ids")
            logger.debug(f"[IMPORT] Query SQL: {query_sql}")
            try:
                cur.execute(query_sql, prompt_ids)
                rows = cur.fetchall()
                logger.info(f"[IMPORT] Query executed successfully, returned {len(rows)} rows")
            except Exception as e:
                logger.error(f"[IMPORT] Query execution failed: {str(e)}")
                logger.error(f"[IMPORT] Query was: {query_sql}")
                logger.error(f"[IMPORT] Prompt IDs were: {prompt_ids}")
                raise
        else:
            cur.close()
            conn.close()
            return error_response(
                message="Either prompt_ids or count must be provided",
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        # Build work data dict
        logger.info(f"[IMPORT] Building works_data dict from {len(rows)} rows")
        works_data = {}
        for idx, row in enumerate(rows):
            try:
                # Handle different row lengths:
                # - 15 fields: with rank_score and metadata (BY COUNT mode)
                # - 14 fields: with metadata but no rank_score (BY PROMPT_IDS mode)
                # - 14 fields: with rank_score but no metadata (legacy BY COUNT mode)
                # - 13 fields: without rank_score and metadata (legacy BY PROMPT_IDS mode)
                row_len = len(row)
                if row_len == 15:
                    (prompt_id, prompt_content, negative_prompt, title, model_used,
                     tags, view_count, fav_count, featured, category, media_url,
                     media_type, created_at, rank_score, metadata) = row
                    logger.debug(f"[IMPORT] Row {idx}: prompt_id={prompt_id}, has rank_score={rank_score}, metadata={metadata is not None}")
                elif row_len == 14:
                    # Check if last field is metadata (dict/JSONB) or rank_score (number)
                    # BY PROMPT_IDS mode: last field is metadata (after created_at)
                    # Legacy BY COUNT mode: last field is rank_score (after created_at)
                    last_field = row[-1]
                    # If last field is a dict or looks like metadata, it's BY PROMPT_IDS mode
                    # Otherwise, if it's a number, it might be rank_score (legacy)
                    if isinstance(last_field, dict) or (isinstance(last_field, str) and last_field.startswith('{')):
                        # BY PROMPT_IDS mode: has metadata, no rank_score
                        (prompt_id, prompt_content, negative_prompt, title, model_used,
                         tags, view_count, fav_count, featured, category, media_url,
                         media_type, created_at, metadata) = row
                        rank_score = None
                        logger.debug(f"[IMPORT] Row {idx}: prompt_id={prompt_id}, no rank_score, metadata={metadata is not None}")
                    else:
                        # Legacy BY COUNT mode: has rank_score, no metadata
                        (prompt_id, prompt_content, negative_prompt, title, model_used,
                         tags, view_count, fav_count, featured, category, media_url,
                         media_type, created_at, rank_score) = row
                        metadata = None
                        logger.debug(f"[IMPORT] Row {idx}: prompt_id={prompt_id}, has rank_score={rank_score}, no metadata")
                else:
                    # Legacy mode: 13 fields without rank_score and metadata
                    (prompt_id, prompt_content, negative_prompt, title, model_used,
                     tags, view_count, fav_count, featured, category, media_url,
                     media_type, created_at) = row
                    rank_score = None
                    metadata = None
                    logger.debug(f"[IMPORT] Row {idx}: prompt_id={prompt_id}, no rank_score, no metadata (13 fields)")
                
                # Extract params from metadata
                # metadata is JSONB from PostgreSQL, which psycopg2 automatically converts to Python dict
                # Work.params is SQLAlchemy JSON column, which accepts dict and auto-serializes to JSON on save
                params = None
                if metadata:
                    try:
                        # metadata from JSONB is automatically converted to dict by psycopg2
                        if isinstance(metadata, dict):
                            # Use metadata dict directly as params - SQLAlchemy JSON column will serialize it
                            params = metadata
                            logger.debug(f"[IMPORT] Using metadata (JSONB->dict) as params for prompt_id={prompt_id}")
                        elif isinstance(metadata, str):
                            # Try to parse JSON string if metadata is stored as string
                            parsed_metadata = json.loads(metadata)
                            if isinstance(parsed_metadata, dict):
                                params = parsed_metadata
                                logger.debug(f"[IMPORT] Parsed JSON string metadata and used as params for prompt_id={prompt_id}")
                            else:
                                logger.warning(f"[IMPORT] Parsed metadata is not a dict for prompt_id={prompt_id}, skipping params")
                                params = None
                        else:
                            logger.warning(f"[IMPORT] Metadata is not dict or string for prompt_id={prompt_id}, type: {type(metadata)}, skipping params")
                            params = None
                    except Exception as e:
                        logger.warning(f"[IMPORT] Failed to extract params from metadata for prompt_id={prompt_id}: {str(e)}, metadata={metadata}")
                        params = None
                
                works_data[prompt_id] = {
                    "prompt": prompt_content,
                    "negative_prompt": negative_prompt,
                    "title": title,
                    "model_used": model_used,
                    "tags": tags,
                    "view_count": view_count,
                    "fav_count": fav_count,
                    "featured": featured,
                    "category": category,
                    "media_url": media_url,
                    "media_type": media_type,
                    "created_at": created_at,
                    "params": params,  # Add params from metadata
                }
                logger.debug(f"[IMPORT] Added work_data for prompt_id={prompt_id}, media_url={media_url}, media_type={media_type}, params={params is not None}")
            except Exception as e:
                logger.error(f"[IMPORT] Error parsing row {idx}: {str(e)}, row length: {len(row)}")
                raise
        
        logger.info(f"[IMPORT] Built works_data dict with {len(works_data)} entries")
        cur.close()
        conn.close()
        logger.info(f"[IMPORT] Closed origin database connection")
        
        # Import works
        logger.info(f"[IMPORT] Starting to import {len(prompt_ids)} works")
        storage = get_storage_service()
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "image/*,video/*,*/*",
        }
        
        results = []
        async with httpx.AsyncClient(headers=headers, follow_redirects=True, timeout=60.0) as client:
            for idx, prompt_id in enumerate(prompt_ids):
                logger.info(f"[IMPORT] Processing work {idx + 1}/{len(prompt_ids)}: prompt_id={prompt_id}")
                
                if prompt_id not in works_data:
                    logger.warning(f"[IMPORT] prompt_id {prompt_id} not found in works_data")
                    results.append({
                        "success": False,
                        "reason": "Work not found in origin database",
                        "prompt_id": prompt_id
                    })
                    continue
                
                # Randomly select model name from the list
                if request.model_names and len(request.model_names) > 0:
                    model_name = random.choice(request.model_names)
                    logger.info(f"[IMPORT] Selected random model name: {model_name} from list: {request.model_names}")
                else:
                    model_name = "Flux"
                    logger.warning(f"[IMPORT] No model names provided, using default: {model_name}")
                
                logger.info(f"[IMPORT] Calling download_and_import_work for prompt_id={prompt_id}")
                result = await download_and_import_work(
                    db=db,
                    storage=storage,
                    prompt_id=prompt_id,
                    work_data=works_data[prompt_id],
                    user_id=request.user_id,
                    model_name=model_name,
                    client=client
                )
                logger.info(f"[IMPORT] download_and_import_work result for prompt_id={prompt_id}: success={result.get('success')}, reason={result.get('reason', 'N/A')}")
                results.append(result)
        
        # Mark successfully imported works as is_imported = TRUE in origin database
        success_count = sum(1 for r in results if r.get("success"))
        failed_count = len(results) - success_count
        logger.info(f"[IMPORT] Import summary: success={success_count}, failed={failed_count}, total={len(results)}")
        
        # Log detailed results
        for idx, result in enumerate(results):
            if result.get("success"):
                logger.info(f"[IMPORT] Result {idx + 1}: SUCCESS - prompt_id={result.get('prompt_id')}, work_id={result.get('work_id')}")
            else:
                logger.warning(f"[IMPORT] Result {idx + 1}: FAILED - prompt_id={result.get('prompt_id')}, reason={result.get('reason')}")
        
        if success_count > 0:
            # Reconnect to origin database to update is_imported flag
            logger.info(f"[IMPORT] Updating is_imported flag for {success_count} successful imports")
            origin_conn = get_origin_db_connection()
            origin_cur = origin_conn.cursor()
            try:
                successful_prompt_ids = [r.get("prompt_id") for r in results if r.get("success")]
                if successful_prompt_ids:
                    logger.info(f"[IMPORT] Marking {len(successful_prompt_ids)} prompts as imported: {successful_prompt_ids}")
                    placeholders = ','.join(['%s'] * len(successful_prompt_ids))
                    update_sql = f"""
                        UPDATE prompts
                        SET is_imported = TRUE
                        WHERE prompt_id IN ({placeholders})
                    """
                    origin_cur.execute(update_sql, successful_prompt_ids)
                    origin_conn.commit()
                    logger.info(f"[IMPORT] Successfully marked {len(successful_prompt_ids)} prompts as imported in origin database")
            except Exception as e:
                logger.error(f"[IMPORT] Failed to update is_imported flag in origin database: {str(e)}")
                import traceback
                logger.error(traceback.format_exc())
                # Don't fail the whole import if marking fails
            finally:
                origin_cur.close()
                origin_conn.close()
        
        logger.info(f"[IMPORT] Final summary - Admin {current_admin.id} imported {success_count} works (failed: {failed_count})")
        
        return success_response(
            data={
                "success_count": success_count,
                "failed_count": failed_count,
                "results": results
            },
            message=f"Successfully imported {success_count} works" + (f" ({failed_count} failed)" if failed_count > 0 else "")
        )
        
    except Exception as e:
        logger.error(f"[IMPORT] CRITICAL ERROR importing works: {str(e)}")
        import traceback
        logger.error(f"[IMPORT] Traceback:\n{traceback.format_exc()}")
        return error_response(
            message=f"Failed to import works: {str(e)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.post("/sockpuppets/engage-works")
async def engage_works(
    request: EngageWorksRequest,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Engage with works for virtual users (add views, favorites, likes, comments).
    For each user, randomly select works and apply engagement in order:
    1. Add views to random works
    2. Add favorites to random works
    3. Add likes to random works
    4. Add comments to random works
    """
    try:
        results = []
        total_success = 0
        total_failed = 0
        
        # Process each user sequentially
        for user_id in request.user_ids:
            user_result = {
                "user_id": user_id,
                "success": True,
                "message": "",
                "details": {
                    "views_added": 0,
                    "favorites_added": 0,
                    "likes_added": 0,
                    "comments_added": 0
                }
            }
            
            try:
                # Verify user exists and is a virtual user
                user = db.query(User).filter(
                    and_(User.id == user_id, User.source == UserSource.ADMIN_CREATED)
                ).first()
                
                if not user:
                    user_result["success"] = False
                    user_result["message"] = "Virtual user not found"
                    results.append(user_result)
                    total_failed += 1
                    continue
                
                # Get all works for this user
                all_works = db.query(Work).filter(
                    Work.user_id == user_id,
                    Work.is_shared == True
                ).all()
                
                if not all_works:
                    user_result["success"] = False
                    user_result["message"] = "No works found for this user"
                    results.append(user_result)
                    total_failed += 1
                    continue
                
                # Helper function to generate random timestamp between start_time and now
                def random_timestamp(start_time):
                    """Generate random timestamp between start_time and now."""
                    now = datetime.now(timezone.utc)
                    if start_time > now:
                        return now
                    time_diff = (now - start_time).total_seconds()
                    random_seconds = random.uniform(0, time_diff)
                    return start_time + timedelta(seconds=random_seconds)
                
                # Get user creation time
                user_created_at = user.created_at if user.created_at else datetime.now(timezone.utc)
                now = datetime.now(timezone.utc)
                
                # Shuffle works for random selection
                works_list = list(all_works)
                random.shuffle(works_list)
                
                # 1. Add views to random works
                if request.view_count > 0:
                    view_works = works_list[:min(request.view_count, len(works_list))]
                    for work in view_works:
                        # Simply increment view_count (1-20 views per work)
                        # No need to create View records for anonymous views
                        view_increment = random.randint(1, 20)
                        work.view_count = (work.view_count or 0) + view_increment
                        user_result["details"]["views_added"] += 1
                
                # 2. Add favorites to random works (different from views)
                if request.favorite_count > 0:
                    # Get works that weren't used for views
                    favorite_candidates = works_list[request.view_count:] if request.view_count < len(works_list) else []
                    if not favorite_candidates:
                        favorite_candidates = works_list
                    random.shuffle(favorite_candidates)
                    favorite_works = favorite_candidates[:min(request.favorite_count, len(favorite_candidates))]
                    for work in favorite_works:
                        # Calculate start time: max(user_created_at, work.created_at)
                        work_created_at = work.created_at if work.created_at else user_created_at
                        start_time = max(user_created_at, work_created_at)
                        
                        # Create favorite record with random timestamp
                        favorite_timestamp = random_timestamp(start_time)
                        
                        # Check if favorite already exists (unique constraint)
                        existing_favorite = db.query(Favorite).filter(
                            Favorite.user_id == user_id,
                            Favorite.work_id == work.id
                        ).first()
                        
                        if not existing_favorite:
                            new_favorite = Favorite(
                                user_id=user_id,
                                work_id=work.id,
                                created_at=favorite_timestamp
                            )
                            db.add(new_favorite)
                            work.favorite_count = (work.favorite_count or 0) + 1
                            user_result["details"]["favorites_added"] += 1
                
                # 3. Add likes to random works (different from views and favorites)
                if request.like_count > 0:
                    used_indices = set(range(min(request.view_count, len(works_list))))
                    used_indices.update(range(request.view_count, request.view_count + min(request.favorite_count, len(works_list) - request.view_count)))
                    like_candidates = [w for i, w in enumerate(works_list) if i not in used_indices]
                    if not like_candidates:
                        like_candidates = works_list
                    random.shuffle(like_candidates)
                    like_works = like_candidates[:min(request.like_count, len(like_candidates))]
                    for work in like_works:
                        # Calculate start time: max(user_created_at, work.created_at)
                        work_created_at = work.created_at if work.created_at else user_created_at
                        start_time = max(user_created_at, work_created_at)
                        
                        # Create like record with random timestamp
                        like_timestamp = random_timestamp(start_time)
                        
                        # Check if like already exists (unique constraint)
                        existing_like = db.query(Like).filter(
                            Like.user_id == user_id,
                            Like.work_id == work.id
                        ).first()
                        
                        if not existing_like:
                            new_like = Like(
                                user_id=user_id,
                                work_id=work.id,
                                created_at=like_timestamp
                            )
                            db.add(new_like)
                            work.like_count = (work.like_count or 0) + 1
                            user_result["details"]["likes_added"] += 1
                
                # 4. Add comments to random works
                if request.comment_count > 0 and request.comment_contents:
                    used_indices = set(range(min(request.view_count, len(works_list))))
                    used_indices.update(range(request.view_count, request.view_count + min(request.favorite_count, len(works_list) - request.view_count)))
                    used_indices.update(range(request.view_count + request.favorite_count, request.view_count + request.favorite_count + min(request.like_count, len(works_list) - request.view_count - request.favorite_count)))
                    comment_candidates = [w for i, w in enumerate(works_list) if i not in used_indices]
                    if not comment_candidates:
                        comment_candidates = works_list
                    random.shuffle(comment_candidates)
                    comment_works = comment_candidates[:min(request.comment_count, len(comment_candidates))]
                    
                    for work in comment_works:
                        # Calculate start time: max(user_created_at, work.created_at, last_comment_time)
                        work_created_at = work.created_at if work.created_at else user_created_at
                        start_time = max(user_created_at, work_created_at)
                        
                        # Get last comment time for this work
                        last_comment = db.query(Comment).filter(
                            Comment.work_id == work.id
                        ).order_by(Comment.created_at.desc()).first()
                        
                        if last_comment and last_comment.created_at:
                            start_time = max(start_time, last_comment.created_at)
                        
                        # Randomly select a comment content
                        comment_content = random.choice(request.comment_contents)
                        
                        # Create comment with random timestamp
                        comment_timestamp = random_timestamp(start_time)
                        new_comment = Comment(
                            work_id=work.id,
                            user_id=user_id,
                            content=comment_content,
                            parent_id=None,
                            created_at=comment_timestamp
                        )
                        db.add(new_comment)
                        user_result["details"]["comments_added"] += 1
                
                db.commit()
                user_result["message"] = "Engagement added successfully"
                results.append(user_result)
                total_success += 1
                
                logger.info(f"Engaged works for user {user_id}: views={user_result['details']['views_added']}, "
                          f"favorites={user_result['details']['favorites_added']}, "
                          f"likes={user_result['details']['likes_added']}, "
                          f"comments={user_result['details']['comments_added']}")
                
            except Exception as e:
                db.rollback()
                user_result["success"] = False
                user_result["message"] = f"Error: {str(e)}"
                results.append(user_result)
                total_failed += 1
                logger.error(f"Error engaging works for user {user_id}: {str(e)}")
                import traceback
                logger.error(traceback.format_exc())
        
        logger.info(f"Admin {current_admin.id} engaged works for {len(request.user_ids)} users: "
                   f"success={total_success}, failed={total_failed}")
        
        return success_response(
            data={
                "success_count": total_success,
                "failed_count": total_failed,
                "results": results
            },
            message=f"Engagement completed: {total_success} successful, {total_failed} failed"
        )
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error in engage_works: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return error_response(
            message=f"Failed to engage works: {str(e)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.post("/sockpuppets/create-work")
async def create_work(
    user_id: int = Form(...),
    model_name: str = Form(...),
    prompt: str = Form(...),
    work_type: str = Form(...),
    url: str = Form(...),
    category: Optional[str] = Form(None),
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Create a single work manually (from user input).
    """
    try:
        # Verify target user
        target_user = db.query(User).filter(
            and_(User.id == user_id, User.source == UserSource.ADMIN_CREATED)
        ).first()
        if not target_user:
            return error_response(
                message="Target virtual user not found",
                status_code=status.HTTP_404_NOT_FOUND
            )
        
        # Validate work_type
        valid_types = ["text2img", "text-to-image", "img2img", "image-to-image", "text2video", "text-to-video", "img2video", "image-to-video"]
        if work_type not in valid_types:
            return error_response(
                message=f"Invalid work_type. Must be one of: {', '.join(valid_types)}",
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        # Map work_type to WorkType enum
        type_map = {
            "text2img": WorkType.TEXT2IMG,
            "text-to-image": WorkType.TEXT2IMG,
            "img2img": WorkType.IMG2IMG,
            "image-to-image": WorkType.IMG2IMG,
            "text2video": WorkType.TEXT2VIDEO,
            "text-to-video": WorkType.TEXT2VIDEO,
            "img2video": WorkType.IMG2VIDEO,
            "image-to-video": WorkType.IMG2VIDEO,
        }
        work_type_enum = type_map[work_type]
        is_video = work_type in ["text2video", "img2video", "text-to-video", "image-to-video"]
        
        # Download file from URL
        storage = get_storage_service()
        async with httpx.AsyncClient() as client:
            try:
                headers = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                    "Accept": "image/*,video/*,*/*",
                }
                resp = await client.get(url, headers=headers, follow_redirects=True, timeout=60.0)
                resp.raise_for_status()
                file_data = resp.content
                
                if len(file_data) < 2000:
                    return error_response(
                        message="File too small",
                        status_code=status.HTTP_400_BAD_REQUEST
                    )
            except Exception as e:
                logger.error(f"Failed to download {url}: {str(e)}")
                return error_response(
                    message=f"Failed to download file: {str(e)}",
                    status_code=status.HTTP_400_BAD_REQUEST
                )
        
        # Upload to storage
        file_ext = "mp4" if is_video else "jpg"
        file_key = storage.generate_key(filename=f"manual.{file_ext}")
        storage_key = file_key.split('.')[0]
        
        new_url = storage.upload_file(
            file_obj=BytesIO(file_data),
            key=file_key,
            content_type="video/mp4" if is_video else "image/jpeg"
        )
        
        # Generate SEO fields
        alphabet = string.ascii_letters + string.digits
        short_code = ''.join(secrets.choice(alphabet) for _ in range(11))
        
        # Handle thumbnail
        thumbnail_url = None
        if "aliyuncs.com" in new_url:
            sep = "&" if "?" in new_url else "?"
            if is_video:
                thumbnail_url = f"{new_url}{sep}x-oss-process=video/snapshot,t_0,f_jpg,w_480"
            else:
                thumbnail_url = f"{new_url}{sep}x-oss-process=image/resize,w_480"
        
        # Generate title and description using utility functions
        prompt_clean = prompt.strip()  # Clean prompt for storage
        title, description = generate_work_metadata(prompt_clean, model_name)
        share_name = title
        
        canonical_url = storage.generate_canonical_url(storage_key, title, file_ext)
        url_slug = generate_url_slug(short_code, title)
        
        # Generate random created_at between user registration and now
        user_created_at = target_user.created_at
        if user_created_at.tzinfo is None:
            user_created_at = user_created_at.replace(tzinfo=timezone.utc)
        
        now = datetime.now(timezone.utc)
        time_diff = (now - user_created_at).total_seconds()
        if time_diff > 0:
            random_seconds = random.uniform(0, time_diff)
            work_created_at = user_created_at + timedelta(seconds=random_seconds)
        else:
            work_created_at = now
        
        # Create Work record
        work = Work(
            user_id=user_id,
            type=work_type_enum,
            prompt=prompt_clean,
            model_name=model_name,
            model_key="manual_import",
            file_url=new_url,
            thumbnail_url=thumbnail_url,
            storage_key=storage_key,
            canonical_url=canonical_url,
            short_code=short_code,
            url_slug=url_slug,
            status=WorkStatus.SUCCESS,
            is_shared=True,
            share_status=ShareStatus.APPROVED,
            share_name=title,
            title=title,
            description=description,
            category=category,  # Use provided category or None
            view_count=0,
            like_count=0,
            favorite_count=0,
            tags=[],
            created_at=work_created_at,
            completed_at=work_created_at,
            source="PGC"
        )
        
        db.add(work)
        db.commit()
        db.refresh(work)
        
        logger.info(f"Admin {current_admin.id} created work {work.id} for user {user_id}")
        
        return success_response(
            data={"work_id": work.id},
            message="Work created successfully"
        )
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating work: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return error_response(
            message=f"Failed to create work: {str(e)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.post("/sockpuppets/batch-import-works")
async def batch_import_works(
    user_id: int = Form(...),
    file: UploadFile = File(...),
    category: Optional[str] = Form(None),
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Batch import works from CSV/Excel file.
    File format: model_name, prompt, work_type, url
    """
    try:
        # Verify target user
        target_user = db.query(User).filter(
            and_(User.id == user_id, User.source == UserSource.ADMIN_CREATED)
        ).first()
        if not target_user:
            return error_response(
                message="Target virtual user not found",
                status_code=status.HTTP_404_NOT_FOUND
            )
        
        # Read file
        file_ext = file.filename.split('.')[-1].lower() if file.filename else ''
        content = await file.read()
        
        # Parse CSV or Excel
        rows = []
        try:
            if file_ext in ['xlsx', 'xls']:
                df = pd.read_excel(BytesIO(content))
                rows = df.to_dict('records')
            else:
                # CSV
                content_str = content.decode('utf-8-sig')  # Handle BOM
                csv_reader = csv.DictReader(content_str.splitlines())
                rows = list(csv_reader)
        except Exception as e:
            logger.error(f"Failed to parse file: {str(e)}")
            return error_response(
                message=f"Failed to parse file: {str(e)}",
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        if not rows:
            return error_response(
                message="File is empty or has no valid rows",
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate columns
        required_columns = ['', 'Prompt', '', 'URL']
        # Also support English column names
        required_columns_en = ['model_name', 'prompt', 'work_type', 'url']
        
        first_row = rows[0]
        has_chinese = any(col in first_row for col in required_columns)
        has_english = any(col in first_row for col in required_columns_en)
        
        if not (has_chinese or has_english):
            return error_response(
                message=f"File must contain columns: {', '.join(required_columns)} or {', '.join(required_columns_en)}",
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        # Map column names
        col_map = {}
        if has_chinese:
            col_map = {
                'model_name': '',
                'prompt': 'Prompt',
                'work_type': '',
                'url': 'URL'
            }
        else:
            col_map = {
                'model_name': 'model_name',
                'prompt': 'prompt',
                'work_type': 'work_type',
                'url': 'url'
            }
        
        # Process each row
        storage = get_storage_service()
        success_count = 0
        failed_count = 0
        errors = []
        
        # Get user registration time for random created_at
        user_created_at = target_user.created_at
        if user_created_at.tzinfo is None:
            user_created_at = user_created_at.replace(tzinfo=timezone.utc)
        now = datetime.now(timezone.utc)
        time_diff = (now - user_created_at).total_seconds()
        
        for idx, row in enumerate(rows, start=2):  # Start from 2 (row 1 is header)
            try:
                # Get values (case-insensitive)
                model_name = None
                prompt = None
                work_type = None
                url = None
                
                for key, value in row.items():
                    key_lower = key.lower().strip()
                    if key_lower in [col_map['model_name'].lower(), 'model_name', '']:
                        model_name = str(value).strip() if value else None
                    elif key_lower in [col_map['prompt'].lower(), 'prompt']:
                        prompt = str(value).strip() if value else None
                    elif key_lower in [col_map['work_type'].lower(), 'work_type', '']:
                        work_type = str(value).strip().lower() if value else None
                    elif key_lower in [col_map['url'].lower(), 'url', 'url', 'url']:
                        url = str(value).strip() if value else None
                
                # Validate required fields
                if not all([model_name, prompt, work_type, url]):
                    errors.append(f"Row {idx}: Missing required fields")
                    failed_count += 1
                    continue
                
                # Validate work_type
                valid_types = ["text2img", "text-to-image", "img2img", "image-to-image", "text2video", "text-to-video", "img2video", "image-to-video", "", "", "", ""]
                type_map = {
                    "text2img": WorkType.TEXT2IMG,
                    "text-to-image": WorkType.TEXT2IMG,
                    "img2img": WorkType.IMG2IMG,
                    "image-to-image": WorkType.IMG2IMG,
                    "text2video": WorkType.TEXT2VIDEO,
                    "text-to-video": WorkType.TEXT2VIDEO,
                    "img2video": WorkType.IMG2VIDEO,
                    "image-to-video": WorkType.IMG2VIDEO,
                    "": WorkType.TEXT2IMG,
                    "": WorkType.IMG2IMG,
                    "": WorkType.TEXT2VIDEO,
                    "": WorkType.IMG2VIDEO
                }
                
                if work_type not in type_map:
                    errors.append(f"Row {idx}: Invalid work_type '{work_type}'")
                    failed_count += 1
                    continue
                
                work_type_enum = type_map[work_type]
                is_video = work_type_enum in [WorkType.TEXT2VIDEO, WorkType.IMG2VIDEO]
                
                # Download file
                async with httpx.AsyncClient() as client:
                    try:
                        headers = {
                            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                            "Accept": "image/*,video/*,*/*",
                        }
                        resp = await client.get(url, headers=headers, follow_redirects=True, timeout=60.0)
                        resp.raise_for_status()
                        file_data = resp.content
                        
                        if len(file_data) < 2000:
                            errors.append(f"Row {idx}: File too small")
                            failed_count += 1
                            continue
                    except Exception as e:
                        errors.append(f"Row {idx}: Failed to download file: {str(e)}")
                        failed_count += 1
                        continue
                
                # Upload to storage
                file_ext = "mp4" if is_video else "jpg"
                file_key = storage.generate_key(filename=f"batch_import_{idx}.{file_ext}")
                storage_key = file_key.split('.')[0]
                
                new_url = storage.upload_file(
                    file_obj=BytesIO(file_data),
                    key=file_key,
                    content_type="video/mp4" if is_video else "image/jpeg"
                )
                
                # Generate SEO fields
                alphabet = string.ascii_letters + string.digits
                short_code = ''.join(secrets.choice(alphabet) for _ in range(11))
                
                # Handle thumbnail
                thumbnail_url = None
                if "aliyuncs.com" in new_url:
                    sep = "&" if "?" in new_url else "?"
                    if is_video:
                        thumbnail_url = f"{new_url}{sep}x-oss-process=video/snapshot,t_0,f_jpg,w_480"
                    else:
                        thumbnail_url = f"{new_url}{sep}x-oss-process=image/resize,w_480"
                
                # Generate title and description using utility functions
                prompt_clean = prompt.strip()  # Clean prompt for storage
                title, description = generate_work_metadata(prompt_clean, model_name)
                share_name = title
                
                canonical_url = storage.generate_canonical_url(storage_key, title, file_ext)
                url_slug = generate_url_slug(short_code, title)
                
                # Generate random created_at
                if time_diff > 0:
                    random_seconds = random.uniform(0, time_diff)
                    work_created_at = user_created_at + timedelta(seconds=random_seconds)
                else:
                    work_created_at = now
                
                # Create Work record
                work = Work(
                    user_id=user_id,
                    type=work_type_enum,
                    prompt=prompt_clean,
                    model_name=model_name,
                    model_key="batch_import",
                    file_url=new_url,
                    thumbnail_url=thumbnail_url,
                    storage_key=storage_key,
                    canonical_url=canonical_url,
                    short_code=short_code,
                    url_slug=url_slug,
                    status=WorkStatus.SUCCESS,
                    is_shared=True,
                    share_status=ShareStatus.APPROVED,
                    share_name=title,
                    title=title,
                    description=description,
                    category=category,  # Use provided category or None
                    view_count=0,
                    like_count=0,
                    favorite_count=0,
                    tags=[],
                    created_at=work_created_at,
                    completed_at=work_created_at,
                    source="PGC"
                )
                
                db.add(work)
                success_count += 1
                
            except Exception as e:
                errors.append(f"Row {idx}: {str(e)}")
                failed_count += 1
                logger.error(f"Error processing row {idx}: {str(e)}")
                continue
        
        # Commit all successful works
        db.commit()
        
        logger.info(f"Admin {current_admin.id} batch imported works for user {user_id}: success={success_count}, failed={failed_count}")
        
        return success_response(
            data={
                "success_count": success_count,
                "failed_count": failed_count,
                "errors": errors[:10]  # Return first 10 errors
            },
            message=f"Batch import completed: {success_count} successful, {failed_count} failed"
        )
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error in batch_import_works: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return error_response(
            message=f"Failed to batch import works: {str(e)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
