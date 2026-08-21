import os
import sys

# Add the current directory to sys.path to import app modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.models.base import SessionLocal
from app.models.generation_model import GenerationModel
from app.models.generate_page import GeneratePage
from app.services.generate_page_sync import upsert_generate_page_for_model

def cleanup():
    db = SessionLocal()
    try:
        # 1. Define the mapping from "bad" names to "correct" names
        # Based on your UI, the correct ones seem to be the short ones
        mapping = {
            "IMG2VIDEO": "IMG2VID",
            "TEXT2VIDEO": "TXT2VID",
            "TEXT2IMG": "TXT2IMG",
            "IMG2IMG": "IMG2IMG", # If there's a duplicate, we keep the one already in level 1
        }
        
        # Lowercase mapping common in some setups, let's also handle those if they exist
        mapping.update({
            "text-to-video": "TXT2VID",
            "image-to-video": "IMG2VID",
            "text-to-image": "TXT2IMG",
            "image-to-image": "IMG2IMG",
        })

        print("--- Step 1: Updating Models ---")
        models = db.query(GenerationModel).all()
        for model in models:
            old_type = model.work_type
            if old_type in mapping:
                new_type = mapping[old_type]
                print(f"Updating model '{model.name}': {old_type} -> {new_type}")
                model.work_type = new_type
        
        db.commit()

        print("\n--- Step 2: Cleaning up redundant Category Pages (Level 1) ---")
        # Find all level 1 categories
        all_categories = db.query(GeneratePage).filter(GeneratePage.level == 1).all()
        
        # We want to keep: IMG2VID, TXT2VID, IMG2IMG, TXT2IMG
        # We want to delete: IMG2VIDEO, TEXT2VIDEO, TEXT2IMG, and any duplicates
        keep_names = ["IMG2VID", "TXT2VID", "IMG2IMG", "TXT2IMG", "IMG FX"]
        
        for cat in all_categories:
            if cat.category_name not in keep_names:
                print(f"Removing redundant category: {cat.category_name} (ID: {cat.id})")
                # Delete children first (level 2 pages associated with this bad category)
                db.query(GeneratePage).filter(GeneratePage.parent_id == cat.id).delete()
                # Delete the category itself
                db.delete(cat)
            else:
                # If it's a "keep" name, check if there are duplicates and keep only the oldest/first one
                duplicates = db.query(GeneratePage).filter(
                    GeneratePage.level == 1, 
                    GeneratePage.category_name == cat.category_name,
                    GeneratePage.id != cat.id
                ).all()
                for dup in duplicates:
                    print(f"Removing duplicate category: {dup.category_name} (ID: {dup.id})")
                    db.query(GeneratePage).filter(GeneratePage.parent_id == dup.id).delete()
                    db.delete(dup)

        db.commit()

        print("\n--- Step 3: Re-syncing Model Pages ---")
        # Now that categories are clean, re-run the sync for all models
        models = db.query(GenerationModel).all()
        for model in models:
            success = upsert_generate_page_for_model(
                db, model.work_type, model.model_key, model.name
            )
            if success:
                print(f"Synced page for: {model.name} under {model.work_type}")
            else:
                print(f"Failed to sync page for: {model.name} (Check if category {model.work_type} exists)")

        db.commit()
        print("\nCleanup Completed Successfully!")

    except Exception as e:
        db.rollback()
        print(f"Error during cleanup: {str(e)}")
    finally:
        db.close()

if __name__ == "__main__":
    cleanup()
