from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime
from ..models.base import get_db
from ..models.seo_config import SeoConfig
from ..models.work import Work, ShareStatus
from ..models.blog import BlogPost, PostStatus
from ..models.topic import Topic
from ..models.user import User
from ..models.generate_page import GeneratePage
from ..utils.responses import success_response, error_response
from ..utils.logger import logger
from fastapi import status

router = APIRouter()


def get_seo_config(db: Session, key: str) -> Optional[str]:
    """Get SEO configuration value by key."""
    config = db.query(SeoConfig).filter(
        SeoConfig.config_key == key,
        SeoConfig.is_enabled == True
    ).first()
    return config.config_value if config else None


def get_base_url(db: Session) -> str:
    """Get base URL from config and ensure no trailing slash."""
    url = get_seo_config(db, "base_url") or "https://yoursite.com"
    return url.rstrip('/')


@router.get("/robots.txt")
def get_robots_txt(db: Session = Depends(get_db)):
    """
    Generate dynamic robots.txt based on configuration.
    Always use database field value if exists and not empty, otherwise use default.
    """
    try:
        # Get robots.txt content from database
        config = db.query(SeoConfig).filter(
            SeoConfig.config_key == "robots_txt_custom"
        ).first()
        
        # Use database value if exists and not empty, otherwise use default
        if config and config.config_value and config.config_value.strip() and config.is_enabled:
            content = config.config_value.strip()
        else:
            # Default robots.txt logic
            base_url = get_base_url(db)
            
            # Start with common rules
            lines = [
                "User-agent: *",
                "Allow: /",
                "Disallow: /api/",
                "Disallow: /admin/",
                "Disallow: /auth/",
                "Disallow: /payment/"
            ]
            
            # Dynamic prompt rules based on sitemap settings
            works_config = db.query(SeoConfig).filter(SeoConfig.config_key == "sitemap_include_works").first()
            works_mode = works_config.config_value if works_config and works_config.is_enabled else "true"
            
            if works_mode == "featured":
                # Explicitly allow featured works
                featured_works = db.query(Work.url_slug, Work.short_code, Work.id).filter(
                    Work.is_featured == True,
                    Work.share_status == ShareStatus.APPROVED,
                    Work.is_banned == False,
                    Work.deleted_at == None
                ).limit(1000).all()
                
                for slug, code, wid in featured_works:
                    path = slug or code or str(wid)
                    lines.append(f"Allow: /prompt/{path}")
                
                # Disallow all other prompt pages
                lines.append("Disallow: /prompt/")
            elif works_mode == "false":
                # Disallow all prompt pages
                lines.append("Disallow: /prompt/")
            
            lines.append(f"\nSitemap: {base_url}/sitemap.xml")
            content = "\n".join(lines)
        
        return Response(content=content, media_type="text/plain")
    
    except Exception as e:
        logger.error(f"Error generating robots.txt: {e}", exc_info=True)
        # Fallback to basic robots.txt
        return Response(
            content="User-agent: *\nAllow: /\nDisallow: /admin/",
            media_type="text/plain"
        )


