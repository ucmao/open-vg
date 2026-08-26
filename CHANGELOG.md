# Changelog

All notable changes to the **VidGen** project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.1.0] - 2026-08-25

### Added
- **Admin i18n & Language Switching**: Complete Chinese/English bilingual support for the super admin panel (`useAdminI18n`, locale dictionaries).
- **Unit Testing & CI Integration**: Frontend/backend unit test coverage integrated directly into GitHub Actions CI workflows.

### Changed
- **Type Safety & Code Quality**: Refactored component types across `web` and `admin` applications, resolving all Vue type-check issues and achieving zero ESLint warnings.
- **Documentation & Deployment**: Updated quickstart guide, environment variable docs, and deployment requirements across multi-language READMEs.

### Security & Maintenance
- **Markdown Sanitization**: Added strict sanitizer for user-generated Markdown link targets to prevent XSS.
- **Dependency Pinning**: Upgraded core dependencies, synchronized lockfiles, and tightened Python backend package bounds.

## [1.0.0] - 2026-08-22

### Added
- **Initial Public Release**: Open-source release of the complete VidGen AI platform.
- **Frontend Applications**:
  - `web`: User-facing AI Video & Image Generation Web App built with Nuxt 3, Tailwind CSS, and Pinia.
  - `admin`: Full-featured Super Admin Panel for user management, credit packages, prompt settings, and AI model workflows.
- **Backend API Engine**: FastAPI backend with SQLAlchemy, Celery async task queue, Redis caching, and Alembic database migrations.
- **AI Integrations**: Support for Replicate, Gemini, and custom AI Generation Workflows.
- **Mock Mode**: Open-source contributor Mock AI Generation mode (`MOCK_AI_GENERATION=true`) for cost-free local testing.
- **Security & CI**: Fail-fast environment security guards, Docker Compose localhost isolation, and GitHub Actions CI Quality Gate workflows.
