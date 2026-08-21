#!/usr/bin/env python3
"""
 credit_records  description 「Generation: {type} with {model_key}」 model_key（slug）
 generation_models  name（）。

 "Generation: ... with ..."  generation_models  model_key ；
 model_key 。

:
    cd backend && python scripts/fix_credit_record_descriptions.py --dry-run
    python scripts/fix_credit_record_descriptions.py --execute
"""
import sys
import re
import argparse
from pathlib import Path

backend_dir = str(Path(__file__).parent.parent)
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app.models.base import SessionLocal
from app.models.credit_record import CreditRecord
from app.models.generation_model import GenerationModel

#  "Generation: <type> with <model_key>"
DESC_PATTERN = re.compile(r"^Generation: (.+) with (.+)$", re.IGNORECASE)


def get_model_key_to_name(db):
    """ model_key -> name 。"""
    models = db.query(GenerationModel).filter(GenerationModel.model_key.isnot(None)).all()
    return {m.model_key: m.name for m in models}


def fix_credit_record_descriptions(execute: bool = False):
    db = SessionLocal()
    try:
        key_to_name = get_model_key_to_name(db)
        if not key_to_name:
            print("No generation models found in DB. Exiting.")
            return

        #  description  "Generation: ... with ..."
        records = (
            db.query(CreditRecord)
            .filter(CreditRecord.description.isnot(None))
            .filter(CreditRecord.description.like("Generation:%with%"))
            .all()
        )

        updated = 0
        skipped_no_match = 0
        skipped_unknown_key = 0

        for record in records:
            m = DESC_PATTERN.match(record.description.strip())
            if not m:
                skipped_no_match += 1
                continue
            gen_type, model_key = m.group(1).strip(), m.group(2).strip()
            model_name = key_to_name.get(model_key)
            if not model_name:
                skipped_unknown_key += 1
                if execute:
                    print(f"  [skip] id={record.id} unknown model_key: {model_key!r}")
                continue
            new_desc = f"Generation: {gen_type} with {model_name}"
            if record.description == new_desc:
                continue
            updated += 1
            if execute:
                old_short = (record.description[:60] + "…") if len(record.description) > 60 else record.description
                new_short = (new_desc[:60] + "…") if len(new_desc) > 60 else new_desc
                print(f"  id={record.id}: {old_short} -> {new_short}")
                record.description = new_desc
                db.add(record)

        if execute and updated > 0:
            db.commit()
            print(f"Committed {updated} updates.")
        elif execute:
            print("No records to update.")
        else:
            print(f"[dry-run] Would update {updated} record(s).")
            if skipped_unknown_key:
                print(f"  Skipped (unknown model_key): {skipped_unknown_key}")
            if skipped_no_match:
                print(f"  Skipped (description format): {skipped_no_match}")

    except Exception as e:
        db.rollback()
        print(f"Error: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fix credit_record description: replace model slug with model name.")
    parser.add_argument("--dry-run", action="store_true", help="Only print what would be changed.")
    parser.add_argument("--execute", action="store_true", help="Apply changes to the database.")
    args = parser.parse_args()

    if not args.execute and not args.dry_run:
        parser.print_help()
        print("\nUse --dry-run or --execute.")
        sys.exit(1)

    fix_credit_record_descriptions(execute=args.execute)
