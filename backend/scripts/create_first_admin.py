import os
import secrets
import sys
from pathlib import Path
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from app.models.base import SessionLocal
from app.models.admin import Admin
from app.utils.auth import hash_password, verify_password


INSECURE_ADMIN_PASSWORDS = ("admin123", "password", "changeme")


def _uses_insecure_password(password_hash: str) -> bool:
    try:
        return any(
            verify_password(candidate, password_hash)
            for candidate in INSECURE_ADMIN_PASSWORDS
        )
    except (TypeError, ValueError):
        # A malformed stored hash is not a usable production credential.
        return True

def main():
    username = os.getenv("INITIAL_ADMIN_USERNAME", "admin")
    email = os.getenv("INITIAL_ADMIN_EMAIL", "admin@example.com")
    password = os.getenv("INITIAL_ADMIN_PASSWORD", "").strip()
    environment = os.getenv("ENVIRONMENT", "development").strip().lower()
    generated_password = False

    if not password:
        if environment == "production":
            raise RuntimeError("INITIAL_ADMIN_PASSWORD is required in production")
        password = secrets.token_urlsafe(18)
        generated_password = True

    if environment == "production" and (
        len(password) < 12 or password.lower() in INSECURE_ADMIN_PASSWORDS
    ):
        raise RuntimeError(
            "INITIAL_ADMIN_PASSWORD must be at least 12 characters and must not use a known default"
        )

    db = SessionLocal()
    try:
        if environment == "production":
            insecure_admins = [
                admin.username
                for admin in db.query(Admin).filter(Admin.is_active == True).all()
                if _uses_insecure_password(admin.password_hash)
            ]
            if insecure_admins:
                raise RuntimeError(
                    "Existing active admin accounts use a known default or invalid password: "
                    f"{', '.join(insecure_admins)}. Change them before starting production."
                )

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
        if generated_password:
            print(f"   Password: {password}")
            print("   Save this generated local-development password now; it will not be shown again.")
        else:
            print("   Password: [SET FROM INITIAL_ADMIN_PASSWORD VAR]")
    except Exception as e:
        db.rollback()
        print(f"❌ Error creating initial admin: {str(e)}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    main()
