"""
Seed Data Export Script (Psycopg2 Direct + Autocommit)
======================================================
This script connects directly via psycopg2 to the remote production PostgreSQL database, extracts:
1. All 100% full system configurations.
2. Ten curated image/video works for every Explore Gallery top-level category.
3. Keeps public CDN media URLs; the frontend handles unavailable media with a placeholder.
"""
import argparse
import os
import sys
import json
from pathlib import Path
import psycopg2
import psycopg2.extras

backend_dir = Path(__file__).resolve().parents[1]
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.utils.seed_sanitizer import sanitize_seed_data

BASE_DIR = str(backend_dir)
DATA_DIR = os.path.join(BASE_DIR, "scripts", "seed_data")

os.makedirs(DATA_DIR, exist_ok=True)

EXPLORE_CATEGORY_WORK_QUOTA = 10
FEATURED_VIDEO_PREVIEW_QUOTAS = {
    "text-to-video": 15,
    "image-to-video": 15,
}
LANDSCAPE_VIDEO_ASPECT_RATIOS = {"16:9", "landscape"}

VALID_DEMO_WORK_SQL = """
    share_status = 'APPROVED'
    AND status = 'SUCCESS'
    AND COALESCE(is_banned, false) = false
    AND COALESCE(hidden, false) = false
    AND (nsfw_status IS NULL OR nsfw_status = 'APPROVED')
    AND deleted_at IS NULL
    AND file_url IS NOT NULL
    AND file_url <> ''
    AND thumbnail_url IS NOT NULL
    AND thumbnail_url <> ''
"""

SHOWCASE_WORK_ORDER_SQL = """
    is_featured DESC NULLS LAST,
    like_count DESC NULLS LAST,
    favorite_count DESC NULLS LAST,
    view_count DESC NULLS LAST,
    id DESC
"""

def default_json_serializer(o):
    return str(o)

def export_table(conn, table):
    print(f"📦 Exporting full table: {table}...", flush=True)
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        cur.execute(f"SELECT * FROM {table};")
        dict_rows = [dict(r) for r in cur.fetchall()]
        
    if table == "page_seos":
        for r in dict_rows:
            r["is_enabled"] = True
    elif table == "system_configs":
        # Never export production credentials into the open-source seed dataset.
        for r in dict_rows:
            if r.get("is_encrypted"):
                r["config_value"] = None
    elif table == "recharge_promos":
        # Per-user promotions are operational data, not reusable seed config.
        dict_rows = [r for r in dict_rows if r.get("user_id") is None]

    # Exported content may contain the production hostname in URLs, HTML,
    # nested topic blocks, SEO fields, model defaults, or workflow JSON.
    dict_rows = sanitize_seed_data(dict_rows)
            
    out_file = os.path.join(DATA_DIR, f"{table}.json")
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(dict_rows, f, ensure_ascii=False, indent=2, default=default_json_serializer)
    print(f"  ✅ Saved {len(dict_rows)} records to {table}.json", flush=True)


def compact_model_bundle():
    """Keep only workflows and provider APIs used by the canonical product models."""
    def load_seed(filename):
        with open(os.path.join(DATA_DIR, filename), "r", encoding="utf-8") as file_handle:
            return json.load(file_handle)

    models = load_seed("generation_models.json")
    workflows = load_seed("workflows.json")
    apis = load_seed("api_library.json")

    workflow_ids = {
        model.get("workflow_id")
        for model in models
        if model.get("workflow_id") is not None
    }
    workflows = [item for item in workflows if item.get("id") in workflow_ids]
    api_ids = {
        node.get("api_id")
        for workflow in workflows
        for node in (workflow.get("nodes") or [])
        if node.get("type") == "api_call" and node.get("api_id") is not None
    }
    apis = [item for item in apis if item.get("id") in api_ids]

    for filename, items in (("workflows.json", workflows), ("api_library.json", apis)):
        with open(os.path.join(DATA_DIR, filename), "w", encoding="utf-8") as file_handle:
            json.dump(items, file_handle, ensure_ascii=False, indent=2, default=default_json_serializer)

    print(
        f"  🧹 Canonical model bundle: {len(models)} models, "
        f"{len(workflows)} workflows, {len(apis)} provider APIs",
        flush=True,
    )