@router.get("/sitemap.xml")
def get_sitemap_xml(db: Session = Depends(get_db)):
    """
    Generate dynamic sitemap.xml based on database content.
    """
    try:
        base_url = get_base_url(db)
        
        # Helper to check if a feature is enabled and its value
        def get_sitemap_mode(key: str, default: str = "true") -> str:
            config = db.query(SeoConfig).filter(SeoConfig.config_key == key).first()
            if not config:
                return default
            if not config.is_enabled:
                return "false"  # If disabled, do not include in sitemap
            return config.config_value or default

        # Get sitemap settings
        include_works_mode = get_sitemap_mode("sitemap_include_works", "true")
        include_blogs = get_sitemap_mode("sitemap_include_blogs", "true") == "true"
        include_topics = get_sitemap_mode("sitemap_include_topics", "true") == "true"
        include_users = get_sitemap_mode("sitemap_include_users", "true") == "true"
        include_categories = get_sitemap_mode("sitemap_include_categories", "true") == "true"
        include_effects = get_sitemap_mode("sitemap_include_effects", "true") == "true"
        include_generate = get_sitemap_mode("sitemap_include_generate", "true") == "true"
        
        # Start XML
        xml_content = ['<?xml version="1.0" encoding="UTF-8"?>']
        xml_content.append('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">')
        
        # Homepage
        xml_content.append('  <url>')
        xml_content.append(f'    <loc>{base_url}/</loc>')
        xml_content.append(f'    <lastmod>{datetime.now().strftime("%Y-%m-%d")}</lastmod>')
        xml_content.append('    <changefreq>daily</changefreq>')
        xml_content.append('    <priority>1.0</priority>')
        xml_content.append('  </url>')
        
        # Static pages
        static_pages = [
            {'path': '/explore', 'priority': '0.9', 'changefreq': 'daily'},
            {'path': '/magic', 'priority': '0.9', 'changefreq': 'daily'},
            {'path': '/generate', 'priority': '0.8', 'changefreq': 'weekly'},
            {'path': '/blog', 'priority': '0.8', 'changefreq': 'daily'},
            {'path': '/topic', 'priority': '0.7', 'changefreq': 'weekly'},
            {'path': '/effects', 'priority': '0.7', 'changefreq': 'weekly'},
            {'path': '/category', 'priority': '0.7', 'changefreq': 'weekly'},
            {'path': '/help-center', 'priority': '0.5', 'changefreq': 'monthly'},
            {'path': '/terms', 'priority': '0.3', 'changefreq': 'monthly'},
            {'path': '/privacy', 'priority': '0.3', 'changefreq': 'monthly'},
        ]
        
        for page in static_pages:
            xml_content.append('  <url>')
            xml_content.append(f'    <loc>{base_url}{page["path"]}</loc>')
            xml_content.append(f'    <changefreq>{page["changefreq"]}</changefreq>')
            xml_content.append(f'    <priority>{page["priority"]}</priority>')
            xml_content.append('  </url>')
        
        # Category Pages
        if include_categories:
            from ..models.category_page import CategoryPage
            cat_pages = db.query(CategoryPage).filter(
                CategoryPage.is_active == True
            ).all()
            
            for page in cat_pages:
                if page.page_path:
                    path = page.page_path if page.page_path.startswith('/') else f"/{page.page_path}"
                    xml_content.append('  <url>')
                    xml_content.append(f'    <loc>{base_url}{path}</loc>')
                    if page.updated_at:
                        xml_content.append(f'    <lastmod>{page.updated_at.strftime("%Y-%m-%d")}</lastmod>')
                    xml_content.append('    <changefreq>weekly</changefreq>')
                    xml_content.append('    <priority>0.7</priority>')
                    xml_content.append('  </url>')

        # Effects Pages
        if include_effects:
            from ..models.effects_page import EffectsPage
            eff_pages = db.query(EffectsPage).filter(
                EffectsPage.is_active == True
            ).all()
            
            for page in eff_pages:
                if page.page_path:
                    path = page.page_path if page.page_path.startswith('/') else f"/{page.page_path}"
                    xml_content.append('  <url>')
                    xml_content.append(f'    <loc>{base_url}{path}</loc>')
                    if page.updated_at:
                        xml_content.append(f'    <lastmod>{page.updated_at.strftime("%Y-%m-%d")}</lastmod>')
                    xml_content.append('    <changefreq>weekly</changefreq>')
                    xml_content.append('    <priority>0.7</priority>')
                    xml_content.append('  </url>')

        # Generate Pages
        if include_generate:
            gen_pages = db.query(GeneratePage).filter(
                GeneratePage.is_active == True
            ).all()
            
            for page in gen_pages:
                if page.page_path:
                    path = page.page_path if page.page_path.startswith('/') else f"/{page.page_path}"
                    xml_content.append('  <url>')
                    xml_content.append(f'    <loc>{base_url}{path}</loc>')
                    if page.updated_at:
                        xml_content.append(f'    <lastmod>{page.updated_at.strftime("%Y-%m-%d")}</lastmod>')
                    xml_content.append('    <changefreq>weekly</changefreq>')
                    xml_content.append('    <priority>0.8</priority>')
                    xml_content.append('  </url>')
        
        # Blog posts
        if include_blogs:
            blog_posts = db.query(BlogPost).filter(
                BlogPost.status == PostStatus.PUBLISHED
            ).order_by(BlogPost.published_at.desc()).limit(1000).all()
            
            for post in blog_posts:
                xml_content.append('  <url>')
                xml_content.append(f'    <loc>{base_url}/blog/{post.slug}</loc>')
                if post.updated_at:
                    xml_content.append(f'    <lastmod>{post.updated_at.strftime("%Y-%m-%d")}</lastmod>')
                xml_content.append('    <changefreq>weekly</changefreq>')
                xml_content.append('    <priority>0.7</priority>')
                xml_content.append('  </url>')
        
        # Topics
        if include_topics:
            from ..models.topic import TopicStatus
            topics = db.query(Topic).filter(
                Topic.status == TopicStatus.PUBLISHED
            ).order_by(Topic.created_at.desc()).limit(500).all()
            
            for topic in topics:
                xml_content.append('  <url>')
                xml_content.append(f'    <loc>{base_url}/topic/{topic.slug}</loc>')
                if topic.updated_at:
                    xml_content.append(f'    <lastmod>{topic.updated_at.strftime("%Y-%m-%d")}</lastmod>')
                xml_content.append('    <changefreq>weekly</changefreq>')
                xml_content.append('    <priority>0.6</priority>')
                xml_content.append('  </url>')
        
        # Works (Prompts)
        if include_works_mode != "false":
            query = db.query(Work).filter(
                Work.share_status == ShareStatus.APPROVED,
                Work.is_banned == False,
                Work.deleted_at == None
            )
            
            # Apply "featured only" filter if selected
            if include_works_mode == "featured":
                query = query.filter(Work.is_featured == True)
            
            works = query.order_by(Work.created_at.desc()).limit(5000).all()
            
            for work in works:
                # Use url_slug if available, otherwise fallback to short_code or id
                work_path = work.url_slug or work.short_code or str(work.id)
                priority = "0.8" if work.is_featured else "0.5"
                changefreq = "daily" if work.is_featured else "monthly"
                
                xml_content.append('  <url>')
                xml_content.append(f'    <loc>{base_url}/prompt/{work_path}</loc>')
                if work.updated_at:
                    xml_content.append(f'    <lastmod>{work.updated_at.strftime("%Y-%m-%d")}</lastmod>')
                xml_content.append(f'    <changefreq>{changefreq}</changefreq>')
                xml_content.append(f'    <priority>{priority}</priority>')
                xml_content.append('  </url>')
        
        # User profiles
        if include_users:
            users = db.query(User).filter(
                User.is_active == True
            ).order_by(User.created_at.desc()).limit(1000).all()
            
            for user in users:
                if user.handle:
                    xml_content.append('  <url>')
                    xml_content.append(f'    <loc>{base_url}/user/{user.handle}</loc>')
                    xml_content.append('    <changefreq>weekly</changefreq>')
                    xml_content.append('    <priority>0.4</priority>')
                    xml_content.append('  </url>')
        
        # Close XML
        xml_content.append('</urlset>')
        
        return Response(
            content='\n'.join(xml_content),
            media_type="application/xml"
        )
    
    except Exception as e:
        logger.error(f"Error generating sitemap.xml: {e}")
        # Return minimal sitemap
        return Response(
            content='<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"></urlset>',
            media_type="application/xml"
        )


