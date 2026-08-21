"""
Unified Master Database Seed & Initialization Script
======================================================
This script initializes the database tables and populates all initial required data:
1. Runs Alembic database migrations (`alembic upgrade head`)
2. Creates the initial Super Admin account (default: admin / admin123)
3. Imports AI Generation Models & API Library definitions
4. Initializes Recharge Packages (Starter, Basic, Popular, Pro)
5. Initializes SEO System Configurations

Usage:
    python scripts/seed_all.py
"""
import os
import sys
import subprocess
from pathlib import Path
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from app.utils.logger import logger


def run_command(cmd_list, description):
    """Run a sub-script command safely."""
    logger.info(f"👉 Step: {description}...")
    try:
        python_exe = sys.executable
        full_cmd = [python_exe] + cmd_list
        result = subprocess.run(full_cmd, capture_output=True, text=True, cwd=backend_dir)
        if result.returncode == 0:
            logger.info(f"✅ {description} completed.")
            if result.stdout.strip():
                for line in result.stdout.strip().split('\n'):
                    print(f"   {line}")
            return True
        else:
            logger.error(f"❌ {description} failed:\n{result.stderr}")
            return False
    except Exception as e:
        logger.error(f"❌ Execution error during {description}: {str(e)}")
        return False


def main():
    print("=" * 60)
    print("🚀 VidGen Master Seed & Database Initialization")
    print("=" * 60)
    print()

    # Step 1: Migrations
    logger.info("👉 Step 1: Running Alembic Migrations...")
    try:
        result = subprocess.run(
            [sys.executable, "-m", "alembic", "upgrade", "head"],
            capture_output=True,
            text=True,
            cwd=backend_dir
        )
        if result.returncode == 0:
            logger.info("✅ Database schema migrated to latest (head).")
        else:
            logger.error(f"❌ Alembic migration failed:\n{result.stderr}")
            return False
    except Exception as e:
        logger.error(f"❌ Migration exception: {str(e)}")
        return False

    print()

    # Step 2: Create Super Admin
    if not run_command(["scripts/create_first_admin.py"], "Creating Initial Super Admin"):
        return False

    print()

    # Step 3: Import AI Models
    if not run_command(["scripts/import_models.py"], "Importing AI Models & API Libraries"):
        return False

    print()

    # Step 4: Recharge Packages
    if not run_command(["scripts/init_recharge_packages.py"], "Initializing Credit Recharge Packages"):
        return False

    print()

    # Step 5: SEO Configs
    if not run_command(["scripts/init_seo_config.py"], "Initializing System SEO Configurations"):
        return False

    print()
    print("=" * 60)
    print("🎉 ALL SEED & INITIALIZATION STEPS COMPLETED SUCCESSFULLY!")
    print("=" * 60)
    print("  🔑 Admin Login: http://localhost:3001")
    print("     Username: " + os.getenv("INITIAL_ADMIN_USERNAME", "admin"))
    print("     Password: [Configured via INITIAL_ADMIN_PASSWORD env variable]")
    print("=" * 60)
    print()
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
