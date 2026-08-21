import sys
import os
from sqlalchemy.orm import Session

# Add the project root to sys.path to allow importing from 'app'
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.models.base import SessionLocal
from app.models.recharge_package import RechargePackage

def init_recharge_packages():
    db = SessionLocal()
    try:
        # Check if packages already exist
        if db.query(RechargePackage).count() > 0:
            print("Recharge packages already exist. Skipping initialization.")
            return

        default_packages = [
            {"name": "Starter", "amount": 10.0, "credits": 100, "is_active": True, "is_featured": False, "tag_text": None, "order": 1},
            {"name": "Basic", "amount": 20.0, "credits": 200, "is_active": True, "is_featured": False, "tag_text": None, "order": 2},
            {"name": "Popular", "amount": 50.0, "credits": 500, "is_active": True, "is_featured": True, "tag_text": "Most Popular", "order": 3},
            {"name": "Pro", "amount": 100.0, "credits": 1000, "is_active": True, "is_featured": False, "tag_text": "Best Value", "order": 4},
        ]

        for pkg_data in default_packages:
            pkg = RechargePackage(**pkg_data)
            db.add(pkg)
        
        db.commit()
        print(f"Successfully initialized {len(default_packages)} recharge packages.")
    except Exception as e:
        db.rollback()
        print(f"Error initializing recharge packages: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    init_recharge_packages()
