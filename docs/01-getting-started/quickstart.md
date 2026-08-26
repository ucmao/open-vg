# 5-Minute Quickstart Guide

This guide gets you up and running with **VidGen** in under 5 minutes for local evaluation or testing.

---

## ⚡ Quick Evaluation with Docker Compose

The fastest way to spin up the entire VidGen stack (Web Portal, Admin Panel, FastAPI Backend, Celery Worker, PostgreSQL, and Redis) is via Docker Compose.

### 1. Prerequisites
- [Docker Engine 24.0+](https://docs.docker.com/get-docker/)
- [Docker Compose v2.20+](https://docs.docker.com/compose/install/)

### 2. Launch Stack

```bash
# Clone the repository
git clone https://github.com/ucmao/vidgen.git
cd vidgen

# Copy sample environment configuration
cp backend/.env.example backend/.env
cp web/.env.example web/.env
cp admin/.env.example admin/.env

# Spin up all containers in background
docker compose up -d
```
> 💡 *Tip: Omit `-d` or run `docker compose logs -f backend` to stream live startup logs & external API checklist.*

### 3. Verify Running Services

Once containers start:
- **User Web Portal**: Access `http://localhost:3000`
- **Admin Panel**: Access `http://localhost:3001`
- **FastAPI API Swagger**: Access `http://localhost:8000/docs`

---

## 💻 Quickstart for Local Source Setup

If you want to run VidGen directly from source for development:

### Step 1: Install System Dependencies
- Node.js `24.x LTS` (24.15+)
- Python `3.11+`
- PostgreSQL `15.x+` (`brew install postgresql@15` or install it from your distribution's package repository)
- Redis `7.x+` (`brew install redis` or `sudo apt install redis-server`)

### Step 2: Install Backend Dependencies
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

### Step 3: Run Database Migrations & Initial Data
```bash
python scripts/seed_all.py
```
> 💡 `seed_all.py` automatically migrates database schema (`alembic upgrade head`), creates the `admin` superadmin (printing a generated local password when `INITIAL_ADMIN_PASSWORD` is omitted), and imports the safe seed profile with neutral, bundled demo media. The historical full export requires the explicit `SEED_PROFILE=full ALLOW_UNSAFE_FULL_SEED=true` opt-in after a license/content review.

### Step 4: (Optional) Enable Zero-Cost Mock AI Generation Mode
To test AI video and image generation locally without paid API keys:
```bash
# In backend/.env
MOCK_AI_GENERATION=true
```

### Step 5: Install Frontend Dependencies & Start Servers

**Terminal 1 - FastAPI Backend API:**
```bash
cd backend && source venv/bin/activate
uvicorn app.main:app --reload --port 8000
```

**Terminal 2 - Celery Task Worker:**
```bash
cd backend && source venv/bin/activate
celery -A app.celery_app worker -l info --pool solo
```

**Terminal 3 - User Web Portal:**
```bash
cd web && npm install && npm run dev
```

**Terminal 4 - Admin Management Panel:**
```bash
cd admin && npm install && npm run dev
```

---

## 📚 Next Steps

- Explore the [Exhaustive Environment Variables Reference](./environment-variables.md) to configure AI API keys.
- Read the [Local Development Guide](./local-development.md) for contribution guidelines.
