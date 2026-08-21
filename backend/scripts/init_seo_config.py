"""
Script to initialize default SEO configurations.
"""
import sys
import os

# Add parent directory to path to import app modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.models.base import get_db
from app.models.seo_config import SeoConfig


def init_seo_configs():
    """Initialize default SEO configurations."""
    db = next(get_db())
    
    try:
        default_configs = [
            # Basic Settings
            {
                "config_key": "base_url",
                "config_value": "https://yoursite.com",
                "description": "（ robots.txt ）"
            },
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
                "description": " (/category/...)"
            },
            {
                "config_key": "sitemap_include_effects",
                "config_value": "true",
                "description": " (/effects/...)"
            },
            {
                "config_key": "sitemap_include_generate",
                "config_value": "true",
                "description": " (/generate/...)"
            },
            # Robots.txt
            {
                "config_key": "robots_txt_custom",
                "config_value": None,
                "description": " robots.txt （）"
            }
        ]
        
        created_count = 0
        updated_count = 0
        
        for config_data in default_configs:
            existing = db.query(SeoConfig).filter(
                SeoConfig.config_key == config_data["config_key"]
            ).first()
            
            if existing:
                print(f"⚠️  Config '{config_data['config_key']}' already exists, skipping...")
                updated_count += 1
            else:
                new_config = SeoConfig(
                    config_key=config_data["config_key"],
                    config_value=config_data["config_value"],
                    is_enabled=True,
                    description=config_data["description"]
                )
                db.add(new_config)
                created_count += 1
                print(f"✅ Created config: {config_data['config_key']}")
        
        db.commit()
        
        print(f"\n📊 Summary:")
        print(f"   - Created: {created_count}")
        print(f"   - Already exists: {updated_count}")
        print(f"\n✨ SEO configuration initialized successfully!")
        print(f"\n📝 Next steps:")
        print(f"   1. Update 'base_url' to your actual website URL")
        print(f"   2. Configure which content types to include in sitemap")
        print(f"   3. Optionally customize robots.txt content")
        print(f"\n🌐 Access via:")
        print(f"   - Sitemap: {config_data.get('config_value', 'https://yoursite.com')}/sitemap.xml")
        print(f"   - Robots: {config_data.get('config_value', 'https://yoursite.com')}/robots.txt")
        print(f"   - Admin Panel: /admin/seo")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error initializing SEO configs: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    print("🚀 Initializing SEO configurations...\n")
    init_seo_configs()
