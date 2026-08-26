# Changelog

All notable changes to the **VidGen** project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.2.0] - 2026-08-26

### Security & Hardening
- **API Rate Limiting**: Added granular rate limiting guards for auth routes (`login`, `register`, `verify`), file uploads, and AI generation endpoints.
- **WebSocket Security**: Hardened WebSocket subprotocol authentication, token validation, and maximum connection limits per user.
- **Production Baseline Guards**: Enforced fail-fast production credential validation (`POSTGRES_PASSWORD`, `JWT_SECRET`) and localhost port isolation in `docker-compose.prod.yml`.

### Added & Enhanced
- **Redis Event Broadcasting**: Integrated Redis Pub/Sub channel (`REALTIME_REDIS_CHANNEL`) for cross-process worker event relay.
- **Safe Seed Profiles**: Introduced `safe` and `core` seed profiles with non-destructive migration checks to prevent accidental production demo data pollution.
- **Admin Dynamic Timezone Analytics**: Added user/admin dynamic timezone support and unified datetime formatting across admin dashboard charts.

### Changed & Refined
- **Provider Cleanup**: Removed legacy SiliconFlow AI provider adapter; streamlined Replicate & Gemini provider pipelines.
- **Documentation & README Refactoring**: Updated docs category tree links and simplified quickstart seeding guide across bilingual READMEs.

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
