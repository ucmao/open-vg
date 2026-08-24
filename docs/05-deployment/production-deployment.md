# Complete Production Deployment Guide

This document details how to deploy VidGen on Linux VPS / bare-metal servers using Nginx, Systemd, PostgreSQL, and Redis.

---

## 📋 Architecture & Ports

| Port | Service Identifier | Role | Exposure |
|---|---|---|---|
| **80 / 443** | **Nginx** | Public HTTP/HTTPS Reverse Proxy & SSL | **Public** |
| **3000** | **`vidgen-web`** | Nuxt 3 User Web Portal Node SSR | Localhost `127.0.0.1:3000` |
| **3001** | **`vidgen-admin`** | Nuxt 3 Admin Panel SPA | Localhost `127.0.0.1:3001` |
| **8000** | **`vidgen-backend`** | FastAPI Core API Service | Localhost `127.0.0.1:8000` |
| **5432** | **PostgreSQL** | Relational Database Engine | Localhost only |
| **6379** | **Redis** | Task Broker & WebSocket Pub/Sub Channel | Localhost only |

---

## 🚀 Step-by-Step Production Setup

### 1. Prerequisites Installation

The deployment baseline is Python 3.11+, Node.js 24.15+, PostgreSQL 15+, and Redis 7+. Ensure your distribution's package repositories provide compatible PostgreSQL and Redis versions.

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3.11 python3.11-venv python3-pip postgresql redis-server nginx git curl
curl -fsSL https://deb.nodesource.com/setup_24.x | sudo -E bash -
sudo apt install -y nodejs

# Verify the installed runtimes and services meet the required baseline
python3.11 --version
node --version
psql --version
redis-server --version
```

### 2. Code Directory Setup
```bash
sudo mkdir -p /www/wwwroot
cd /www/wwwroot
sudo git clone https://github.com/ucmao/vidgen.git vidgen
sudo chown -R www-data:www-data /www/wwwroot/vidgen
```

### 3. Backend Setup
```bash
cd /www/wwwroot/vidgen/backend
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Apply migrations and initialize the admin account, AI models, recharge
# packages, and SEO settings in one step.
python scripts/seed_all.py
```

### 4. Build Frontends
```bash
cd /www/wwwroot/vidgen/web && npm ci && npm run build
cd /www/wwwroot/vidgen/admin && npm ci && npm run build
```

### 5. Register Systemd Services
```bash
cd /www/wwwroot/vidgen/systemd
sudo ./deploy.sh
sudo ./manage-services.sh start
sudo ./manage-services.sh enable
```
