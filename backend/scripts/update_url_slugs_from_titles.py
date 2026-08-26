"""： url_slug， title  slug"""
import sys
from pathlib import Path

# Add backend directory to path for imports
backend_dir = str(Path(__file__).parent.parent)
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app.models.base import SessionLocal
from app.models.work import Work, WorkStatus, ShareStatus
from app.utils.url_slug import generate_url_slug
from sqlalchemy import or_

def update_url_slugs_from_titles(dry_run=True, batch_size=100):
    """
     url_slug。
    
    Args:
        dry_run:  True，，
        batch_size:
    """
    db = SessionLocal()
    
    try:
        #
        # status='success', share_status='approved', is_banned=False, deleted_at IS NULL, title short_code
        query = db.query(Work).filter(
            Work.status == WorkStatus.SUCCESS,
            Work.share_status == ShareStatus.APPROVED,
            Work.is_banned == False,
            Work.deleted_at.is_(None),
            Work.title.isnot(None),
            Work.short_code.isnot(None)
        )
        
        total_count = query.count()
        print(f"📊  {total_count} \n")
        
        if total_count == 0:
            print("✅ ")
            return
        
        #
        updated_count = 0
        skipped_count = 0
        error_count = 0
        
        for offset in range(0, total_count, batch_size):
            works = query.offset(offset).limit(batch_size).all()
            
            for work in works:
                try:
                    #  url_slug
                    new_url_slug = generate_url_slug(work.short_code, work.title)
                    
                    # slug ,
                    if not new_url_slug:
                        print(f"⏭️  [ID: {work.id}] ： url_slug (short_code: {work.short_code}, title: {work.title})")
                        skipped_count += 1
                        continue
                    
                    if new_url_slug == work.url_slug:
                        print(f"⏭️  [ID: {work.id}] ：url_slug ")
                        skipped_count += 1
                        continue
                    
                    #  slug
                    existing_work = db.query(Work).filter(
                        Work.url_slug == new_url_slug,
                        Work.id != work.id
                    ).first()
                    
                    if existing_work:
                        print(f"⚠️  [ID: {work.id}] ：url_slug '{new_url_slug}'  ID {existing_work.id} ")
                        skipped_count += 1
                        continue
                    
                    #
                    old_slug = work.url_slug or "()"
                    print(f"🔄 [ID: {work.id}]  url_slug:")
                    print(f"   : {old_slug}")
                    print(f"   : {new_url_slug}")
                    print(f"   Title: {work.title}")
                    
                    if not dry_run:
                        #
                        work.url_slug = new_url_slug
                        db.flush()
                        updated_count += 1
                    else:
                        updated_count += 1
                        print(f"   (，)")
                    
                    print()
                    
                except Exception as e:
                    error_count += 1
                    print(f"❌ [ID: {work.id}] : {str(e)}")
                    print()
            
            if not dry_run and updated_count > 0:
                try:
                    db.commit()
                    print(f"✅  {updated_count} \n")
                except Exception as e:
                    db.rollback()
                    print(f"❌ : {str(e)}")
                    raise
        
        #
        print("=" * 60)
        print("📈 :")
        print(f"   : {total_count} ")
        print(f"   : {updated_count} ")
        print(f"   : {skipped_count} ")
        print(f"   : {error_count} ")
        print("=" * 60)
        
        if dry_run:
            print("\n⚠️  ，")
            print("   ， --execute ")
        else:
            print("\n✅ ！")
            
    except Exception as e:
        print(f"❌ : {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description=" url_slug")
    parser.add_argument(
        "--execute",
        action="store_true",
        help="（）"
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=100,
        help="（: 100）"
    )
    
    args = parser.parse_args()
    
    dry_run = not args.execute
    
    if dry_run:
        print("🔍 （）")
        print("    --execute \n")
    else:
        #
        print("⚠️  ：！")
        confirm = input("？(yes/no): ").strip().lower()
        if confirm != "yes":
            print("❌ ")
            sys.exit(0)
        print()
    
    update_url_slugs_from_titles(dry_run=dry_run, batch_size=args.batch_size)
