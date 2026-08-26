"""
Profile-aware offline seed importer.

Profiles:
  core  - runtime configuration only, with a curated model subset
  safe  - core plus local, neutral demo content (default)
  full  - historical exported dataset with external media (explicit opt-in)
"""
import os
import sys
import json
from datetime import datetime
from enum import Enum
from pathlib import Path

from sqlalchemy import DateTime, text

backend_dir = Path(__file__).resolve().parents[1]
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.models.base import get_db, engine
from app.models.seo_config import SeoConfig, PageSeo
from app.models.system_config import SystemConfig
from app.models.generation_model import GenerationModel, APILibrary
from app.models.workflow import Workflow
from app.models.category_page import CategoryPage
from app.models.generate_page import GeneratePage
from app.models.effects_page import EffectsPage
from app.models.homepage_block import HomepageBlock
from app.models.topic import Topic
from app.models.blog import BlogCategory, BlogPost
from app.models.recharge_package import RechargePackage
from app.models.recharge_promo import RechargePromo
from app.models.user import User
from app.models.work import Work
from app.utils.seed_sanitizer import sanitize_seed_data
from app.utils.logger import logger

DATA_DIR = Path(backend_dir) / "scripts" / "seed_data"
SAFE_DATA_DIR = DATA_DIR / "safe"
SEED_PROFILES = {"core", "safe", "full"}

# Deliberately allowlisted: new exported models do not silently become part of
# the public default dataset. Full exports remain available through opt-in.
SAFE_MODEL_KEYS = {
    "ai-aging-filter-ajq4",
    "ai-character-swap-3erd",
    "ai-teacher-generator-op7y",
    "ai-travel-generator-da6l",
    "ai-walk-generator-ymet",
    "cat-cooking-generator-06sk",
    "flux2-klein-a8su",
    "g-0xcn",
    "g-jkl9",
    "google-veo-3-1-hdol",
    "google-veo-3-1-jtki",
    "hailuo-2-3-n1c5",
    "hailuo-2-3-pzdp",
    "kling-v2-6-yjjl",
    "nano-banana-2-t2i",
    "nano-banana-2-vtur",
    "nano-banana-pro-geug",
    "qwen-image-eh68",
    "s-6dbn",
    "s-f0f5",
    "s-jvfs",
    "seedance-1-5-pro-irm6",
    "seedance-1-5-pro-uyfh",
    "seedance-2-0-etvr",
    "seedance-2-0-pro-xkyd",
    "seedream-4-5-w1j4",
    "vidgen-4pan",
    "vidgen-imno",
    "vidgen-pjpm",
    "vidgen-x5ij",
    "wan-2-6-i2v-jmj4",
}


def _read_json(path: Path):
    with path.open("r", encoding="utf-8") as file_handle:
        return json.load(file_handle)


def _safe_dependency_ids() -> tuple[set[int], set[int]]:
    models = _read_json(DATA_DIR / "generation_models.json")
    workflow_ids = {
        item["workflow_id"]
        for item in models
        if item.get("model_key") in SAFE_MODEL_KEYS and item.get("workflow_id")
    }
    workflows = _read_json(DATA_DIR / "workflows.json")
    api_ids = {
        node["api_id"]
        for workflow in workflows
        if workflow.get("id") in workflow_ids
        for node in (workflow.get("nodes") or [])
        if node.get("type") == "api_call" and node.get("api_id") is not None
    }
    return workflow_ids, api_ids


def load_seed_items(filename: str, profile: str):
    """Load and sanitize one file according to the selected profile."""
    override = SAFE_DATA_DIR / filename
    path = override if profile != "full" and override.exists() else DATA_DIR / filename
    if not path.exists():
        return None

    items = _read_json(path)
    if profile != "full" and path.parent == DATA_DIR:
        workflow_ids, api_ids = _safe_dependency_ids()
        if filename == "generation_models.json":
            items = [item for item in items if item.get("model_key") in SAFE_MODEL_KEYS]
        elif filename == "workflows.json":
            items = [item for item in items if item.get("id") in workflow_ids]
        elif filename == "api_library.json":
            items = [item for item in items if item.get("id") in api_ids]
        elif filename == "generate_pages.json":
            items = [
                item
                for item in items
                if item.get("parent_id") is None
                or str(item.get("page_path", "")).rsplit("/", 1)[-1] in SAFE_MODEL_KEYS
            ]

    # Exported configuration may reference an administrator that exists only
    # in the source deployment. Safe/core imports are ownership-neutral and
    # must work after migrations on a completely empty database.
    if profile != "full" and filename in {"generation_models.json", "workflows.json"}:
        items = [{**item, "created_by": None} for item in items]

    return sanitize_seed_data(
        items,
        allow_external_media=(profile == "full"),
    )

