"""
Importer for Complete Off-Line Seed Dataset (Ultra-Fast Delta Import)
======================================================================
This script loads exported JSON configuration files from `scripts/seed_data/`
and safely upserts all configuration and sample demo data into the target database.
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

DATA_DIR = os.path.join(backend_dir, "scripts", "seed_data")

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


def import_table_data(db, filename, model_cls, pk_field='id', preserve_when_empty=()):
    filepath = os.path.join(DATA_DIR, filename)
    if not os.path.exists(filepath):
        print(f"  ⚠️ Seed file not found: {filename}, skipping...", flush=True)
        return 0

    with open(filepath, "r", encoding="utf-8") as f:
        # Defense in depth: never write the production hostname to a freshly
        # initialized database, even if a future export was not sanitized.
        items = sanitize_seed_data(json.load(f))

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

def import_all():
    print("🚀 Importing Complete Seed Dataset into Database...\n", flush=True)
    db = next(get_db())

    try:
        # Order matters for foreign key relationships
        import_table_data(db, "page_seos.json", PageSeo, pk_field="page_name")
        import_table_data(db, "seo_configs.json", SeoConfig, pk_field="config_key")
        import_table_data(
            db,
            "system_configs.json",
            SystemConfig,
            pk_field="config_key",
            preserve_when_empty=("config_value",),
        )
        import_table_data(db, "api_library.json", APILibrary, pk_field="id")
        import_table_data(db, "workflows.json", Workflow, pk_field="id")
        import_table_data(db, "generation_models.json", GenerationModel, pk_field="id")
        import_table_data(db, "category_pages.json", CategoryPage, pk_field="id")
        import_table_data(db, "generate_pages.json", GeneratePage, pk_field="id")
        import_table_data(db, "effects_pages.json", EffectsPage, pk_field="id")
        import_table_data(db, "homepage_blocks.json", HomepageBlock, pk_field="id")
        import_table_data(db, "blog_categories.json", BlogCategory, pk_field="id")
        import_table_data(db, "topics.json", Topic, pk_field="id")
        import_table_data(db, "recharge_packages.json", RechargePackage, pk_field="id")
        import_table_data(db, "sample_users.json", User, pk_field="id")
        import_table_data(db, "recharge_promos.json", RechargePromo, pk_field="id")
        import_table_data(db, "blog_posts.json", BlogPost, pk_field="id")
        import_table_data(db, "sample_works.json", Work, pk_field="id")

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

        print("\n✨ All Seed Dataset tables imported successfully!", flush=True)
    except Exception as e:
        db.rollback()
        print(f"❌ Error during seed dataset import: {e}", flush=True)
        raise
    finally:
        db.close()

if __name__ == "__main__":
    import_all()
