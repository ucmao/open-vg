<div align="center">

<img src="docs/assets/logo.png" alt="VidGen Logo" width="160" style="border-radius: 20px; box-shadow: 0 4px 20px rgba(0,0,0,0.15);" />

# VidGen 🎨⚡

**Production-Grade Open-Source AI Video & Image Generation Platform**

[![Live Demo](https://img.shields.io/badge/Live%20Demo-vidgenerator.ai-0070f3?style=for-the-badge&logo=google-chrome&logoColor=white)](https://vidgenerator.ai)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Nuxt 3](https://img.shields.io/badge/Nuxt-3.x-00DC82?style=for-the-badge&logo=nuxt.js&logoColor=white)](https://nuxt.com/)
[![FastAPI](https://img.shields.io/badge/FastAPI-Async-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![PRs Welcome](https://img.shields.io/badge/PRs-Welcome-brightgreen.svg?style=for-the-badge)](https://github.com/)

[English](README.md) | [简体中文](README_CN.md) | [日本語](README_JA.md) | [한국어](README_KO.md) | [Español](README_ES.md) | [Português](README_PT.md) | [Deutsch](README_DE.md) | [Français](README_FR.md)

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
- **Flexible AI Integration**: Built-in support for SiliconFlow, Replicate, Gemini API, and custom provider pipelines.
- **Node-Based Workflow Executor**: Execute complex multi-step generation workflows (`backend/app/services/workflow_executor.py`).
- **Asynchronous Task Queue**: Celery task processor for heavy generation jobs, preventing API thread blocking.
- **Real-Time Job Updates**: Real-time progress notifications streamed via WebSocket & Redis Pub/Sub.

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
| **Frontend Web** | **Nuxt 3** (Vue 3, SSR/ISR), **Pinia**, **Tailwind CSS**, **Lucide Icons**, Axios, Socket.io |
| **Admin Panel** | **Nuxt 3** (Vue 3), **Tailwind CSS**, **Vue i18n** (EN/ZH), Axios |
| **Backend API** | **FastAPI** (Python 3.10+), **SQLAlchemy** (Async ORM), **Pydantic v2**, JWT |
| **Task Queue & Workers** | **Celery**, **Flower** (Monitoring), **Redis** (Broker & Cache) |
| **Database** | **PostgreSQL** 14+ with **Alembic** database migration tracking |
| **Storage & CDN** | **Cloudflare R2** / AWS S3 / Aliyun OSS (S3-compatible object storage) |
| **AI Providers** | SiliconFlow, Replicate, Google Gemini, Custom Provider Adapters |
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

- 🌐 **Web User Portal**: `http://localhost:3000`
- 🔧 **Admin Panel**: `http://localhost:3001` (Default Admin: `admin` / Password: `admin123`)
- 🐍 **Backend API (Swagger Docs)**: `http://localhost:8000/docs`

> 💡 **Automated Master Seed Data**: On container startup, `scripts/seed_all.py` runs automatically to migrate the database schema, create the initial superadmin, import pre-configured AI generation models, credit recharge packages, and SEO settings within 1 minute!

---

### 🛠️ Option 2: Manual Local Setup

#### Prerequisites
- **Python**: 3.10 or higher
- **Node.js**: 18.x or higher
- **PostgreSQL**: 14.x or higher
- **Redis**: 6.x or higher

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
# Run Alembic migrations
alembic upgrade head

# Run CLI initialization scripts
python scripts/init_database.py
python scripts/create_first_admin.py
python scripts/init_seo_config.py
python scripts/init_recharge_packages.py
```

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

# Import new AI models into system database
python scripts/import_models.py

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
