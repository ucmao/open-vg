"""
Unified Master Database Seed & Initialization Script
======================================================
This script initializes the database tables and populates all initial required data:
1. Runs Alembic database migrations (`alembic upgrade head`)
2. Creates the initial Super Admin account (default: admin / admin123)
3. Imports full system configurations, page SEOs (Explore, Magic, Create, Blog, Topics enabled), models, workflows, categories, recharge packages, blogs, and 105 anonymized image/video demo works covering every Explore category, using public CDN media URLs with bundled frontend fallbacks.

Usage:
    python scripts/seed_all.py
"""
import os
import sys
import subprocess
from pathlib import Path

backend_dir = Path(__file__).resolve().parents[1]
backend_path = str(backend_dir)
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

existing_pythonpath = os.environ.get("PYTHONPATH")
os.environ["PYTHONPATH"] = (
    f"{backend_path}{os.pathsep}{existing_pythonpath}"
    if existing_pythonpath
    else backend_path
)

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from app.utils.logger import logger


def run_command(cmd_list, description):
    """Run a sub-script command with real-time streaming output."""
    logger.info(f"👉 Step: {description}...")
    try:
        python_exe = sys.executable
        full_cmd = [python_exe] + cmd_list
        proc = subprocess.Popen(
            full_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            cwd=backend_dir,
            bufsize=1
        )
        if proc.stdout:
            for line in proc.stdout:
                line_str = line.strip()
                if line_str:
                    print(f"   {line_str}", flush=True)
        proc.wait()
        if proc.returncode == 0:
            logger.info(f"✅ {description} completed.")
            return True
        else:
            logger.error(f"❌ {description} failed (exit code {proc.returncode}).")
            return False
    except Exception as e:
        logger.error(f"❌ Execution error during {description}: {str(e)}")
        return False


def main():
    print("=" * 65, flush=True)
    print("🚀 VidGen Master Seed & Database Initialization", flush=True)
    print("=" * 65, flush=True)
    print(flush=True)

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
            logger.error(f"❌ Alembic migration failed:\n{result.stderr.strip()}")
            return False
    except Exception as e:
        logger.error(f"❌ Migration exception: {str(e)}")
        return False

    print(flush=True)

    # Step 2: Create Super Admin
    if not run_command(["scripts/create_first_admin.py"], "Creating Initial Super Admin"):
        return False

    print(flush=True)

    # Step 3: Import Complete Seed Dataset (Configs, Pages, Models, Workflows, Sample Works & Assets)
    if not run_command(["scripts/import_seed_dataset.py"], "Importing Full Configurations, Pages & Demo Dataset"):
        return False

    print(flush=True)
    print("=" * 68, flush=True)
    print("🎉 VIDGEN MASTER SEED & CONTAINER INITIALIZATION COMPLETED!", flush=True)
    print("=" * 68, flush=True)
    print("  🌐 Web Frontend: http://localhost:3000 (All pages & demo data enabled)", flush=True)
    print("  🔑 Admin Login:  http://localhost:3001 (User: admin / Pass: admin123)", flush=True)
    print("  🐍 Backend API:   http://localhost:8000/docs", flush=True)
    print("=" * 68, flush=True)
    print("  ⚠️  EXTERNAL SERVICES CONFIGURATION CHECKLIST (.env):", flush=True)
    print("     • AI Generation:    Configure REPLICATE_API_KEY", flush=True)
    print("                         (Or set MOCK_AI_GENERATION=true for zero-cost testing)", flush=True)
    print("     • Payments:         Configure PAYPAL_CLIENT_ID / PAYPAL_CLIENT_SECRET", flush=True)
    print("     • OAuth Login:      Configure GOOGLE_CLIENT_ID / GOOGLE_CLIENT_SECRET", flush=True)
    print("     • Email (SMTP):     Configure SMTP_HOST / SMTP_PORT for email verification", flush=True)
    print("=" * 68, flush=True)
    print(flush=True)
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
