from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from ..models.base import get_db
from ..models.admin import Admin
from ..models.seo_config import SeoConfig, PageSeo
from ..models.schemas import SeoConfigRequest, UpdateSeoConfigRequest, CreatePageSeoRequest, UpdatePageSeoRequest
from ..utils.auth import get_current_admin
from ..utils.responses import success_response, error_response
from ..utils.logger import logger

router = APIRouter()


@router.get("/seo/configs")
def get_all_seo_configs(
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Get all SEO configurations.
    """
    try:
        configs = db.query(SeoConfig).order_by(SeoConfig.config_key).all()
        return success_response(
            data=[config.to_dict() for config in configs],
            message="SEO configurations retrieved successfully"
        )
    except Exception as e:
        logger.error(f"Error fetching SEO configs: {e}")
        return error_response(
            message="Failed to fetch SEO configurations",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.get("/seo/configs/{config_key}")
def get_seo_config(
    config_key: str,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Get a specific SEO configuration by key.
    """
    try:
        config = db.query(SeoConfig).filter(
            SeoConfig.config_key == config_key
        ).first()
        
        if not config:
            return error_response(
                message="Configuration not found",
                status_code=status.HTTP_404_NOT_FOUND
            )
        
        return success_response(
            data=config.to_dict(),
            message="Configuration retrieved successfully"
        )
    except Exception as e:
        logger.error(f"Error fetching SEO config: {e}")
        return error_response(
            message="Failed to fetch configuration",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.post("/seo/configs")
def create_seo_config(
    request: SeoConfigRequest,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Create a new SEO configuration.
    """
    try:
        # Check if config already exists
        existing = db.query(SeoConfig).filter(
            SeoConfig.config_key == request.config_key
        ).first()
        
        if existing:
            return error_response(
                message="Configuration with this key already exists",
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        # Create new config
        new_config = SeoConfig(
            config_key=request.config_key,
            config_value=request.config_value,
            is_enabled=request.is_enabled,
            description=request.description
        )
        
        db.add(new_config)
        db.commit()
        db.refresh(new_config)
        
        logger.info(f"Admin {current_admin.username} created SEO config: {request.config_key}")
        
        return success_response(
            data=new_config.to_dict(),
            message="Configuration created successfully",
            status_code=status.HTTP_201_CREATED
        )
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating SEO config: {e}")
        return error_response(
            message="Failed to create configuration",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.put("/seo/configs/{config_key}")
def update_seo_config(
    config_key: str,
    request: UpdateSeoConfigRequest,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Update an existing SEO configuration.
    """
    try:
        config = db.query(SeoConfig).filter(
            SeoConfig.config_key == config_key
        ).first()
        
        if not config:
            return error_response(
                message="Configuration not found",
                status_code=status.HTTP_404_NOT_FOUND
            )
        
        # Update fields
        if request.config_value is not None:
            config.config_value = request.config_value
        if request.is_enabled is not None:
            config.is_enabled = request.is_enabled
        if request.description is not None:
            config.description = request.description
        
        db.commit()
        db.refresh(config)
        
        logger.info(f"Admin {current_admin.username} updated SEO config: {config_key}")
        
        return success_response(
            data=config.to_dict(),
            message="Configuration updated successfully"
        )
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating SEO config: {e}")
        return error_response(
            message="Failed to update configuration",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.delete("/seo/configs/{config_key}")
def delete_seo_config(
    config_key: str,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Delete an SEO configuration.
    """
    try:
        config = db.query(SeoConfig).filter(
            SeoConfig.config_key == config_key
        ).first()
        
        if not config:
            return error_response(
                message="Configuration not found",
                status_code=status.HTTP_404_NOT_FOUND
            )
        
        db.delete(config)
        db.commit()
        
        logger.info(f"Admin {current_admin.username} deleted SEO config: {config_key}")
        
        return success_response(
            message="Configuration deleted successfully"
        )
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting SEO config: {e}")
        return error_response(
            message="Failed to delete configuration",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.post("/seo/configs/init-defaults")
def init_default_configs(
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Initialize default SEO configurations.
    """
    try:
        default_configs = [
            # Basic Settings
            {
                "config_key": "base_url",
                "config_value": "https://yoursite.com",
                "description": "（ robots.txt ）"
            },
            # {
            #     "config_key": "site_name",
            #     "config_value": "AIGC Platform",
            #     "description": " (Title)"
            # },
            # {
            #     "config_key": "site_description",
            #     "config_value": "Professional AIGC content generation platform",
            #     "description": "Description (Description)"
            # },
            # {
            #     "config_key": "site_keywords",
            #     "config_value": "AIGC, AI, Content Generation",
            #     "description": "Keywords (Keywords)"
            # },
            # Sitemap Settings
            {
                "config_key": "sitemap_include_works",
                "config_value": "true",
                "description": "/Prompts"
            },
            {
                "config_key": "sitemap_include_blogs",
                "config_value": "true",
                "description": ""
            },
            {
                "config_key": "sitemap_include_topics",
                "config_value": "true",
                "description": ""
            },
            {
                "config_key": "sitemap_include_users",
                "config_value": "true",
                "description": ""
            },
            {
                "config_key": "sitemap_include_categories",
                "config_value": "true",
                "description": "Category (/category/...)"
            },
            {
                "config_key": "sitemap_include_effects",
                "config_value": "true",
                "description": "Category (/effects/...)"
            },
            {
                "config_key": "sitemap_include_generate",
                "config_value": "true",
                "description": "Category (/generate/...)"
            },
            # Robots.txt
            {
                "config_key": "robots_txt_custom",
                "config_value": None,
                "description": " robots.txt （）"
            }
        ]
        
        created_count = 0
        for config_data in default_configs:
            existing = db.query(SeoConfig).filter(
                SeoConfig.config_key == config_data["config_key"]
            ).first()
            
            if not existing:
                new_config = SeoConfig(
                    config_key=config_data["config_key"],
                    config_value=config_data["config_value"],
                    is_enabled=True,
                    description=config_data["description"]
                )
                db.add(new_config)
                created_count += 1
        
        db.commit()
        
        logger.info(f"Admin {current_admin.username} initialized {created_count} default SEO configs")
        
        return success_response(
            message=f"Initialized {created_count} default configurations"
        )
    except Exception as e:
        db.rollback()
        logger.error(f"Error initializing default configs: {e}")
        return error_response(
            message="Failed to initialize default configurations",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# --- Page SEO Routes ---

@router.get("/seo/pages")
def get_all_page_seos(
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Get all page SEO configurations (TDK).
    """
    try:
        pages = db.query(PageSeo).order_by(PageSeo.page_name).all()
        return success_response(
            data=[page.to_dict() for page in pages],
            message="Page SEO configurations retrieved successfully"
        )
    except Exception as e:
        logger.error(f"Error fetching page SEOs: {e}")
        return error_response(
            message="Failed to fetch page SEO configurations",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.get("/seo/pages/{page_name}")
def get_page_seo(
    page_name: str,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Get SEO configuration for a specific page.
    """
    try:
        page = db.query(PageSeo).filter(PageSeo.page_name == page_name).first()
        if not page:
            return error_response(
                message="Page SEO configuration not found",
                status_code=status.HTTP_404_NOT_FOUND
            )
        return success_response(
            data=page.to_dict(),
            message="Page SEO configuration retrieved successfully"
        )
    except Exception as e:
        logger.error(f"Error fetching page SEO for {page_name}: {e}")
        return error_response(
            message="Failed to fetch page SEO configuration",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.put("/seo/pages/{page_name}")
def update_page_seo(
    page_name: str,
    request: UpdatePageSeoRequest,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Update SEO configuration for a specific page.
    """
    try:
        page = db.query(PageSeo).filter(PageSeo.page_name == page_name).first()
        if not page:
            # If it doesn't exist, we create it (auto-vivification for ease of use)
            # Default path to /page_name if not provided
            path = request.page_path or f"/{page_name}"
            page = PageSeo(page_name=page_name, page_path=path)
            db.add(page)
        
        # page_path ， page_path
        if request.title is not None:
            page.title = request.title
        if request.description is not None:
            page.description = request.description
        if request.keywords is not None:
            page.keywords = request.keywords
        if request.is_enabled is not None:
            page.is_enabled = request.is_enabled
            
        db.commit()
        db.refresh(page)
        
        logger.info(f"Admin {current_admin.username} updated Page SEO for {page_name}")
        
        return success_response(
            data=page.to_dict(),
            message="Page SEO configuration updated successfully"
        )
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating page SEO for {page_name}: {e}")
        return error_response(
            message="Failed to update page SEO configuration",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.post("/seo/pages/init-defaults")
def init_default_page_seos(
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Initialize default Page SEO configurations.
    Creates missing pages and fills empty fields for existing pages.
    """
    try:
        default_pages = [
            {"page_name": "home", "page_path": "/", "title": "Home | AIGC Platform", "description": "Welcome to AIGC Platform", "keywords": "AIGC, Home"},
            {"page_name": "explore", "page_path": "/explore", "title": "Explore | AIGC Platform", "description": "Explore AI generated works", "keywords": "AIGC, Explore"},
            {"page_name": "create", "page_path": "/generate", "title": "Create | AIGC Platform", "description": "Create your own AI works", "keywords": "AIGC, Create"},
            {"page_name": "blog", "page_path": "/blog", "title": "Blog | AIGC Platform", "description": "Read our latest articles", "keywords": "AIGC, Blog"},
            {"page_name": "topics", "page_path": "/topic", "title": "Topics | AIGC Platform", "description": "Browse works by topic", "keywords": "AIGC, Topics"},
            {"page_name": "templates", "page_path": "/magic", "title": "Magic | AIGC Platform", "description": "Explore AI generation models and effects", "keywords": "AIGC, Magic, Effects"},
            {"page_name": "effects", "page_path": "/effects", "title": "Effects | AIGC Platform", "description": "Explore AI generation effects", "keywords": "AIGC, Effects"},
            {"page_name": "category", "page_path": "/category", "title": "Category | AIGC Platform", "description": "Browse works by category", "keywords": "AIGC, Category"}
        ]
        
        created_count = 0
        updated_count = 0
        for page_data in default_pages:
            existing = db.query(PageSeo).filter(
                PageSeo.page_name == page_data["page_name"]
            ).first()
            
            if not existing:
                # Create new page if it doesn't exist
                new_page = PageSeo(
                    page_name=page_data["page_name"],
                    page_path=page_data["page_path"],
                    title=page_data["title"],
                    description=page_data["description"],
                    keywords=page_data["keywords"],
                    is_enabled=True
                )
                db.add(new_page)
                created_count += 1
            else:
                # Update empty fields for existing pages
                updated = False
                if not existing.page_path or existing.page_path.strip() == "":
                    existing.page_path = page_data["page_path"]
                    updated = True
                if not existing.title or existing.title.strip() == "":
                    existing.title = page_data["title"]
                    updated = True
                if not existing.description or existing.description.strip() == "":
                    existing.description = page_data["description"]
                    updated = True
                if not existing.keywords or existing.keywords.strip() == "":
                    existing.keywords = page_data["keywords"]
                    updated = True
                if updated:
                    updated_count += 1
        
        db.commit()
        
        logger.info(f"Admin {current_admin.username} initialized {created_count} default page SEO configs and updated {updated_count} existing pages")
        
        if updated_count > 0:
            message = f"： {created_count} ， {updated_count} "
        else:
            message = f"： {created_count} "
        
        return success_response(
            message=message
        )
    except Exception as e:
        db.rollback()
        logger.error(f"Error initializing default page configs: {e}")
        return error_response(
            message="Failed to initialize default page configurations",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
