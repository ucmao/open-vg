"""
Complete Database Initialization Script (Alembic Version)
=========================================================
This script initializes the entire database structure using Alembic:
1. (Optional) Drops all existing tables
2. Runs Alembic migrations to create tables and triggers
3. Provides a clean starting point for the application

Usage:
    cd backend
    python scripts/init_database.py [--drop]
"""
import os
import sys
import argparse
import subprocess
from pathlib import Path
from dotenv import load_dotenv

# Add backend directory to path for imports
backend_dir = str(Path(__file__).parent.parent)
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app.models.base import engine, Base, SessionLocal
from app.utils.logger import logger

load_dotenv()


def drop_tables():
    """Drop all tables in the database."""
    logger.warning("🚨 DROPPING all database tables...")
    try:
        # We use SQLAlchemy to drop all tables registered in Base
        Base.metadata.drop_all(bind=engine)
        
        # Also drop the alembic_version table if it exists
        from sqlalchemy import text
        db = SessionLocal()
        try:
            db.execute(text("DROP TABLE IF EXISTS alembic_version"))
            db.commit()
        finally:
            db.close()
            
        logger.info("✅ All tables dropped successfully")
        return True
    except Exception as e:
        logger.error(f"❌ Failed to drop tables: {str(e)}")
        return False


def run_migrations():
    """Run Alembic migrations to create tables and triggers."""
    logger.info("🚀 Running Alembic migrations...")
    try:
        # Run alembic upgrade head using the venv python
        python_exe = sys.executable
        result = subprocess.run(
            [python_exe, "-m", "alembic", "upgrade", "head"],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            logger.info("✅ Migrations completed successfully")
            print(result.stdout)
            return True
        else:
            logger.error(f"❌ Migrations failed:\n{result.stderr}")
            return False
    except Exception as e:
        logger.error(f"❌ Failed to run migrations: {str(e)}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Initialize database structure using Alembic.")
    parser.add_argument("--drop", action="store_true", help="Drop existing tables before migration")
    args = parser.parse_args()

    print("=" * 60)
    print("🚀 Database Initialization Tool (Alembic)")
    print("=" * 60)
    print()
    
    # Step 0: Optional Drop tables
    if args.drop:
        confirm = input("❗ DANGER: This will delete ALL data in the database. Continue? (y/N): ")
        if confirm.lower() == 'y':
            if not drop_tables():
                print("\n❌ Failed to drop tables. Aborting.")
                return False
        else:
            print("\n⏭️  Skipping drop tables.")
    
    # Step 1: Run migrations
    if not run_migrations():
        print("\n❌ Database initialization failed during migrations")
        return False
    
    print()
    print("=" * 60)
    print("✅ Database initialization completed!")
    print("=" * 60)
    print()
    print("Next steps:")
    print("  1. Create first admin: python scripts/create_first_admin.py")
    print("  2. Add credits: python scripts/add_credits.py <email> <amount>")
    print("  3. Start server: uvicorn app.main:app --reload")
    print()
    
    return True


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Initialization cancelled by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Unexpected error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