def bind_works_to_canonical_models(works):
    """Replace historical work labels with valid current product model references."""
    model_file = os.path.join(DATA_DIR, "generation_models.json")
    with open(model_file, "r", encoding="utf-8") as file_handle:
        models = json.load(file_handle)

    models_by_type = {}
    models_by_key = {}
    for model in models:
        if not model.get("is_active") or not model.get("workflow_id"):
            continue
        models_by_key[model["model_key"]] = model
        models_by_type.setdefault(model["work_type"], []).append(model)
    for candidates in models_by_type.values():
        candidates.sort(key=lambda item: (item.get("sort_order", 0), item["id"]))

    type_offsets = {}
    for work in works:
        model = models_by_key.get(work.get("model_key"))
        if model is None or model.get("work_type") != work.get("type"):
            candidates = models_by_type.get(work.get("type"), [])
            if not candidates:
                raise ValueError(f"No canonical model available for work type {work.get('type')}")
            offset = type_offsets.get(work["type"], 0)
            model = candidates[offset % len(candidates)]
            type_offsets[work["type"]] = offset + 1
        work["model_key"] = model["model_key"]
        work["model_name"] = model["name"]
    return works


def get_explore_categories():
    with open(os.path.join(DATA_DIR, "category_pages.json"), "r", encoding="utf-8") as file_handle:
        categories = json.load(file_handle)
    return [
        item["category_name"]
        for item in sorted(categories, key=lambda row: (row.get("sort_order", 0), row["id"]))
        if item.get("is_active")
        and item.get("show_in_explore")
        and item.get("level") == 1
    ]


def export_explore_showcase_works(cur):
    """Select ten premium works per Explore category, relabeling only Demo data when needed."""
    works = []
    existing_ids = set()
    relabeled_categories = []
    for category_name in get_explore_categories():
        cur.execute(
            f"""
            SELECT * FROM works
            WHERE {VALID_DEMO_WORK_SQL}
              AND (category = %s OR category LIKE %s)
              AND NOT (id = ANY(%s))
            ORDER BY {SHOWCASE_WORK_ORDER_SQL}
            LIMIT %s
            """,
            [category_name, f"{category_name}|%", list(existing_ids), EXPLORE_CATEGORY_WORK_QUOTA],
        )
        selected = [dict(row) for row in cur.fetchall()]
        existing_ids.update(work["id"] for work in selected)

        missing = EXPLORE_CATEGORY_WORK_QUOTA - len(selected)
        if missing:
            # A sparse source label must not leave an open-source Demo Gallery
            # tab empty. Change only the exported work's Demo category.
            cur.execute(
                f"""
                SELECT * FROM works
                WHERE {VALID_DEMO_WORK_SQL}
                  AND NOT (id = ANY(%s))
                ORDER BY {SHOWCASE_WORK_ORDER_SQL}
                LIMIT %s
                """,
                [list(existing_ids), missing],
            )
            fallback = [dict(row) for row in cur.fetchall()]
            if len(fallback) != missing:
                raise RuntimeError(
                    f"Not enough approved remote works to fill Explore category: {category_name}"
                )
            for work in fallback:
                work["category"] = category_name
            selected.extend(fallback)
            existing_ids.update(work["id"] for work in fallback)
            relabeled_categories.append(f"{category_name} ({missing})")

        works.extend(selected)

    expected_count = len(get_explore_categories()) * EXPLORE_CATEGORY_WORK_QUOTA
    if len(works) != expected_count:
        raise RuntimeError(f"Expected {expected_count} Explore works, received {len(works)}")
    print(
        f"  ✅ Explore showcase: {len(get_explore_categories())} categories × "
        f"{EXPLORE_CATEGORY_WORK_QUOTA} works; relabeled {relabeled_categories}",
        flush=True,
    )
    return works


def ensure_featured_video_previews(cur, works):
    """Guarantee full landscape-first carousels for text-to-video and image-to-video."""
    video_types = set(FEATURED_VIDEO_PREVIEW_QUOTAS)
    preview_candidates = []
    for work_type, quota in FEATURED_VIDEO_PREVIEW_QUOTAS.items():
        cur.execute(
            f"""
            SELECT * FROM works
            WHERE {VALID_DEMO_WORK_SQL}
              AND type::text = %s
            ORDER BY
                CASE
                    WHEN COALESCE(params->>'aspect_ratio', '') IN ('16:9', 'landscape') THEN 0
                    ELSE 1
                END,
                {SHOWCASE_WORK_ORDER_SQL}
            LIMIT %s
            """,
            [work_type, quota],
        )
        selected = [dict(row) for row in cur.fetchall()]
        if len(selected) != quota:
            raise RuntimeError(f"Not enough approved {work_type} works for the Preview carousel")
        preview_candidates.extend(selected)

    selected_ids = {work["id"] for work in works}
    candidate_ids = {work["id"] for work in preview_candidates}
    replacement_indexes = iter(
        index for index, work in enumerate(works)
        if work["id"] not in candidate_ids and work.get("type") not in video_types
    )

    for candidate in preview_candidates:
        if candidate["id"] in selected_ids:
            continue
        try:
            replacement_index = next(replacement_indexes)
        except StopIteration as error:
            raise RuntimeError("Unable to preserve Explore category quotas while adding videos") from error
        # Retain the replaced Demo work's category so every Explore tab remains
        # at exactly ten cards; only the seed record is relabeled.
        candidate["category"] = works[replacement_index].get("category")
        selected_ids.remove(works[replacement_index]["id"])
        works[replacement_index] = candidate
        selected_ids.add(candidate["id"])

    preview_ids = {work["id"] for work in preview_candidates}
    preview_works = [work for work in works if work["id"] in preview_ids]
    if len(preview_works) != len(preview_candidates):
        raise RuntimeError("The selected Preview video set is incomplete")
    for work in works:
        if work.get("type") in video_types:
            work["is_featured"] = work["id"] in preview_ids


    landscape_count = sum(
        (work.get("params") or {}).get("aspect_ratio") in LANDSCAPE_VIDEO_ASPECT_RATIOS
        for work in preview_works
    )
    counts_by_type = {
        work_type: sum(work["type"] == work_type for work in preview_works)
        for work_type in FEATURED_VIDEO_PREVIEW_QUOTAS
    }
    print(
        f"  ✅ Featured video Preview: {counts_by_type}, "
        f"{landscape_count} landscape",
        flush=True,
    )
    return works

