from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, Request, status
from sqlalchemy.orm import Session
import os
from dotenv import load_dotenv

from ..models.base import get_db
from ..models.user import User
from ..models.admin import Admin
from ..models.media import Media, MediaType
from ..utils.auth import get_current_user_or_admin
from ..utils.responses import success_response, error_response
from ..utils.logger import logger
from ..services.storage import get_storage_service
from ..services.thumbnail import generate_image_thumbnail_webp, generate_video_thumbnail_webp
from ..utils.rate_limit import enforce_rate_limit, env_limit

load_dotenv()

router = APIRouter()

# Configuration
MAX_UPLOAD_SIZE_MB = int(os.getenv("MAX_UPLOAD_SIZE_MB", "100"))
MAX_UPLOAD_SIZE_BYTES = MAX_UPLOAD_SIZE_MB * 1024 * 1024
ALLOWED_IMAGE_TYPES = os.getenv("ALLOWED_IMAGE_TYPES", "jpg,jpeg,png,webp,gif").split(",")
ALLOWED_VIDEO_TYPES = os.getenv("ALLOWED_VIDEO_TYPES", "mp4,webm,mov,avi").split(",")
UPLOAD_RATE_LIMIT = env_limit("UPLOAD_RATE_LIMIT", 20)
UPLOAD_RATE_WINDOW = env_limit("UPLOAD_RATE_WINDOW_SECONDS", 60)


