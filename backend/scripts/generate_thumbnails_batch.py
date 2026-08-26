#!/usr/bin/env python3
"""
 works

:
    python scripts/generate_thumbnails_batch.py  #  thumbnail_url
    python scripts/generate_thumbnails_batch.py --limit 100  #
    python scripts/generate_thumbnails_batch.py --all  # works()
    python scripts/generate_thumbnails_batch.py --skip-existing
    python scripts/generate_thumbnails_batch.py --only-empty  # thumbnail_url ()
    python scripts/generate_thumbnails_batch.py --type image  #
    python scripts/generate_thumbnails_batch.py --type video  #
"""
import sys
import asyncio
import argparse
from pathlib import Path
from io import BytesIO
from datetime import datetime

# Add backend directory to path for imports
backend_dir = str(Path(__file__).parent.parent)
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app.models.base import SessionLocal
from app.models.work import Work, WorkStatus, WorkType
from app.services.storage import get_storage_service
from app.services.thumbnail import generate_image_thumbnail_webp, compress_video_h264
from app.utils.logger import logger


def print_progress(current: int, total: int, work_id: int, status: str = ""):
    percentage = (current / total * 100) if total > 0 else 0
    bar_length = 50
    filled_length = int(bar_length * current / total) if total > 0 else 0
    bar = '█' * filled_length + '░' * (bar_length - filled_length)
    
    status_text = f" | {status}" if status else ""
    print(f"\r[{bar}] {current}/{total} ({percentage:.1f}%) | Work #{work_id}{status_text}", end='', flush=True)


async def process_work(work_id: int, skip_existing: bool = False) -> tuple[bool, str]:
    """
     work，
    
    Args:
        work_id: Work ID
        skip_existing:
    
    Returns:
        (success: bool, message: str)
    """
    #
    db = SessionLocal()
    try:
        # work,
        work = db.query(Work).filter(Work.id == work_id).first()
        if not work:
            return False, "Work "
        
        # None )
        if skip_existing and work.thumbnail_url and work.thumbnail_url.strip():
            return True, "，"
        
        #  file_url
        if not work.file_url:
            return False, " file_url"
        
        #  storage_key
        if not work.storage_key:
            return False, " storage_key"
        
        storage = get_storage_service()
        is_video = work.type in [WorkType.TEXT2VIDEO.value, WorkType.IMG2VIDEO.value]
        
        # /
        if is_video:
            # 🎬 Video: H.264 + 480p, thumbnail_url
            compressed_video_data = await compress_video_h264(
                video_url=work.file_url,
                max_height=480,
                crf=23
            )
            
            if not compressed_video_data:
                return False, ""
            
            # R2(: storage_key + )
            compressed_key = f"{work.storage_key}.mp4"
            compressed_obj = BytesIO(compressed_video_data)
            storage.upload_file(
                file_obj=compressed_obj,
                key=compressed_key,
                content_type="video/mp4",
                public=False
            )
        else:
            # 🖼️ Image Thumbnail:  WebP
            thumbnail_data = await generate_image_thumbnail_webp(
                image_url=work.file_url,
                max_width=800,
                max_height=800,
                quality=85
            )
            
            # R2(: storage_key + )
            thumbnail_key = f"{work.storage_key}.webp"
            thumbnail_obj = BytesIO(thumbnail_data)
            storage.upload_file(
                file_obj=thumbnail_obj,
                key=thumbnail_key,
                content_type="image/webp",
                public=False
            )
        
        # thumbnail URL( title)
        # R2 {storage_key}.webp {storage_key}.mp4
        #  URL  canonical  {storage_key}-{title}_thumb.webp  {storage_key}-{title}_compressed.mp4
        # canonical URL key
        title = work.title or ""
        thumbnail_url = storage.generate_thumbnail_canonical_url(
            work.storage_key,
            title,
            is_video
        )
        logger.info(f"Work {work.id}: Generated canonical thumbnail URL: {thumbnail_url} (R2 key: {compressed_key if is_video else thumbnail_key})")
        
        #
        work.thumbnail_url = thumbnail_url
        db.commit()
        
        return True, ""
        
    except Exception as e:
        db.rollback()
        error_msg = str(e)
        #
        if len(error_msg) > 50:
            error_msg = error_msg[:47] + "..."
        return False, f": {error_msg}"
    finally:
        db.close()


async def process_works_batch(
    works: list[Work],
    skip_existing: bool = False,
    batch_size: int = 5
):
    """ works"""
    total = len(works)
    success_count = 0
    fail_count = 0
    skip_count = 0
    
    print(f"\n {total}  works...\n")
    
    for i in range(0, total, batch_size):
        batch = works[i:i + batch_size]
        
        tasks = [
            process_work(work.id, skip_existing)
            for work in batch
        ]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for idx, (work, result) in enumerate(zip(batch, results)):
            current = i + idx + 1
            
            if isinstance(result, Exception):
                fail_count += 1
                status = f": {str(result)[:30]}"
                print_progress(current, total, work.id, status)
            else:
                success, message = result
                if success:
                    if message == "，":
                        skip_count += 1
                    else:
                        success_count += 1
                else:
                    fail_count += 1
                
                print_progress(current, total, work.id, message)
        
        if i + batch_size < total:
            await asyncio.sleep(0.1)
    
    print("\n" + "="*70)
    print(f"✅ : {success_count}")
    print(f"⏭️  : {skip_count}")
    print(f"❌ : {fail_count}")
    print(f"📊 : {total}")
    print("="*70)


def main():
    parser = argparse.ArgumentParser(description=' works ')
    parser.add_argument('--limit', type=int, default=None, help='')
    parser.add_argument('--all', action='store_true', help=' works（）')
    parser.add_argument('--skip-existing', action='store_true', help=' works（， --only-empty）')
    parser.add_argument('--only-empty', action='store_true', help=' thumbnail_url  works（）')
    parser.add_argument('--type', choices=['image', 'video'], default=None, help='')
    parser.add_argument('--batch-size', type=int, default=5, help=' (: 5)')
    
    args = parser.parse_args()
    
    # thumbnail_url , --all
    # --skip-existing --only-empty ()
    only_empty = not args.all
    
    db = SessionLocal()
    try:
        #  works
        query = db.query(Work).filter(Work.status == WorkStatus.SUCCESS)
        
        if args.type == 'image':
            query = query.filter(
                Work.type.in_([WorkType.TEXT2IMG, WorkType.IMG2IMG])
            )
        elif args.type == 'video':
            query = query.filter(
                Work.type.in_([WorkType.TEXT2VIDEO, WorkType.IMG2VIDEO])
            )
        
        # thumbnail_url )
        if only_empty:
            #  None
            from sqlalchemy import or_
            query = query.filter(
                or_(
                    Work.thumbnail_url.is_(None),
                    Work.thumbnail_url == ""
                )
            )
        
        if args.limit:
            query = query.limit(args.limit)
        
        # ID ,
        query = query.order_by(Work.id)
        
        works = query.all()
        
        if not works:
            print("❌  works")
            return
        
        print(f"📋  {len(works)}  works ")
        if only_empty:
            print("   ( thumbnail_url  - )")
        else:
            print("   ( works，)")
        if args.type:
            print(f"   ( {args.type} )")
        if args.limit:
            print(f"   ( {args.limit} )")
        
        asyncio.run(process_works_batch(
            works,
            skip_existing=only_empty,
            batch_size=args.batch_size
        ))
        
    except KeyboardInterrupt:
        print("\n\n⚠️  ")
        db.rollback()
    except Exception as e:
        print(f"\n\n❌ : {str(e)}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    main()