@router.get("/sitemap-index.xml")
def get_sitemap_index(db: Session = Depends(get_db)):
    """
    Generate sitemap index for large sites.
    """
    base_url = get_base_url(db)
    
    xml_content = ['<?xml version="1.0" encoding="UTF-8"?>']
    xml_content.append('<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">')
    xml_content.append('  <sitemap>')
    xml_content.append(f'    <loc>{base_url}/sitemap.xml</loc>')
    xml_content.append(f'    <lastmod>{datetime.now().strftime("%Y-%m-%d")}</lastmod>')
    xml_content.append('  </sitemap>')
    xml_content.append('</sitemapindex>')
    
    return Response(
        content='\n'.join(xml_content),
        media_type="application/xml"
    )


@router.get("/api/seo/meta-tags")
def get_meta_tags(db: Session = Depends(get_db)):
    """
    Get enabled meta tags for frontend injection.
    Returns all enabled meta configurations.
    """
    try:
        # Get all relevant SEO configurations
        configs = db.query(SeoConfig).filter(
            (SeoConfig.config_key.like('meta_%')) | 
            (SeoConfig.config_key.like('custom_code_%')) | 
            (SeoConfig.config_key.in_(['site_name', 'site_description', 'site_keywords'])),
            SeoConfig.is_enabled == True,
            SeoConfig.config_value.isnot(None)
        ).all()
        
        meta_data = {}
        for config in configs:
            if config.config_value and config.config_value.strip():
                meta_data[config.config_key] = config.config_value
        
        return success_response(
            data=meta_data,
            message="Meta tags retrieved successfully"
        )
    except Exception as e:
        logger.error(f"Error fetching meta tags: {e}")
        return success_response(data={}, message="No meta tags configured")


