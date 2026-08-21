# System Architecture Overview

This document provides a comprehensive architectural overview of **VidGen**, covering component topology, Monorepo layout, security boundaries, and data flow pipelines.

---

## 🏛️ System Topology Diagram

```
                                  +---------------------------------------+
                                  |    Cloudflare / Nginx Reverse Proxy   |
                                  |      (Port 80 / 443 SSL Proxy)        |
                                  +-------------------+-------------------+
                                                      |
                          +---------------------------+---------------------------+
                          |                                                       |
                          v                                                       v
         +---------------------------------+                     +---------------------------------+
         |     User Web Portal (Nuxt 3)    |                     |    Admin Panel SPA (Nuxt 3)    |
         |  SSR / ISR / CSR (Port 3000)    |                     |    Port 3001 (Vue i18n EN/ZH)   |
         +----------------+----------------+                     +----------------+----------------+
                          |                                                       |
                          +---------------------------+---------------------------+
                                                      | HTTP / REST API
                                                      v
                                   +------------------------------------+
                                   |    FastAPI Core API Service        |
                                   |  Async ORM / JWT Auth / Port 8000  |
                                   +------------------+-----------------+
                                                      |
                  +-----------------------------------+-----------------------------------+
                  |                                   |                                   |
                  v                                   v                                   v
       +--------------------+               +--------------------+               +--------------------+
       | PostgreSQL 14+ DB  |               | Redis 6+ Broker    |               |  Object Storage    |
       | Relational Storage |               | Pub/Sub & Caching  |               | Cloudflare R2 / S3 |
       +--------------------+               +---------+----------+               +--------------------+
                                                      |
                                                      v
                                           +--------------------+
                                           | Celery Task Worker |
                                           | Workflow Engine    |
                                           +----------+---------+
                                                      |
                                                      v
                                        +--------------------------+
                                        | Multi-AI Provider Adapters|
                                        | SiliconFlow/Replicate/   |
                                        | Gemini/Hunyuan/Flux/Wan  |
                                        +--------------------------+
```

---

## 📁 Monorepo Layout

```
vidgen/
├── web/           # User-facing Web application (Nuxt 3, Vue 3, Tailwind CSS, Pinia)
├── admin/         # Management Admin Panel application (Nuxt 3 SPA, VueFlow, Chart.js)
├── backend/       # Core REST API & Worker service (FastAPI, SQLAlchemy, Celery, Alembic)
├── systemd/       # Production Systemd unit definitions & deployment scripts
└── docs/          # Open-source technical documentation suite
```

---

## 🔒 Security Model & Isolation

- **Token Isolation**: User tokens (`auth_token`) and Admin tokens (`admin_token`) are signed with distinct secrets (`JWT_SECRET_KEY` vs `ADMIN_JWT_SECRET_KEY`) to prevent privilege escalation.
- **Port Exposure**: In production, application servers listen strictly on `127.0.0.1`. Only Nginx exposes ports 80/443.
