<div align="center">

<img src="docs/assets/logo.png" alt="VidGen Logo" width="320" style="border-radius: 20px; box-shadow: 0 4px 20px rgba(0,0,0,0.15);" />

**Full-Stack Open-Source AI Video & Image Generation Platform**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.11%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Nuxt 3](https://img.shields.io/badge/Nuxt-3.21.11-00DC82?style=for-the-badge&logo=nuxt.js&logoColor=white)](https://nuxt.com/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.141.1-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Docker Compose](https://img.shields.io/badge/Docker%20Compose-Ready-2496ED?style=for-the-badge&logo=docker&logoColor=white)](docker-compose.yml)

[English](README.md) | [简体中文](README_CN.md)

</div>

<p align="center">
  <a href="https://vidgenerator.ai"><b>🚀 Live Demo</b></a> •
  <a href="#-key-features"><b>✨ Features</b></a> •
  <a href="#️-tech-stack"><b>🛠️ Tech Stack</b></a> •
  <a href="#-quick-start"><b>⚡ Quick Start</b></a> •
  <a href="#-repository-structure"><b>📁 Architecture</b></a>
</p>

---

> 🚀 **Live Demo & Battle-Tested**: VidGen powers [vidgenerator.ai](https://vidgenerator.ai) in production.

## 🌟 Overview

**VidGen** is a modern, high-performance, open-source AI Video and Image Generation platform designed for creators, developers, and entrepreneurs. Built on a clean monorepo architecture, VidGen seamlessly combines a fast SSR Nuxt 3 user portal, a bilingual Nuxt 3 admin panel, and an asynchronous Python FastAPI backend powered by Celery task queues.

Whether you are launching an AI image/video generation platform or building custom workflow pipelines, VidGen provides a complete, battle-tested foundation with built-in credit monetization, community sharing, SEO optimization, and content moderation.

---

## ✨ Key Features

### 🎨 Multi-Modal AI Generation
- **Text-to-Image (Text2Img)**: Generate high-resolution images using state-of-the-art models (FLUX.1, SDXL, Midjourney).
- **Image-to-Image (Img2Img)**: Transform existing images with custom prompt guidance and strength parameters.
- **Text-to-Video (Text2Video)**: Create dynamic AI video clips from text prompts (HunyuanVideo, Luma, Pika, Runway).
- **Image-to-Video (Img2Video)**: Animate static photos into high-definition videos with motion control.

### 🤖 Multi-Provider Workflow Engine
- **Flexible AI Integration**: Built-in support for Replicate, Gemini API, and custom provider pipelines.
- **Node-Based Workflow Executor**: Execute complex multi-step generation workflows (`backend/app/services/workflow_executor.py`).
- **Asynchronous Task Queue**: Celery task processor for heavy generation jobs, preventing API thread blocking.
- **Job Updates**: Authenticated native WebSocket notifications with polling fallback for background-worker jobs.

### 💰 Monetization & Credit System
- **Payment Gateways**: Integrated with **PayPal** and **Stripe** for seamless global subscriptions and credit package purchases.
- **Credit Economics**: Pay-as-you-go credit deduction for model runs with customizable pricing per model option.
- **Discount & Promo Engine**: Support for discount offers, promo codes, and special sales packages.
- **Daily Check-in Rewards**: Interactive daily check-in feature with streak multipliers and bonus credits.

### 🌐 Prompt Community & Social Features
- **Explore Gallery**: Masonry layout showcasing community creations, prompts, models used, and generation parameters.
- **Creator Profiles**: Custom user handles (`@username`), bios, avatars, and personal work showcases.
- **Social Engagement**: Like, favorite, comment on works, and follow creators.
- **SEO & Aggregation Pages**: Dynamic SEO metadata, sitemap generator, topic aggregation pages (`/topic/...`), category pages (`/category/...`), and effect pages (`/effects/...`).

### 🔧 Feature-Rich Admin Panel
- **Bilingual i18n Support**: 100% English UI by default with 1-click Chinese language toggle (`English` / `中文`).
- **Sockpuppet / Virtual User Generator**: Generate realistic synthetic user accounts using `faker` & automatic Cloudflare R2 avatar fetching.
- **Content Moderation**: Automated NSFW image filter, sensitive keyword lexicon manager, user report handling, and work banning.
- **Model & Pricing Management**: Configure AI models, base credit costs, option multipliers, and workflow templates without redeploying.
- **Operational Management**: Banner & carousel slider manager, blog post editor, and system configuration.

---

## 🛠️ Tech Stack

| Layer | Technologies |
| :--- | :--- |
| **Frontend Web** | **Nuxt 3.21.11** (Vue 3, SSR/ISR), **Pinia**, **Tailwind CSS**, **Lucide Icons**, Axios, native WebSocket |
| **Admin Panel** | **Nuxt 3.21.11** (Vue 3), **Tailwind CSS**, custom i18n (EN/ZH), Axios |
| **Backend API** | **FastAPI 0.141.1** (Python 3.11+), **SQLAlchemy 2.0.25** (synchronous ORM), **Pydantic 2.12.5**, JWT |
| **Task Queue & Workers** | **Celery 5.4+**, **Flower 2.0+** (Monitoring), **Redis 7** (Broker & Cache) |
| **Database** | **PostgreSQL 15+** with **Alembic** database migration tracking |
| **Storage & CDN** | **Cloudflare R2** / AWS S3 / Aliyun OSS (S3-compatible object storage) |
| **AI Providers** | Replicate, Google Gemini, Custom Provider Adapters |
| **Payments** | PayPal SDK, Stripe API |
| **Containerization** | **Docker**, **Docker Compose** (One-click stack orchestration) |
| **Service Management** | Unified **systemd** service suite (`systemd/`), Nginx Reverse Proxy |

---

## 📁 Repository Structure

```
vidgen/
├── web/                     # 🌐 Frontend Web Application (Nuxt 3, Port 3000)
│   ├── pages/               # Page routes (explore, generate, profile, recharge, etc.)
│   ├── components/          # Reusable UI components
│   ├── composables/         # Custom composable hooks
│   ├── stores/              # Pinia state management stores
│   └── nuxt.config.ts       # Nuxt 3 configuration
│
├── admin/                   # 🔧 Admin Management Panel (Nuxt 3, Port 3001)
│   ├── pages/               # Admin routes (users, works, moderation, models, etc.)
│   ├── composables/         # Admin API & i18n composables (useAdminI18n.ts)
│   ├── locales/             # Bilingual UI dictionaries (en.ts, zh.ts)
│   └── nuxt.config.ts
│
├── backend/                 # 🐍 Backend API & Async Engine (FastAPI, Port 8000)
│   ├── app/
│   │   ├── main.py          # FastAPI app entry point & routes registration
│   │   ├── celery_app.py    # Celery task queue configuration
│   │   ├── routes/          # API route handlers (auth, works, generation, admin*.py)
│   │   ├── models/          # SQLAlchemy database models
│   │   ├── services/        # Storage, Email, Gemini, Moderation, Payment services
│   │   ├── tasks/           # Asynchronous Celery workflow tasks
│   │   └── utils/           # i18n, Logger, Auth, Slug, Validation utilities
│   ├── migrations/          # Alembic database migration scripts
│   ├── scripts/             # System initialization & maintenance CLI tools
│   └── requirements.txt     # Python dependencies
│
├── systemd/                 # ⚙️ Unified Service Management & Deployment Scripts
│   ├── deploy.sh            # Automated deployment script
│   ├── manage-services.sh   # Interactive systemd service manager
│   └── *.service            # Service unit configuration files
│
└── docs/                    # 📚 Technical Documentation & Guides
    ├── AA_PANEL_DEPLOYMENT_GUIDE.md
    ├── SYSTEMD_UNIFIED_GUIDE.md
    └── ...
```

---

## ⚡ Quick Start

### 🐳 Option 1: One-Click Docker Compose (Recommended)

Run the entire VidGen stack (Web, Admin, Backend, Celery, Postgres, Redis) with a single command:

```bash
# Clone repository
git clone https://github.com/ucmao/vidgen.git
cd vidgen

# Launch all 6 services via Docker Compose
docker compose up -d
```
> 💡 *Tip: Omit `-d` or run `docker compose logs -f backend` to stream live startup logs & external API checklist.*

- 🌐 **Web User Portal**: `http://localhost:3000`
- 🔧 **Admin Panel**: `http://localhost:3001` (user: `admin`; the first startup log prints a generated local password unless `INITIAL_ADMIN_PASSWORD` is set)
- 🐍 **Backend API (Swagger Docs)**: `http://localhost:8000/docs`

> 💡 **Local initialization**: On container startup, `scripts/seed_all.py` applies migrations, creates the superadmin, and imports the demo dataset. The development stack binds published ports to `127.0.0.1` and must not be exposed directly to the internet.

> [!IMPORTANT]
> **External Integrations & API Keys Checklist**:  
> Running Docker spins up full local infrastructure, database schemas, frontend/admin panels, and demo datasets out of the box. To activate real external third-party services, configure your `backend/.env`:
> - **AI Generation**: Fill `REPLICATE_API_KEY` (or keep `MOCK_AI_GENERATION=true` for zero-cost testing).
> - **Payments**: Fill `PAYPAL_CLIENT_ID` / `PAYPAL_CLIENT_SECRET`.
> - **Email Verification**: Fill `SMTP_HOST` / `SMTP_PORT`. For local testing without SMTP, explicitly start Compose with `RETURN_VERIFICATION_CODES=true`; this flag is ignored in production.
> - **OAuth Login**: Fill `GOOGLE_CLIENT_ID` / `GOOGLE_CLIENT_SECRET`.

---

### 🔐 Production Docker baseline

Do not deploy the development Compose file publicly. The production baseline requires strong credentials, disables verification-code responses, skips demo-data import, and binds application ports to loopback for a TLS reverse proxy:

```bash
# Save these and other integration credentials in a private .env.production file.
POSTGRES_PASSWORD='replace-with-a-strong-database-password'
JWT_SECRET='replace-with-at-least-32-random-characters'
CONFIG_ENCRYPTION_KEY='replace-with-an-independent-random-secret'
INITIAL_ADMIN_EMAIL='admin@example.com'
INITIAL_ADMIN_PASSWORD='replace-with-a-strong-admin-password'
BACKEND_URL='https://api.example.com'
FRONTEND_URL='https://example.com'
ADMIN_FRONTEND_URL='https://admin.example.com'
WEBSOCKET_URL='wss://api.example.com'

docker compose --env-file .env.production -f docker-compose.prod.yml up -d
```

Terminate HTTPS at a reverse proxy and keep backend ports unreachable from untrusted networks. Redis is mandatory for production rate limiting.

---

### 🛠️ Option 2: Manual Local Setup

#### Prerequisites
- **Python**: 3.11 or higher
- **Node.js**: 24.15 or higher
- **PostgreSQL**: 15.x or higher
- **Redis**: 7.x or higher

---

### 1. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create and activate Python virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create configuration from template
cp .env.example .env
# Edit backend/.env to configure DATABASE_URL, REDIS_URL, R2 credentials, API keys
```

#### Initialize Database & Seed Data

```bash
# Optional: configure the initial admin (a random local password is generated otherwise)
export INITIAL_ADMIN_USERNAME=admin
export INITIAL_ADMIN_PASSWORD=replace-with-a-secure-password

# Apply migrations, create the admin, and import the complete demo dataset
python scripts/seed_all.py
```

The command is safe to run repeatedly. A failed migration or initialization step exits with a non-zero status instead of continuing with a partial setup.

#### Run FastAPI Development Server

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
- **API Docs (Swagger UI)**: `http://localhost:8000/docs`

---

### 2. Celery Worker Setup (Asynchronous Tasks)

```bash
cd backend
source venv/bin/activate

# Start Celery worker for image & video generation tasks
celery -A app.celery_app worker --loglevel=info -c 4
```

---

### 3. Frontend Web Setup (Port 3000)

```bash
cd web

# Install dependencies
npm install

# Create configuration from template
cp .env.example .env
# Edit web/.env to point NUXT_PUBLIC_API_BASE_URL to http://localhost:8000

# Start Nuxt 3 development server
npm run dev
```
- **Web App**: `http://localhost:3000`

---

### 4. Admin Panel Setup (Port 3001)

```bash
cd admin

# Install dependencies
npm install

# Start Admin Panel development server
npm run dev
```
- **Admin Panel**: `http://localhost:3001`
- **Default Credentials**: Created via `python scripts/create_first_admin.py`

---

## 🚢 Service Management & Production Deployment

VidGen includes a production-ready **systemd unified service manager** located in `systemd/`:

```bash
# Run interactive service manager
chmod +x systemd/manage-services.sh
./systemd/manage-services.sh
```

Available service commands:
- **`manage-services.sh status`**: View real-time status of Web, Admin, Backend API, and Celery Workers.
- **`manage-services.sh start`**: Start all services simultaneously.
- **`manage-services.sh restart`**: Gracefully restart all services.
- **`deploy.sh`**: One-click automated production deployment script.

For detailed Nginx and aaPanel deployment instructions, refer to [docs/05-deployment/production-deployment.md](docs/05-deployment/production-deployment.md).

---

## 🛠️ CLI Maintenance Tools

The `backend/scripts/` folder provides utility scripts for administrative maintenance:

```bash
# Add credits to a user account
python scripts/add_credits.py --email user@example.com --amount 1000

# Reapply the canonical configuration and demo dataset
python scripts/seed_all.py

# Backfill work tags and slugs
python scripts/update_url_slugs_from_titles.py
```

---

## 📄 License

This project is open-source under the **MIT License**. See the [LICENSE](LICENSE) file for details.

---

## 🤝 Contributing & Community

Contributions, issues, and feature requests are welcome!  
Feel free to open an Issue or submit a Pull Request.

*If you find VidGen helpful, please give us a ⭐️ Star on GitHub!*