def export_data(works_only=False):
    conn_str = os.getenv("REMOTE_DB_URL")
    if not conn_str:
        raise RuntimeError("REMOTE_DB_URL must be set explicitly")
    print(f"🚀 Connecting to remote DB...", flush=True)
    
    conn = psycopg2.connect(conn_str, connect_timeout=10)
    conn.autocommit = True
    
    config_tables = [
        "page_seos",
        "seo_configs",
        "system_configs",
        "generation_models",
        "api_library",
        "workflows",
        "category_pages",
        "generate_pages",
        "effects_pages",
        "homepage_blocks",
        "topics",
        "blog_categories",
        "blog_posts",
        "recharge_packages",
        "recharge_promos"
    ]
    
    if not works_only:
        for table in config_tables:
            export_table(conn, table)
        compact_model_bundle()

    target_count = len(get_explore_categories()) * EXPLORE_CATEGORY_WORK_QUOTA
    print(f"\n🎬 Exporting {target_count} curated Explore Gallery works...", flush=True)
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        dict_works = export_explore_showcase_works(cur)
        dict_works = ensure_featured_video_previews(cur, dict_works)
        for work in dict_works:
            # APPROVED source records are normalized to publicly visible Demo
            # works so the frontend's is_shared filter cannot hide them.
            work["is_shared"] = True
        
        user_ids = list(set([w["user_id"] for w in dict_works if w.get("user_id")]))
        
        if user_ids:
            cur.execute(f"SELECT id, email, handle, nickname, avatar_url, bio, is_admin FROM users WHERE id IN ({','.join(map(str, user_ids))});")
            dict_users = [dict(r) for r in cur.fetchall()]
        else:
            dict_users = []
            
    conn.close()

    for index, user in enumerate(sorted(dict_users, key=lambda item: item["id"]), start=1):
        user["email"] = f"demo-user-{user['id']}@example.invalid"
        user["handle"] = f"demo_user_{index:03d}"
        user["nickname"] = f"Demo Creator {index:03d}"
        user["avatar_url"] = None
        user["bio"] = "Demo creator account for the open-source initialization dataset."
        user["is_admin"] = False

    dict_users = sanitize_seed_data(dict_users)

    if dict_users:
        blog_file = os.path.join(DATA_DIR, "blog_posts.json")
        with open(blog_file, "r", encoding="utf-8") as f:
            blog_posts = json.load(f)
        demo_author_id = dict_users[0]["id"]
        for post in blog_posts:
            post["author_id"] = demo_author_id
        with open(blog_file, "w", encoding="utf-8") as f:
            json.dump(blog_posts, f, ensure_ascii=False, indent=2)

    with open(os.path.join(DATA_DIR, "sample_users.json"), "w", encoding="utf-8") as f:
        json.dump(dict_users, f, ensure_ascii=False, indent=2, default=default_json_serializer)
    print(f"  ✅ Saved {len(dict_users)} sample users", flush=True)

    dict_works = sanitize_seed_data(bind_works_to_canonical_models(dict_works))
            
    with open(os.path.join(DATA_DIR, "sample_works.json"), "w", encoding="utf-8") as f:
        json.dump(dict_works, f, ensure_ascii=False, indent=2, default=default_json_serializer)
    print(f"  ✅ Saved {len(dict_works)} sample works", flush=True)

    print("\n🎉 Export Complete!", flush=True)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Export sanitized seed data")
    parser.add_argument(
        "--works-only",
        action="store_true",
        help="Refresh only sample users and representative works",
    )
    args = parser.parse_args()
    export_data(works_only=args.works_only)
