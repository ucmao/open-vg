import os
import sys
from pathlib import Path
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from app.models.base import SessionLocal
from app.models.admin import Admin
from app.utils.auth import hash_password

def main():
    username = os.getenv("INITIAL_ADMIN_USERNAME", "admin")
    email = os.getenv("INITIAL_ADMIN_EMAIL", "admin@example.com")
    password = os.getenv("INITIAL_ADMIN_PASSWORD", "admin123")

    db = SessionLocal()
    try:
        # Check if admin already exists
        existing_admin = db.query(Admin).filter((Admin.username == username) | (Admin.email == email)).first()
        if existing_admin:
            print(f"⚠️  Admin user '{existing_admin.username}' ({existing_admin.email}) already exists (ID: {existing_admin.id})")
            return

        admin = Admin(
            username=username,
            email=email,
            nickname="Super Admin",
            password_hash=hash_password(password),
            role="super_admin",
            is_active=True,
        )
        db.add(admin)
        db.commit()
        db.refresh(admin)
        print("✅ Initial Super Admin Created:")
        print(f"   Username: {username}")
        print(f"   Email:    {email}")
        print("   Password: [SET FROM INITIAL_ADMIN_PASSWORD VAR]")
    except Exception as e:
        db.rollback()
        print(f"❌ Error creating initial admin: {str(e)}")
    finally:
        db.close()

if __name__ == "__main__":
    main()