def is_different(curr, v):
    if curr == v:
        return False
    if isinstance(curr, Enum):
        return v not in (curr.name, curr.value)
    if isinstance(curr, (dict, list)) or isinstance(v, (dict, list)):
        try:
            return json.dumps(curr, sort_keys=True) != json.dumps(v, sort_keys=True)
        except Exception:
            return True
    return str(curr) != str(v)

def normalize_value(column, value):
    """Convert JSON scalar values to the Python types expected by SQLAlchemy."""
    if value == "None":
        return None
    if value is not None and isinstance(column.type, DateTime) and isinstance(value, str):
        return datetime.fromisoformat(value)
    return value


def order_self_referencing_rows(items, existing_ids):
    """Ensure parent rows are flushed before children with self foreign keys."""
    pending = list(items)
    ordered = []
    available = set(existing_ids)

    while pending:
        ready = [
            item
            for item in pending
            if item.get("parent_id") is None or item.get("parent_id") in available
        ]
        if not ready:
            unresolved = sorted({item.get("parent_id") for item in pending})
            raise ValueError(f"Unresolved parent_id values in seed data: {unresolved}")
        ordered.extend(ready)
        available.update(item.get("id") for item in ready)
        ready_ids = {id(item) for item in ready}
        pending = [item for item in pending if id(item) not in ready_ids]

    return ordered


def import_table_data(db, filename, model_cls, pk_field='id', preserve_when_empty=(), profile="safe"):
    items = load_seed_items(filename, profile)
    if items is None:
        print(f"  ⚠️ Seed file not found: {filename}, skipping...", flush=True)
        return 0

    columns = {c.name: c for c in model_cls.__table__.columns}
    inserted = 0
    updated = 0

    existing_list = db.query(model_cls).all()
    existing_map = {
        getattr(obj, pk_field): obj
        for obj in existing_list
        if getattr(obj, pk_field, None) is not None
    }

    if "parent_id" in columns:
        items = order_self_referencing_rows(items, existing_map)

    new_objs = []
    for item in items:
        valid_kwargs = {}
        for k, v in item.items():
            if k in columns:
                valid_kwargs[k] = normalize_value(columns[k], v)

        pk_val = valid_kwargs.get(pk_field)
        existing = existing_map.get(pk_val) if pk_val is not None else None

        if not existing:
            new_objs.append(model_cls(**valid_kwargs))
            inserted += 1
        else:
            changed = False
            for k, v in valid_kwargs.items():
                if k in preserve_when_empty and v in (None, ""):
                    continue
                curr = getattr(existing, k, None)
                if is_different(curr, v):
                    setattr(existing, k, v)
                    changed = True
            if changed:
                updated += 1

    if new_objs:
        db.add_all(new_objs)

    db.flush()
    print(f"  ✅ Imported {len(items)} records for {model_cls.__tablename__} ({inserted} new, {updated} updated)", flush=True)
    return len(items)


def synchronize_table_to_seed(db, filename, model_cls, pk_field="id", profile="safe"):
    """Delete rows absent from the canonical seed file.

    Models, workflows, and provider APIs form one versioned runtime bundle. Keeping
    additive leftovers here can expose parameterless legacy models in the product UI.
    """
    items = load_seed_items(filename, profile)
    if items is None:
        raise ValueError(f"Missing canonical seed file: {filename}")

    seed_keys = {
        item[pk_field]
        for item in items
        if item.get(pk_field) is not None
    }
    if not seed_keys:
        raise ValueError(f"Refusing to synchronize {model_cls.__tablename__} from an empty seed")

    removed = db.query(model_cls).filter(
        getattr(model_cls, pk_field).notin_(seed_keys)
    ).delete(synchronize_session=False)
    db.flush()
    print(
        f"  🧹 Removed {removed} obsolete records from {model_cls.__tablename__}",
        flush=True,
    )
    return removed


