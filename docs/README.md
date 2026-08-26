# VidGen Documentation Index & Sitemap

Welcome to the official technical documentation for **VidGen**, a full-stack open-source AI video and image generation platform.

This documentation suite is organized into 6 modular categories to help developers, system administrators, and open-source contributors understand, develop, deploy, and extend the VidGen platform.

---

## 📚 Documentation Categories

### 🚀 [1. Getting Started](./01-getting-started/)
- [5-Minute Quickstart](./01-getting-started/quickstart.md): Get VidGen running locally or via Docker.
- [Exhaustive Environment Variables Reference](./01-getting-started/environment-variables.md): Complete configuration dictionary for Backend, Web, and Admin.
- [Local Development Guide](./01-getting-started/local-development.md): Detailed local development workflow, tools, and coding conventions.

### 🏛️ [2. Architecture & Design](./02-architecture/)
- [System Architecture Overview](./02-architecture/system-overview.md): High-level topology, Monorepo layout, and security model.
- [Node-Based Workflow Engine](./02-architecture/workflow-engine.md): DAG execution engine and VueFlow node protocol.
- [Asynchronous Queues & WebSockets](./02-architecture/async-tasks-and-sockets.md): Celery workers, authenticated WebSocket acceleration, and polling fallback.
- [Credit Economics & Monetization](./02-architecture/credit-economics.md): Pay-as-you-go credits, transactional DB row locking, and auto-refunds.

### 🔧 [3. Subsystems & Data Models](./03-subsystems/)
- [Backend FastAPI Core](./03-subsystems/backend-fastapi.md): REST API design, Pydantic v2 schemas, and JWT security scopes.
- [User Web Portal Architecture](./03-subsystems/frontend-web.md): Nuxt 3 Web application, SSR/ISR strategy, and SEO aggregation routes.
- [Admin Management Panel](./03-subsystems/admin-panel.md): Nuxt 3 Admin SPA, VueFlow node builder, Sockpuppets, and moderation tools.
- [Database Schema & Migrations](./03-subsystems/database-schema.md): Entity-Relationship models, table specifications, and Alembic migrations.

### 🔌 [4. Integrations & Extensions](./04-integrations/)
- [AI Provider Extension Guide](./04-integrations/provider-extension-guide.md): Step-by-step tutorial on adding custom AI provider adapters.
- [Payment Gateways Integration](./04-integrations/payment-gateways.md): PayPal REST API v2 & Stripe Webhook integration guide.
- [Object Storage Setup](./04-integrations/object-storage.md): Cloudflare R2, AWS S3, and Aliyun OSS configuration.

### 🚢 [5. Operations & Deployment](./05-deployment/)
- [Docker & Docker Compose Deployment Guide](./05-deployment/docker-deployment.md): One-click containerized deployment guide.
- [Production Deployment Guide](./05-deployment/production-deployment.md): VPS & Bare-metal deployment with Nginx and SSL.
- [Systemd Services Suite](./05-deployment/systemd-services.md): Systemd process daemons & management script reference.
- [SSR Troubleshooting Guide](./05-deployment/ssr-troubleshooting.md): Nuxt 3 SSR hydration fixes & `NUXT_INTERNAL_API_URL` troubleshooting.

### 🤝 [6. Open-Source Governance](./06-governance/)
- [Contribution Guidelines](./06-governance/CONTRIBUTING.md): PR standards, code styling, and development workflow.
- [Code of Conduct](./06-governance/CODE_OF_CONDUCT.md): Community standards and behavior policy.
- [Security Policy](./06-governance/SECURITY.md): Vulnerability disclosure policy and security contacts.
