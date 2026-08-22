from fastapi import APIRouter, HTTPException, status, Body
from pydantic import BaseModel, HttpUrl
from app.services.parser.parser_factory import ParserFactory
from app.utils.logger import logger
import os
import secrets

router = APIRouter()

_env_mode = os.getenv("ENVIRONMENT", "development").strip().lower()
SECURITY_TOKEN = os.getenv("OVERSEAS_PARSER_TOKEN", "").strip()

if _env_mode == "production":
    if not SECURITY_TOKEN:
        raise RuntimeError(
            "CRITICAL SECURITY ERROR: Missing OVERSEAS_PARSER_TOKEN in PRODUCTION mode! "
            "Please set a strong random OVERSEAS_PARSER_TOKEN environment variable."
        )
else:
    if not SECURITY_TOKEN:
        logger.warning("OVERSEAS_PARSER_TOKEN not configured. Using temporary fallback token for development.")
        SECURITY_TOKEN = "vidgen_dev_overseas_parser_token_change_me"

class ParseRequest(BaseModel):
    url: str
    token: str

class ParseResponse(BaseModel):
    success: bool
    platform: str | None = None
    title: str | None = None
    video_url: str | None = None
    cover_url: str | None = None
    author: dict | None = None
    images: list | None = []
    audio_url: str | None = None
    error: str | None = None

@router.post("/parse", response_model=ParseResponse, summary="Parse overseas video/image metadata")
async def parse_overseas_url(req: ParseRequest = Body(...)):
    """
    Parse TikTok, YouTube, Instagram, and Twitter URLs.
    Secured by a matching token between the domestic and overseas server.
    """
    # 1. Validate security token using constant-time comparison
    if not secrets.compare_digest(req.token, SECURITY_TOKEN):
        logger.warning("Unauthorized overseas parse attempt with invalid security token.")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized parser token"
        )

    # 2. Perform parsing
    try:
        logger.info(f"Processing overseas parse request for URL: {req.url}")
        parsed_data = ParserFactory.parse_url(req.url)
        return ParseResponse(
            success=True,
            platform=parsed_data.get("platform"),
            title=parsed_data.get("title"),
            video_url=parsed_data.get("video_url"),
            cover_url=parsed_data.get("cover_url"),
            author=parsed_data.get("author"),
            images=parsed_data.get("images") or [],
            audio_url=parsed_data.get("audio_url")
        )
    except ValueError as ve:
        logger.warning(f"Unsupported platform error for URL {req.url}: {ve}")
        return ParseResponse(success=False, error=str(ve))
    except Exception as e:
        logger.error(f"Failed to parse URL {req.url} dynamically: {e}", exc_info=True)
        return ParseResponse(success=False, error=f"Parsing error: {str(e)}")
