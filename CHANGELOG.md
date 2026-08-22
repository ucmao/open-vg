# Changelog

All notable changes to the **VidGen** project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.0.0] - 2026-08-22

### Added
- **Initial Public Release**: Open-source release of the complete VidGen AI platform.
- **Frontend Applications**:
  - `web`: User-facing AI Video & Image Generation Web App built with Nuxt 3, Tailwind CSS, and Pinia.
  - `admin`: Full-featured Super Admin Panel for user management, credit packages, prompt settings, and AI model workflows.
- **Backend API Engine**: FastAPI backend with SQLAlchemy, Celery async task queue, Redis caching, and Alembic database migrations.
- **AI Integrations**: Support for Replicate, SiliconFlow, Gemini, and custom AI Generation Workflows.
- **Mock Mode**: Open-source contributor Mock AI Generation mode (`MOCK_AI_GENERATION=true`) for cost-free local testing.
- **Security & CI**: Fail-fast environment security guards, Docker Compose localhost isolation, and GitHub Actions CI Quality Gate workflows.
