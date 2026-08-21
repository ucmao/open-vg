import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app.models.base import SessionLocal
from app.models.generation_model import GenerationModel
from app.models.generate_page import GeneratePage
from app.services.generate_page_sync import upsert_generate_page_for_model
from app.utils.url_slug import slugify

def final_fix():
    db = SessionLocal()
    try:
        # 1. ，
        mapping = {
            "TXT2VID": "text-to-video",
            "text2video": "text-to-video",
            "TEXT2VIDEO": "text-to-video",
            "TXT2VIDEO": "text-to-video",
            "IMG2VID": "image-to-video",
            "img2video": "image-to-video",
            "IMG2VIDEO": "image-to-video",
            "TXT2IMG": "text-to-image",
            "text2img": "text-to-image",
            "TEXT2IMG": "text-to-image",
            "IMG2IMG": "image-to-image",
            "img2img": "image-to-image",
            "IMG FX": "image-effects",
            "VID FX": "video-effects",
            "video-effects": "video-effects",
            "image-effects": "image-effects"
        }

        print("--- Step 1:  Work Type ---")
        models = db.query(GenerationModel).all()
        for m in models:
            old = m.work_type
            if old in mapping:
                m.work_type = mapping[old]
                print(f"Fixed: {m.name} ({old} -> {m.work_type})")
            elif not old:
                m.work_type = "text-to-image" #
        db.commit()

        print("\n--- Step 2:  ---")
        db.query(GeneratePage).delete()
        db.commit()

        defaults = [
            ("video-effects", "VID FX"),
            ("image-effects", "IMG FX"),
            ("image-to-video", "IMG2VID"),
            ("text-to-video", "TXT2VID"),
            ("image-to-image", "IMG2IMG"),
            ("text-to-image", "TXT2IMG"),
        ]
        
        for name, title in defaults:
            new_cat = GeneratePage(
                category_name=name,
                level=1,
                page_path=f"/generate/{slugify(name)}",
                title=f"{title} AI",
                is_active=True,
                sort_order=defaults.index((name, title))
            )
            db.add(new_cat)
        db.commit()

        print("\n--- Step 3:  ---")
        for m in models:
            upsert_generate_page_for_model(db, m.work_type, m.model_key, m.name)
        
        db.commit()
        print("\n[] ！")

    except Exception as e:
        db.rollback()
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    final_fix()
