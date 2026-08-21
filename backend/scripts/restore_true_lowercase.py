import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app.models.base import SessionLocal
from app.models.generation_model import GenerationModel
from app.models.generate_page import GeneratePage
from app.services.generate_page_sync import upsert_generate_page_for_model
from app.utils.url_slug import slugify

def fix_to_lowercase():
    db = SessionLocal()
    try:
        # Correctly map back to the system's expected full, lowecase names
        mapping = {
            "IMG2VID": "image-to-video",
            "TXT2VID": "text-to-video",
            "TXT2IMG": "text-to-image",
            "IMG2IMG": "image-to-image",
            "IMG FX": "image-effects"
        }

        print("--- Step 1: Updating Models back to correct lowercase ---")
        models = db.query(GenerationModel).all()
        for model in models:
            old_type = model.work_type
            if old_type in mapping:
                new_type = mapping[old_type]
                print(f"Reverting '{model.name}': {old_type} -> {new_type}")
                model.work_type = new_type
        
        db.commit()

        print("\n--- Step 2: Wiping ALL wrong level-1 & level-2 categories ---")
        db.query(GeneratePage).delete() # Wipe cleanly and rebuild properly
        db.commit()

        print("\n--- Step 3: Recreating the 6 core default categories ---")
        defaults = [
            ("video-effects", ""),
            ("image-effects", ""),
            ("image-to-video", ""),
            ("text-to-video", ""),
            ("image-to-image", ""),
            ("text-to-image", ""),
        ]
        
        for name, title in defaults:
            new_cat = GeneratePage(
                category_name=name,
                level=1,
                page_path=f"/generate/{slugify(name)}",
                title=f"{title} AI Tools",
                description=f"Explore the best {title} AI tools.",
                display_description=title,
                is_active=True,
                sort_order=defaults.index((name, title))
            )
            db.add(new_cat)
            print(f"Created Base Category: {name}")

        db.commit()

        print("\n--- Step 4: Re-syncing all model sub-pages ---")
        for m in models:
            if m.work_type:
                res = upsert_generate_page_for_model(db, m.work_type, m.model_key, m.name)
                if res:
                    print(f"Synced {m.name} -> {m.work_type}")
        
        db.commit()
        print("\nSystem successfully restored to its true original state!")

    except Exception as e:
        db.rollback()
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    fix_to_lowercase()
