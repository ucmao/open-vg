"""One-off script to migrate work_type values for models and workflows.

Usage (from backend directory):

    python scripts/update_work_types.py

This will update `generation_models.work_type` and `workflows.work_type`
according to the mapping defined below.
"""

import sys
from pathlib import Path

# Add backend directory to sys.path so we can import app modules
backend_dir = str(Path(__file__).parent.parent)
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app.models.base import SessionLocal  # type: ignore
from app.models.generation_model import GenerationModel  # type: ignore
from app.models.workflow import Workflow  # type: ignore


# Old -> new work_type mapping
# Note:
# - First group handles the original legacy values.
# - Second group fixes values produced by the first (buggy) version of this script.
WORK_TYPE_MAPPING = {
    # Original legacy values -> final values
    "img2video": "image-to-video",
    "text2video": "text-to-video",
    "text2img": "text-to-image",
    "img2img": "image-to-image",
    "video_effects": "video-effects",
    "img_effects": "image-effects",
    # Fix values written by the buggy script version:
    #   video_effects  -> image-effects
    #   img_effects    -> text-effects
    # We now map them to the correct final values.
    "image-effects": "video-effects",  # rows that used to be video_effects
    "text-effects": "image-effects",   # rows that used to be img_effects
}


def migrate_work_types() -> None:
    session = SessionLocal()
    try:
        print("Starting work_type migration...")
        print("Mapping:")
        for old, new in WORK_TYPE_MAPPING.items():
            print(f"  {old!r} -> {new!r}")

        total_models_updated = 0
        total_workflows_updated = 0

        # Update GenerationModel.work_type
        for old, new in WORK_TYPE_MAPPING.items():
            affected = (
                session.query(GenerationModel)
                .filter(GenerationModel.work_type == old)
                .update({GenerationModel.work_type: new}, synchronize_session=False)
            )
            if affected:
                print(f"[GenerationModel] {old!r} -> {new!r}: {affected} rows")
                total_models_updated += affected

        # Update Workflow.work_type
        for old, new in WORK_TYPE_MAPPING.items():
            affected = (
                session.query(Workflow)
                .filter(Workflow.work_type == old)
                .update({Workflow.work_type: new}, synchronize_session=False)
            )
            if affected:
                print(f"[Workflow] {old!r} -> {new!r}: {affected} rows")
                total_workflows_updated += affected

        session.commit()
        print("Migration completed successfully.")
        print(f"Total GenerationModel rows updated: {total_models_updated}")
        print(f"Total Workflow rows updated: {total_workflows_updated}")
    except Exception as exc:  # pragma: no cover - safety net
        session.rollback()
        print(f"Migration failed, rolled back. Error: {exc}")
        raise
    finally:
        session.close()


if __name__ == "__main__":
    migrate_work_types()