@router.get("/api/seo/page-configs")
def get_all_page_configs(db: Session = Depends(get_db)):
    """
    Get all page SEO configurations for frontend routing/head management.
    """
    try:
        from ..models.seo_config import PageSeo
        pages = db.query(PageSeo).filter(PageSeo.is_enabled == True).all()
        page_data = {p.page_name: p.to_dict() for p in pages}
        
        return success_response(
            data=page_data,
            message="Page SEO configurations retrieved successfully"
        )
    except Exception as e:
        logger.error(f"Error fetching page configs: {e}")
        return success_response(data={}, message="No page SEO configured")


@router.get("/api/seo/page-status/{page_name}")
def get_page_status(page_name: str, db: Session = Depends(get_db)):
    """
    Get page SEO status (including disabled pages) for 404 checking.
    Returns page configuration if exists, regardless of is_enabled status.
    """
    try:
        from ..models.seo_config import PageSeo
        page = db.query(PageSeo).filter(PageSeo.page_name == page_name).first()
        
        if not page:
            return success_response(
                data={"exists": False, "is_enabled": False},
                message="Page not found"
            )
        
        return success_response(
            data={
                "exists": True,
                "is_enabled": page.is_enabled,
                "page": page.to_dict()
            },
            message="Page status retrieved successfully"
        )
    except Exception as e:
        logger.error(f"Error fetching page status for {page_name}: {e}")
        return success_response(
            data={"exists": False, "is_enabled": False},
            message="Error checking page status"
        )


