"""
Seed Data Export Script (Psycopg2 Direct + Autocommit)
======================================================
This script connects directly via psycopg2 to the remote production PostgreSQL database, extracts:
1. All 100% full system configurations.
2. 100 representative image/video works plus anonymized demo authors.
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

DEMO_WORK_QUOTAS = {
    "text-to-image": 50,
    "text-to-video": 25,
    "image-to-video": 15,
    "image-to-image": 5,
    "image-effects": 3,
    "video-effects": 2,
}

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

    # Select a balanced image/video showcase instead of letting the much larger
    # text-to-image pool crowd every other generation type out of the demo.
    target_count = sum(DEMO_WORK_QUOTAS.values())
    print(f"\n🎬 Exporting {target_count} representative sample works...", flush=True)
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        cur.execute("""
            WITH ranked AS (
                SELECT
                    works.*,
                    ROW_NUMBER() OVER (
                        PARTITION BY type
                        ORDER BY
                            is_featured DESC NULLS LAST,
                            like_count DESC NULLS LAST,
                            view_count DESC NULLS LAST,
                            id DESC
                    ) AS demo_rank
                FROM works
                WHERE share_status = 'APPROVED'
                  AND status = 'SUCCESS'
                  AND COALESCE(is_banned, false) = false
                  AND COALESCE(hidden, false) = false
                  AND deleted_at IS NULL
                  AND file_url IS NOT NULL
                  AND file_url <> ''
                  AND thumbnail_url IS NOT NULL
                  AND thumbnail_url <> ''
            )
            SELECT * FROM ranked
            WHERE demo_rank <= CASE type::text
                WHEN 'text-to-image' THEN 50
                WHEN 'text-to-video' THEN 25
                WHEN 'image-to-video' THEN 15
                WHEN 'image-to-image' THEN 5
                WHEN 'image-effects' THEN 3
                WHEN 'video-effects' THEN 2
                ELSE 0
            END
            ORDER BY type::text, demo_rank;
        """)
        dict_works = [dict(r) for r in cur.fetchall()]
        for work in dict_works:
            work.pop("demo_rank", None)
        
        user_ids = list(set([w["user_id"] for w in dict_works if w.get("user_id")]))
        
        if user_ids:
            cur.execute(f"SELECT id, email, handle, nickname, avatar_url, bio, is_admin FROM users WHERE id IN ({','.join(map(str, user_ids))});")
            dict_users = [dict(r) for r in cur.fetchall()]
        else:
            dict_users = []
            
    conn.close()

    for index, user in enumerate(sorted(dict_users, key=lambda item: item["id"]), start=1):
        user["email"] = f"demo-user-{user['id']}@example.invalid"
        user["handle"] = f"demo_creator_{index:03d}"
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

    dict_works = sanitize_seed_data(dict_works)
            
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