def reset_postgres_sequences(db, model_classes):
    """Advance PostgreSQL sequences after importing rows with explicit IDs."""
    if db.bind.dialect.name != "postgresql":
        return

    for model_cls in model_classes:
        table_name = model_cls.__tablename__
        if "id" not in model_cls.__table__.columns:
            continue
        db.execute(
            text(
                "SELECT setval(pg_get_serial_sequence(:table_name, 'id'), "
                "GREATEST(COALESCE(MAX(id), 1), 1), MAX(id) IS NOT NULL) "
                f'FROM "{table_name}"'
            ),
            {"table_name": table_name},
        )

def import_all(profile=None):
    profile = (profile or os.getenv("SEED_PROFILE", "safe")).strip().lower()
    if profile not in SEED_PROFILES:
        raise ValueError(f"SEED_PROFILE must be one of: {', '.join(sorted(SEED_PROFILES))}")
    if profile == "full" and os.getenv("ALLOW_UNSAFE_FULL_SEED", "false").lower() not in {
        "1", "true", "yes", "on"
    }:
        raise RuntimeError(
            "The full seed contains historical external media and non-neutral content. "
            "Set ALLOW_UNSAFE_FULL_SEED=true only after reviewing its licenses and content."
        )

    print(f"🚀 Importing '{profile}' Seed Dataset into Database...\n", flush=True)
    db = next(get_db())

    try:
        # Order matters for foreign key relationships
        common = {"profile": profile}
        import_table_data(db, "page_seos.json", PageSeo, pk_field="page_name", **common)
        import_table_data(db, "seo_configs.json", SeoConfig, pk_field="config_key", **common)
        import_table_data(
            db,
            "system_configs.json",
            SystemConfig,
            pk_field="config_key",
            preserve_when_empty=("config_value",),
            **common,
        )
        import_table_data(db, "api_library.json", APILibrary, **common)
        import_table_data(db, "workflows.json", Workflow, **common)
        import_table_data(db, "generation_models.json", GenerationModel, **common)
        import_table_data(db, "category_pages.json", CategoryPage, **common)
        import_table_data(db, "generate_pages.json", GeneratePage, **common)
        import_table_data(db, "effects_pages.json", EffectsPage, **common)
        import_table_data(db, "recharge_packages.json", RechargePackage, **common)

        if profile in {"safe", "full"}:
            import_table_data(db, "homepage_blocks.json", HomepageBlock, **common)
            import_table_data(db, "blog_categories.json", BlogCategory, **common)
            import_table_data(db, "topics.json", Topic, **common)
            import_table_data(db, "sample_users.json", User, **common)
            import_table_data(db, "recharge_promos.json", RechargePromo, **common)
            import_table_data(db, "blog_posts.json", BlogPost, **common)
            import_table_data(db, "sample_works.json", Work, **common)

        # Only the explicitly requested historical full export is authoritative.
        # Safe/core profiles are deliberately additive: an upgrade must never
        # delete operator-created models merely because they are not allowlisted.
        if profile == "full":
            synchronize_table_to_seed(db, "generation_models.json", GenerationModel, profile=profile)
            synchronize_table_to_seed(db, "workflows.json", Workflow, profile=profile)
            synchronize_table_to_seed(db, "api_library.json", APILibrary, profile=profile)

        reset_postgres_sequences(
            db,
            (
                APILibrary,
                GenerationModel,
                Workflow,
                CategoryPage,
                GeneratePage,
                EffectsPage,
                HomepageBlock,
                Topic,
                BlogCategory,
                BlogPost,
                RechargePackage,
                RechargePromo,
                User,
                Work,
            ),
        )
        db.commit()

        from app.models.generation_config import invalidate_cache
        invalidate_cache()

        print(f"\n✨ '{profile}' seed dataset imported successfully!", flush=True)
    except Exception as e:
        db.rollback()
        print(f"❌ Error during seed dataset import: {e}", flush=True)
        raise
    finally:
        db.close()

if __name__ == "__main__":
    import_all()