@router.get("/api/category-pages/tree")
def get_category_tree_public(
    db: Session = Depends(get_db)
):
    """
    Get category tree structure (public endpoint, no auth required).
    Returns only active categories with show_in_explore=True for use in explore page.
    """
    try:
        from ..models.category_page import CategoryPage
        
        # Get all active level 1 categories that should be shown in explore
        level1_categories = db.query(CategoryPage).filter(
            CategoryPage.level == 1,
            CategoryPage.is_active == True,
            CategoryPage.show_in_explore == True
        ).order_by(CategoryPage.sort_order, CategoryPage.category_name).all()
        
        tree_data = []
        for parent in level1_categories:
            parent_dict = parent.to_dict(include_children=False)
            
            # Get active children that should be shown in explore
            children = db.query(CategoryPage).filter(
                CategoryPage.parent_id == parent.id,
                CategoryPage.is_active == True,
                CategoryPage.show_in_explore == True
            ).order_by(CategoryPage.sort_order, CategoryPage.category_name).all()
            
            parent_dict["children"] = [child.to_dict(include_children=False) for child in children]
            tree_data.append(parent_dict)
        
        return success_response(
            data=tree_data,
            message="Category tree retrieved successfully"
        )
    except Exception as e:
        logger.error(f"Error fetching category tree: {e}")
        return error_response(
            message="Failed to fetch category tree",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.get("/api/category-pages/tree-active")
def get_category_tree_active(
    db: Session = Depends(get_db)
):
    """
    Get category tree structure for category search page (public endpoint, no auth required).
    Returns only active categories (is_active=True), regardless of show_in_explore setting.
    Used in /category page to show all active categories for searching.
    """
    try:
        from ..models.category_page import CategoryPage
        
        # Get all active level 1 categories (only filter by is_active, not show_in_explore)
        level1_categories = db.query(CategoryPage).filter(
            CategoryPage.level == 1,
            CategoryPage.is_active == True
        ).order_by(CategoryPage.sort_order, CategoryPage.category_name).all()
        
        tree_data = []
        for parent in level1_categories:
            parent_dict = parent.to_dict(include_children=False)
            
            # Get active children (only filter by is_active, not show_in_explore)
            children = db.query(CategoryPage).filter(
                CategoryPage.parent_id == parent.id,
                CategoryPage.is_active == True
            ).order_by(CategoryPage.sort_order, CategoryPage.category_name).all()
            
            parent_dict["children"] = [child.to_dict(include_children=False) for child in children]
            tree_data.append(parent_dict)
        
        return success_response(
            data=tree_data,
            message="Active category tree retrieved successfully"
        )
    except Exception as e:
        logger.error(f"Error fetching active category tree: {e}")
        return error_response(
            message="Failed to fetch active category tree",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.get("/api/effects-pages/tree")
def get_effects_tree_public(
    db: Session = Depends(get_db)
):
    """
    Get effects pages tree structure (public endpoint, no auth required).
    Returns categories with show_in_explore=True for use in AI Effects page.
    Visibility in AI Effects page is independent of is_active (page generation).
    """
    try:
        from ..models.effects_page import EffectsPage
        
        # Get all level 1 categories that should be shown in AI Effects page
        level1_categories = db.query(EffectsPage).filter(
            EffectsPage.level == 1,
            EffectsPage.show_in_explore == True
        ).order_by(EffectsPage.sort_order, EffectsPage.category_name).all()
        
        tree_data = []
        for parent in level1_categories:
            parent_dict = parent.to_dict(include_children=False, include_parent=False)
            
            # Get children that should be shown in AI Effects page
            children = db.query(EffectsPage).filter(
                EffectsPage.parent_id == parent.id,
                EffectsPage.show_in_explore == True
            ).order_by(EffectsPage.sort_order, EffectsPage.category_name).all()
            
            parent_dict["children"] = [child.to_dict(include_children=False, include_parent=False) for child in children]
            tree_data.append(parent_dict)
        
        return success_response(
            data=tree_data,
            message="Effects pages tree retrieved successfully"
        )
    except Exception as e:
        logger.error(f"Error fetching effects pages tree: {e}")
        return error_response(
            message="Failed to fetch effects pages tree",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.get("/api/effects-pages/tree-active")
def get_effects_tree_active(
    db: Session = Depends(get_db)
):
    """
    Get effects pages tree structure for magic page search (public endpoint, no auth required).
    Returns only active effects pages (is_active=True), regardless of show_in_explore setting.
    Used in /magic page to show all active effects for searching.
    """
    try:
        from ..models.effects_page import EffectsPage
        
        # Get all active level 1 categories (only filter by is_active, not show_in_explore)
        level1_categories = db.query(EffectsPage).filter(
            EffectsPage.level == 1,
            EffectsPage.is_active == True
        ).order_by(EffectsPage.sort_order, EffectsPage.category_name).all()
        
        tree_data = []
        for parent in level1_categories:
            parent_dict = parent.to_dict(include_children=False, include_parent=False)
            
            # Get active children (only filter by is_active, not show_in_explore)
            children = db.query(EffectsPage).filter(
                EffectsPage.parent_id == parent.id,
                EffectsPage.is_active == True
            ).order_by(EffectsPage.sort_order, EffectsPage.category_name).all()
            
            parent_dict["children"] = [child.to_dict(include_children=False, include_parent=False) for child in children]
            tree_data.append(parent_dict)
        
        return success_response(
            data=tree_data,
            message="Active effects pages tree retrieved successfully"
        )
    except Exception as e:
        logger.error(f"Error fetching active effects pages tree: {e}")
        return error_response(
            message="Failed to fetch active effects pages tree",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.get("/api/generate-pages/tree-active")
def get_generate_tree_active(
    db: Session = Depends(get_db)
):
    """
    Get generate pages tree structure (public endpoint, no auth required).
    Returns only active generate pages (is_active=True).
    Used in /generate page to show all active categories.
    """
    try:
        from ..models.generate_page import GeneratePage
        
        # Get all active level 1 categories
        level1_categories = db.query(GeneratePage).filter(
            GeneratePage.level == 1,
            GeneratePage.is_active == True
        ).order_by(GeneratePage.sort_order, GeneratePage.category_name).all()
        
        tree_data = []
        for parent in level1_categories:
            parent_dict = parent.to_dict(include_children=False)
            
            # Get active children
            children = db.query(GeneratePage).filter(
                GeneratePage.parent_id == parent.id,
                GeneratePage.is_active == True
            ).order_by(GeneratePage.sort_order, GeneratePage.category_name).all()
            
            parent_dict["children"] = [child.to_dict(include_children=False) for child in children]
            tree_data.append(parent_dict)
        
        return success_response(
            data=tree_data,
            message="Active generate pages tree retrieved successfully"
        )
    except Exception as e:
        logger.error(f"Error fetching active generate pages tree: {e}")
        return error_response(
            message="Failed to fetch active generate pages tree",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.get("/api/category-pages/by-path{page_path:path}")
def get_category_page_by_path(
    page_path: str,
    db: Session = Depends(get_db)
):
    """
    Get category page configuration by page_path (public endpoint, no auth required).
    Returns only active category pages.
    Supports both level 1 (e.g., /category/love) and level 2 (e.g., /category/love/romantic-couple) paths.
    """
    try:
        from ..models.category_page import CategoryPage
        
        # Ensure page_path starts with /
        if not page_path.startswith('/'):
            page_path = '/' + page_path
        
        # Query category page by page_path and is_active=True
        category_page = db.query(CategoryPage).filter(
            CategoryPage.page_path == page_path,
            CategoryPage.is_active == True
        ).first()
        
        if not category_page:
            return error_response(
                message="Category page not found or not active",
                status_code=status.HTTP_404_NOT_FOUND
            )
        
        return success_response(
            data=category_page.to_dict(include_children=False),
            message="Category page retrieved successfully"
        )
    except Exception as e:
        logger.error(f"Error fetching category page by path {page_path}: {e}")
        return error_response(
            message="Failed to fetch category page",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.get("/api/category-pages/{category_id}/children")
def get_category_children(
    category_id: int,
    db: Session = Depends(get_db)
):
    """
    Get all active child categories (level 2) for a given category (public endpoint, no auth required).
    Used for filtering subcategories on level 1 category pages.
    Returns only active level 2 categories, regardless of show_in_explore setting.
    """
    try:
        from ..models.category_page import CategoryPage
        
        # Verify parent category exists and is active
        parent_category = db.query(CategoryPage).filter(
            CategoryPage.id == category_id,
            CategoryPage.is_active == True
        ).first()
        
        if not parent_category:
            return error_response(
                message="Category not found or not active",
                status_code=status.HTTP_404_NOT_FOUND
            )
        
        # Get all active children (level 2) for this parent
        children = db.query(CategoryPage).filter(
            CategoryPage.parent_id == category_id,
            CategoryPage.is_active == True,
            CategoryPage.level == 2
        ).order_by(CategoryPage.sort_order, CategoryPage.category_name).all()
        
        children_data = [child.to_dict(include_children=False) for child in children]
        
        return success_response(
            data=children_data,
            message="Category children retrieved successfully"
        )
    except Exception as e:
        logger.error(f"Error fetching category children for category_id {category_id}: {e}")
        return error_response(
            message="Failed to fetch category children",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
