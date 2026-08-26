#!/usr/bin/env python3
"""
 Gemini  5  tags 。

：works
- status = success
- deleted_at
- （is_shared=True, share_status=approved）
- prompt  > 80
- tags  []

 token、：
-  API： prompt （ 8 ）
-  prompt  500  Gemini
- （ 1.5 ）， 429
- 429/503
- ，（--resume  last_id ）

:
    cd backend && python scripts/backfill_work_tags.py --dry-run
    python scripts/backfill_work_tags.py --execute
    python scripts/backfill_work_tags.py --execute --batch-size 8 --delay 1.5 --resume
    python scripts/backfill_work_tags.py --execute --limit 100
"""
import sys
import time
import json
import argparse
from pathlib import Path

# Add backend directory to path for imports
backend_dir = str(Path(__file__).parent.parent)
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from sqlalchemy import or_, func, cast
from sqlalchemy.types import Text
from app.models.base import SessionLocal
from app.models.work import Work, WorkStatus, ShareStatus
from app.services.gemini_service import get_gemini_service

# last work id
CHECKPOINT_FILE = Path(__file__).parent.parent / ".backfill_work_tags_checkpoint.json"
DEFAULT_BATCH_SIZE = 8
DEFAULT_DELAY_SEC = 1.5
MAX_RETRIES = 5
INITIAL_BACKOFF = 2.0


def load_checkpoint() -> dict:
    if not CHECKPOINT_FILE.exists():
        return {}
    try:
        with open(CHECKPOINT_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def save_checkpoint(last_id: int, processed: int, total: int):
    CHECKPOINT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(CHECKPOINT_FILE, "w", encoding="utf-8") as f:
        json.dump({"last_id": last_id, "processed": processed, "total": total}, f, indent=2)


def build_query(db, after_id: int = 0, limit: int = 0):
    """：、、、prompt>80、tags  []"""
    q = db.query(Work).filter(
        Work.status == WorkStatus.SUCCESS,
        Work.deleted_at.is_(None),
        Work.is_shared == True,
        Work.share_status == ShareStatus.APPROVED,
        Work.hidden == False,
        Work.is_banned == False,
        func.length(Work.prompt) > 80,
        or_(Work.tags.is_(None), cast(Work.tags, Text) == "[]"),
    ).order_by(Work.id.asc())
    if after_id > 0:
        q = q.filter(Work.id > after_id)
    if limit > 0:
        q = q.limit(limit)
    return q


def run(dry_run: bool, batch_size: int, delay_sec: float, limit: int, resume: bool):
    db = SessionLocal()
    try:
        after_id = 0
        if resume:
            cp = load_checkpoint()
            after_id = int(cp.get("last_id", 0))
            if after_id > 0:
                print(f"📌 ：last_id={after_id}\n")

        # limit, )
        count_query = build_query(db, after_id=after_id, limit=0)
        total = count_query.count()
        if limit > 0:
            total = min(total, limit)

        if total == 0:
            print("✅ （、、、prompt>80、tags ）")
            return

        print(f"📊 ：{total}\n")
        if dry_run:
            #
            sample = build_query(db, after_id=after_id, limit=min(5, total)).all()
            for w in sample:
                print(f"  ID={w.id}  prompt_len={len(w.prompt or '')}  tags={w.tags!r}")
            print("\n⚠️  dry-run ， API 。 --execute 。")
            return

        gemini = get_gemini_service(db_session=db)
        processed = 0
        err_count = 0
        last_id = after_id

        while True:
            batch = build_query(db, after_id=last_id, limit=batch_size).all()
            if not batch:
                break

            prompts = [w.prompt or "" for w in batch]
            for _ in range(MAX_RETRIES):
                try:
                    tag_lists = gemini.generate_tags_batch(
                        prompts,
                        max_per_request=len(prompts),
                        max_prompt_chars=500,
                    )
                    break
                except Exception as e:
                    err_str = str(e).lower()
                    if "429" in err_str or "quota" in err_str or "rate limit" in err_str or "503" in err_str or "overloaded" in err_str or "unavailable" in err_str:
                        #
                        backoff = INITIAL_BACKOFF * (2 ** _)
                        backoff = min(backoff, 60)
                        print(f"⏳ /，{backoff:.0f}s  ({_ + 1}/{MAX_RETRIES}) ...")
                        time.sleep(backoff)
                    else:
                        print(f"❌  API : {e}")
                        err_count += len(batch)
                        tag_lists = [[] for _ in batch]
                        break
            else:
                print(f"❌  {MAX_RETRIES} ")
                err_count += len(batch)
                tag_lists = [[] for _ in batch]

            # batch
            for w, tags in zip(batch, tag_lists):
                w.tags = tags if isinstance(tags, list) else []
                last_id = w.id
                processed += 1

            db.commit()
            save_checkpoint(last_id, processed, total)
            print(f"✅  {processed}/{total}  ( {len(batch)} , last_id={last_id})")

            if delay_sec > 0:
                time.sleep(delay_sec)

            if limit > 0 and processed >= limit:
                break

        print(f"\n📈 ： {processed - err_count}， {err_count}， {processed}")
    except Exception as e:
        db.rollback()
        print(f"❌ : {e}")
        raise
    finally:
        db.close()


def main():
    parser = argparse.ArgumentParser(description=" tags ")
    parser.add_argument("--dry-run", action="store_true", help="， API ")
    parser.add_argument("--execute", action="store_true", help="（ dry-run）")
    parser.add_argument("--batch-size", type=int, default=DEFAULT_BATCH_SIZE, help=f"（ {DEFAULT_BATCH_SIZE}）")
    parser.add_argument("--delay", type=float, default=DEFAULT_DELAY_SEC, help=f"（ {DEFAULT_DELAY_SEC}）")
    parser.add_argument("--limit", type=int, default=0, help="，0 ")
    parser.add_argument("--resume", action="store_true", help="（ .backfill_work_tags_checkpoint.json）")
    args = parser.parse_args()

    dry_run = not args.execute
    if not dry_run:
        confirm = input(" Gemini ？(yes/no): ").strip().lower()
        if confirm != "yes":
            print("")
            sys.exit(0)

    run(
        dry_run=dry_run,
        batch_size=args.batch_size,
        delay_sec=args.delay,
        limit=args.limit,
        resume=args.resume,
    )


if __name__ == "__main__":
    main()
