import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app.models.base import SessionLocal
from app.models.generate_page import GeneratePage
from app.services.generate_page_sync import upsert_generate_page_for_model
from app.models.generation_model import GenerationModel
from app.utils.url_slug import slugify

def restore_categories():
    db = SessionLocal()
    try:
        # Get all unique work_types currently used by models
        models = db.query(GenerationModel).all()
        work_types = set([m.work_type for m in models if m.work_type])
        
        print("Required Level 1 Categories based on current models:", work_types)

        # Base default mapping to provide nice titles if missing
        default_titles = {
            "TXT2VID": "Text to Video",
            "IMG2VID": "Image to Video",
            "TXT2IMG": "Text to Image",
            "IMG2IMG": "Image to Image",
            "text2img": "Text to Image",
            "img2img": "Image to Image",
            "text2video": "Text to Video",
            "img2video": "Image to Video",
            "video-effects": "Video Effects",
            "image-effects": "Image Effects",
        }

        for wt in work_types:
            existing = db.query(GeneratePage).filter(
                GeneratePage.level == 1,
                GeneratePage.category_name == wt
            ).first()

            if not existing:
                title = default_titles.get(wt, wt.replace("-", " ").title())
                slug = slugify(wt)
                new_cat = GeneratePage(
                    category_name=wt,
                    level=1,
                    page_path=f"/generate/{slug}",
                    title=f"{title} AI Tools",
                    description=f"Explore the best {title} AI tools.",
                    display_description=title,
                    is_active=True,
                    sort_order=0
                )
                db.add(new_cat)
                print(f"Created missing Level 1 category: {wt}")
                
        db.commit()

        print("\n--- Re-syncing all models ---")
        for m in models:
            res = upsert_generate_page_for_model(db, m.work_type, m.model_key, m.name)
            if res:
                print(f"Successfully synced page for: {m.name} -> {m.work_type}")
            else:
                print(f"Warning: Failed to sync page for {m.name} -> {m.work_type}. Is work_type empty?")

        db.commit()
        print("\nCategory restore complete!")
    except Exception as e:
        db.rollback()
        print(f"Error during restore: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    restore_categories()