def validate_upload_file(file: UploadFile, source: str = "user_upload") -> tuple[bool, str]:
    """
    Validate uploaded file.
    
    Args:
        file: Uploaded file
        source: Source of the upload (admin, user_upload, etc.)
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    # Check file extension
    if not file.filename:
        return False, "Filename is required"
    
    ext = file.filename.split(".")[-1].lower()
    
    allowed_exts = ALLOWED_IMAGE_TYPES.copy()
    # For admin or general uploads, also allow video
    if source in ["admin", "user_upload", "user_work"]:
        allowed_exts.extend(ALLOWED_VIDEO_TYPES)
        
    if ext not in allowed_exts:
        return False, f"File type not allowed. Allowed types: {', '.join(allowed_exts)}"
    
    # Check content type
    if file.content_type:
        is_image = file.content_type.startswith("image/")
        is_video = file.content_type.startswith("video/")
        
        if not (is_image or is_video):
            return False, "Invalid content type. Must be an image or video."
    
    return True, ""


@router.post("")
async def upload_file(
    request: Request,
    file: UploadFile = File(...),
    source: str = Form("user_upload"),
    current_auth = Depends(get_current_user_or_admin),
    db: Session = Depends(get_db)
):
    """
    Upload a file (image or video) to R2 storage.
    Returns both permanent URL and presigned URL.
    """
    identity_type = "admin" if isinstance(current_auth, Admin) else "user"
    enforce_rate_limit(
        request,
        "upload:account",
        UPLOAD_RATE_LIMIT,
        UPLOAD_RATE_WINDOW,
        identity=f"{identity_type}:{current_auth.id}",
    )
    try:
        # Determine user_id for the media record
        if isinstance(current_auth, User):
            uploader_id = current_auth.id
        else:
            # Admin uploading - associate with the first admin user in 'users' table
            # or any user if no admin user exists
            system_user = db.query(User).filter(User.is_admin == True).first()
            if not system_user:
                system_user = db.query(User).first()
            
            if not system_user:
                return error_response(
                    message="No user found in database to associate with admin upload",
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            uploader_id = system_user.id

        # Validate source
        allowed_sources = ["admin", "user_upload", "user_avatar", "user_work"]
        if source not in allowed_sources:
            source = "user_upload"
            
        # Validate file
        is_valid, error_msg = validate_upload_file(file, source)
        if not is_valid:
            return error_response(
                message=error_msg,
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        # Read file content
        content = await file.read()
        
        # Check file size
        if len(content) > MAX_UPLOAD_SIZE_BYTES:
            return error_response(
                message=f"File too large. Maximum size: {MAX_UPLOAD_SIZE_MB}MB",
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        # Get storage service
        storage = get_storage_service()
        
        # Generate unique key
        # Use a more appropriate default extension if filename is missing
        default_ext = "jpg"
        if file.content_type and "video" in file.content_type:
            default_ext = "mp4"
            
        key = storage.generate_key(
            filename=file.filename or f"upload.{default_ext}"
        )
        
        # Upload to R2
        from io import BytesIO
        file_obj = BytesIO(content)
        
        url = storage.upload_file(
            file_obj=file_obj,
            key=key,
            content_type=file.content_type,
            public=False  # Private by default
        )
        
        # Generate presigned URL for temporary access
        presigned_url = storage.generate_presigned_url(key, expiration=3600)
        
        # Determine media type from mime type
        media_type = MediaType.IMAGE
        if file.content_type:
            if file.content_type.startswith("video/"):
                media_type = MediaType.VIDEO
            elif file.content_type.startswith("audio/"):
                media_type = MediaType.AUDIO
            elif file.content_type.startswith("image/"):
                media_type = MediaType.IMAGE
            else:
                media_type = MediaType.DOCUMENT
        
        # Generate thumbnail URL for images/videos ( WebP )
        thumbnail_url = None
        try:
            if media_type == MediaType.IMAGE:
                #  WebP
                thumbnail_data = await generate_image_thumbnail_webp(
                    image_url=url,
                    max_width=800,
                    max_height=800,
                    quality=85
                )
                
                #  R2
                storage_key_base = key.rsplit('.', 1)[0] if '.' in key else key
                thumbnail_key = f"{storage_key_base}_thumb.webp"
                thumbnail_obj = BytesIO(thumbnail_data)
                thumbnail_url = storage.upload_file(
                    file_obj=thumbnail_obj,
                    key=thumbnail_key,
                    content_type="image/webp",
                    public=False
                )
                logger.info(f"Upload image WebP thumbnail: {thumbnail_url}")
            elif media_type == MediaType.VIDEO:
                #  WebP
                thumbnail_data = await generate_video_thumbnail_webp(
                    video_url=url,
                    time_position=1.0,
                    max_width=800,
                    max_height=800,
                    quality=85
                )
                
                if thumbnail_data:
                    #  R2
                    storage_key_base = key.rsplit('.', 1)[0] if '.' in key else key
                    thumbnail_key = f"{storage_key_base}_thumb.webp"
                    thumbnail_obj = BytesIO(thumbnail_data)
                    thumbnail_url = storage.upload_file(
                        file_obj=thumbnail_obj,
                        key=thumbnail_key,
                        content_type="image/webp",
                        public=False
                    )
                    logger.info(f"Upload video WebP thumbnail: {thumbnail_url}")
        except Exception as e:
            logger.warning(f"Failed to generate thumbnail for upload: {str(e)}")
            thumbnail_url = None
        
        # Save media record to database
        media_record = Media(
            user_id=uploader_id,
            filename=key.split("/")[-1],  # Just the filename part
            original_filename=file.filename or f"upload.{default_ext}",
            file_url=url,
            thumbnail_url=thumbnail_url,
            file_size=len(content),
            mime_type=file.content_type or ("video/mp4" if media_type == MediaType.VIDEO else "image/jpeg"),
            media_type=media_type,
            storage_key=key,
            storage_type="oss" if not storage.is_local else "local",
            source=source
        )
        db.add(media_record)
        db.commit()
        db.refresh(media_record)
        
        logger.info(f"File uploaded by {type(current_auth).__name__} {getattr(current_auth, 'id', 'unknown')}: {key} (Media ID: {media_record.id})")
        
        return success_response(
            data={
                "id": media_record.id,
                "url": url,
                "presigned_url": presigned_url,
                "key": key,
                "filename": file.filename,
                "size": len(content),
                "content_type": file.content_type,
                "media_type": media_type.value,
                "thumbnail_url": thumbnail_url,
            },
            message="File uploaded successfully"
        )
        
    except Exception as e:
        import traceback
        error_detail = traceback.format_exc()
        logger.error(f"Error uploading file: {str(e)}\n{error_detail}")
        db.rollback()
        return error_response(
            message=f"Failed to upload file: {str(e)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
