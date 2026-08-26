"""
Security Warning Checker for VidGen Startup.
=================================================
Checks for unsafe production configurations:
1. Insecure default JWT_SECRET
2. Insecure default INITIAL_ADMIN_PASSWORD in production
3. Mock AI Generation Mode notice
"""
import os
from .logger import logger

INSECURE_JWT_SECRETS = {
    "your-secret-key-change-in-production",
    "secret",
    "change_me",
    "changeme",
    "jwt_secret",
    "admin123",
    "123456",
    "12345678"
}


def check_security_warnings():
    """Check configuration and print ASCII Security Warnings if insecure values are detected."""
    env_mode = os.getenv("ENVIRONMENT", "development").strip().lower()
    jwt_secret = os.getenv("JWT_SECRET", "your-secret-key-change-in-production").strip()
    admin_pass = os.getenv("INITIAL_ADMIN_PASSWORD", "").strip()
    crypto_key = os.getenv("CONFIG_ENCRYPTION_KEY", "").strip()
    mock_mode = os.getenv("MOCK_AI_GENERATION", "false").strip().lower() in ("true", "1", "yes", "y", "on")

    warnings = []

    # 1. Check JWT Secret
    if jwt_secret in INSECURE_JWT_SECRETS or len(jwt_secret) < 16:
        warnings.append(
            "CRITICAL: Insecure or default JWT_SECRET detected!\n"
            "   Please set a strong random secret in your .env file:\n"
            "   JWT_SECRET=" + (os.urandom(24).hex() if hasattr(os, 'urandom') else 'generate_random_key_here')
        )

    # 2. Check Encryption Key
    if not crypto_key or crypto_key == "aigc-platform-default-secret-key-change-it-in-prod":
        warnings.append(
            "CRITICAL: Insecure or default CONFIG_ENCRYPTION_KEY detected!\n"
            "   Please set a strong secret key for vendor API Key encryption."
        )

    # 3. Check Admin Password in Production
    if env_mode == "production" and (
        len(admin_pass) < 12 or admin_pass.lower() in {"admin123", "password", "changeme"}
    ):
        warnings.append(
            "CRITICAL: INITIAL_ADMIN_PASSWORD is missing, weak, or uses a known default in PRODUCTION!\n"
            "   Set a strong password of at least 12 characters."
        )

    # Print ASCII Warning Banner if warnings found
    if warnings:
        border = "=" * 70
        print()
        print("🚨" + border[2:])
        print("🚨  SECURITY WARNING — ACTION REQUIRED FOR PRODUCTION DEPLOYMENT")
        print("🚨" + border[2:])
        for w in warnings:
            for line in w.split("\n"):
                print(f"⚠️   {line}")
        print("🚨" + border[2:])
        print()

        if env_mode == "production":
            raise RuntimeError("CRITICAL SECURITY CHECK FAILED: Unsafe default credentials or missing secrets in production mode.")

    # Informational notice for Mock Mode
    if mock_mode:
        print()
        print("🧪 [MOCK AI GENERATION MODE ACTIVE]")
        print("   AI Generations will be simulated locally with zero API cost.")
        print()
