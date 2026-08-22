<div align="center">

<img src="docs/assets/logo.png" alt="VidGen Logo" width="160" style="border-radius: 20px; box-shadow: 0 4px 20px rgba(0,0,0,0.15);" />

# VidGen 🎨⚡

**Produktionsbereite Open-Source-KI-Video- und Bildgenerierungsplattform**

[![Live Demo](https://img.shields.io/badge/Live%20Demo-vidgenerator.ai-0070f3?style=for-the-badge&logo=google-chrome&logoColor=white)](https://vidgenerator.ai)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Nuxt 3](https://img.shields.io/badge/Nuxt-3.x-00DC82?style=for-the-badge&logo=nuxt.js&logoColor=white)](https://nuxt.com/)
[![FastAPI](https://img.shields.io/badge/FastAPI-Async-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![PRs Welcome](https://img.shields.io/badge/PRs-Willkommen-brightgreen.svg?style=for-the-badge)](.github/CONTRIBUTING.md)

[English](README.md) | [简体中文](README_CN.md) | [日本語](README_JA.md) | [한국어](README_KO.md) | [Español](README_ES.md) | [Português](README_PT.md) | [Deutsch](README_DE.md) | [Français](README_FR.md)

</div>

<p align="center">
  <a href="https://vidgenerator.ai"><b>🚀 Live Demo</b></a> •
  <a href="#-hauptfunktionen"><b>✨ Funktionen</b></a> •
  <a href="#️-tech-stack"><b>🛠️ Tech Stack</b></a> •
  <a href="#-schnellstart"><b>⚡ Schnellstart</b></a> •
  <a href="#-architektur-und-struktur"><b>📁 Architektur</b></a>
</p>

---

> 🚀 **Live Demo & Praxiserprobt (Battle-Tested)**: VidGen treibt die kommerzielle Live-Plattform [vidgenerator.ai](https://vidgenerator.ai) in der Produktion an.

## 🌟 Übersicht

**VidGen** ist eine moderne, hochperformante Open-Source-Plattform zur KI-Video- und Bildgenerierung für Ersteller, Entwickler und Unternehmer. Auf einer sauberen Monorepo-Architektur aufgebaut, kombiniert VidGen nahtlos ein schnelles SSR Nuxt 3 Benutzerportal, ein mehrsprachiges Nuxt 3 Admin-Panel und ein asynchrones Python FastAPI Backend, das von Celery-Aufgabenwarteschlangen angetrieben wird.

Egal ob Sie eine Plattform zur KI-Bild-/Videogenerierung starten oder benutzerdefinierte Workflow-Pipelines aufbauen: VidGen bietet ein vollständiges, praxiserprobtes Fundament mit integrierter Guthaben-Monetarisierung, Community-Sharing, SEO-Optimierung und Inhaltsmoderation.

---

## ✨ Hauptfunktionen

### 🎨 Multimodale KI-Generierungs-Engine
- **Text-zu-Bild (Text2Img)**: Generieren Sie hochauflösende Bilder mit führenden Modellen (FLUX.1, SDXL, Midjourney).
- **Bild-zu-Bild (Img2Img)**: Transformieren Sie vorhandene Bilder mit benutzerdefinierten Prompt-Anweisungen und Stärkeparametern.
- **Text-zu-Video (Text2Video)**: Erstellen Sie dynamische KI-Videoclips aus Text-Prompts (HunyuanVideo, Luma, Pika, Runway).
- **Bild-zu-Video (Img2Video)**: Animieren Sie statische Fotos in hochauflösende Videos mit Bewegungssteuerung.

### 🤖 Multi-Provider-Workflow-Engine
- **Flexible KI-Integration**: Integrierte Unterstützung für SiliconFlow, Replicate, Gemini API und benutzerdefinierte Provider-Pipelines.
- **Knotenbasierter Workflow-Executor**: Führen Sie komplexe mehrstufige Generierungs-Workflows aus (`backend/app/services/workflow_executor.py`).
- **Asynchrone Aufgabenwarteschlange**: Celery-Aufgabenprozessor für schwere Generierungsaufträge zur Vermeidung von API-Thread-Blockaden.
- **Echtzeit-Updates**: Echtzeit-Fortschrittsbenachrichtigungen über WebSocket & Redis Pub/Sub gestreamt.

### 💰 Monetarisierung & Guthabensystem
- **Zahlungs-Gateways**: Nahtlos integriert mit **PayPal** und **Stripe** für globale Abonnements und Guthabenpaket-Käufe.
- **Guthaben-Ökonomie**: Nutzungsbasierte Guthaben-Abbuchen für Modellläufe mit anpassbaren Preisen pro Modelloption.
- **Rabatt- & Promo-Engine**: Unterstützung für Rabattangebote, Promo-Codes und spezielle Verkaufspakete.
- **Tägliche Check-in-Belohnungen**: Interaktive tägliche Check-in-Funktion mit Serien-Multiplikatoren und Bonus-Guthaben.

### 🌐 Prompt-Community & Soziale Funktionen
- **Exploration-Galerie**: Masonry-Layout zur Präsentation von Community-Kreationen, Prompts, verwendeten Modellen und Generierungsparametern.
- **Ersteller-Profile**: Benutzerdefinierte Handles (`@username`), Biografien, Avatare und persönliche Werk-Präsentationen.
- **Soziale Interaktion**: Liken, Favorisieren, Kommentieren von Werken und Folgen von Erstellern.
- **SEO & Aggregationsseiten**: Dynamische SEO-Metadaten, Sitemap-Generator, Themenaggregationsseiten (`/topic/...`), Kategorieseiten (`/category/...`) und Effektseiten (`/effects/...`).

### 🔧 Funktionsreiches Admin-Panel
- **Mehrsprachige (i18n) Unterstützung**: Verfügbar in Englisch, Chinesisch, Japanisch, Koreanisch, Spanisch, Portugiesisch, Deutsch und Französisch.
- **Virtueller Benutzergenerator (Sockpuppets)**: Erstellen Sie realistische synthetische Benutzerkonten mit `faker` & automatischem Cloudflare R2 Avatar-Abruf.
- **Inhaltsmoderation**: Automatischer NSFW-Bildfilter, Lexikonsystem für sensible Schlüsselwörter, Benutzer-Meldeabwicklung und Werk-Sperrung.
- **Modell- & Preisverwaltung**: Konfigurieren Sie KI-Modelle, Basis-Guthabenkosten, Optionsmultiplikatoren und Workflow-Vorlagen ohne Re-Deployment.
- **Betriebsverwaltung**: Banner- & Karussell-Slider-Manager, Blog-Post-Editor und Systemkonfiguration.

---

## 🛠️ Tech Stack

| Schicht | Technologien |
| :--- | :--- |
| **Frontend Web Portal** | **Nuxt 3** (Vue 3, SSR/ISR), **Pinia**, **Tailwind CSS**, **Lucide Icons**, Axios, Socket.io |
| **Admin Panel** | **Nuxt 3** (Vue 3), **Tailwind CSS**, **Vue i18n** (8 Sprachen), Axios |
| **Backend API** | **FastAPI** (Python 3.10+), **SQLAlchemy** (Async ORM), **Pydantic v2**, JWT |
| **Aufgabenwarteschlange & Worker** | **Celery**, **Flower** (Überwachung), **Redis** (Broker & Cache) |
| **Datenbank** | **PostgreSQL** 14+ mit **Alembic** Datenbank-Migrationsverfolgung |
| **Speicher & CDN** | **Cloudflare R2** / AWS S3 / Aliyun OSS (S3-kompatibler Objektspeicher) |
| **KI-Anbieter** | SiliconFlow, Replicate, Google Gemini, Benutzerdefinierte Adapter |
| **Zahlungs-Gateways** | PayPal SDK, Stripe API |
| **Containerisierung** | **Docker**, **Docker Compose** (Ein-Klick-Stack-Orchestrierung) |
| **Dienstverwaltung** | Einheitliche **systemd** Dienst-Suite (`systemd/`), Nginx Reverse Proxy |

---

## 📁 Architektur und Struktur

```
vidgen/
├── web/                     # 🌐 Frontend Web-Anwendung (Nuxt 3, Port 3000)
│   ├── pages/               # Seitenrouten (Erkunden, Generieren, Profil, Aufladen etc.)
│   ├── components/          # Wiederverwendbare UI-Komponenten
│   ├── composables/         # Benutzerdefinierte Composable Hooks
│   ├── stores/              # Pinia Statusverwaltung
│   └── nuxt.config.ts       # Nuxt 3 Konfiguration
│
├── admin/                   # 🔧 Admin-Verwaltungspanel (Nuxt 3, Port 3001)
│   ├── pages/               # Admin-Routen (Benutzer, Werke, Moderation, Modelle etc.)
│   ├── composables/         # Admin API & i18n Composables (useAdminI18n.ts)
│   ├── locales/             # Mehrsprachige Wörterbücher (en.ts, de.ts etc.)
│   └── nuxt.config.ts
│
├── backend/                 # 🐍 Backend API & Asynchrone Engine (FastAPI, Port 8000)
│   ├── app/
│   │   ├── main.py          # FastAPI App-Einstiegspunkt & Routenregistrierung
│   │   ├── celery_app.py    # Celery Aufgabenwarteschlangen-Konfiguration
│   │   ├── routes/          # API-Routen-Handler (auth, works, generation, admin*.py)
│   │   ├── models/          # SQLAlchemy Datenbankmodelle
│   │   ├── services/        # Speicher-, E-Mail-, Gemini-, Moderations-, Zahlungsdienste
│   │   ├── tasks/           # Asynchrone Celery Workflow-Aufgaben
│   │   └── utils/           # i18n, Logger, Auth, Slug, Validierung Dienstprogramme
│   ├── migrations/          # Alembic Datenbank-Migrationsskripte
│   ├── scripts/             # Systeminitialisierung & Wartung CLI-Tools
│   └── requirements.txt     # Python-Abhängigkeiten
│
├── systemd/                 # ⚙️ Einheitliche Dienstverwaltung & Bereitstellungsskripte
│   ├── deploy.sh            # Automatisiertes Bereitstellungsskript
│   ├── manage-services.sh   # Interaktiver systemd Dienstmanager
│   └── *.service            # Dienst-Konfigurationsdateien
│
└── docs/                    # 📚 Technische Dokumentation & Anleitungen
    ├── AA_PANEL_DEPLOYMENT_GUIDE.md
    ├── SYSTEMD_UNIFIED_GUIDE.md
    └── ...
```

---

## ⚡ Schnellstart

### 🐳 Option 1: Ein-Klick Docker Compose (Empfohlen)

Starten Sie den gesamten VidGen-Stack (Web, Admin, Backend, Celery, Postgres, Redis) mit einem einzigen Befehl:

```bash
# Repository klonen
git clone https://github.com/ucmao/vidgen.git
cd vidgen

# Alle 6 Dienste über Docker Compose starten
docker compose up -d
```

- 🌐 **Web-Benutzerportal**: `http://localhost:3000`
- 🔧 **Admin-Panel**: `http://localhost:3001` (Standard-Admin: `admin` / Passwort: `admin123`)
- 🐍 **Backend API (Swagger Docs)**: `http://localhost:8000/docs`

> 💡 **Automatisierte Master-Seed-Daten**: Beim Containerstart wird `scripts/seed_all.py` automatisch ausgeführt, um das Datenbank-Schema zu migrieren, den ersten Superadmin zu erstellen, KI-Modelle, Aufladepakete und SEO-Einstellungen unter 1 Minute zu initialisieren!

---

### 🛠️ Option 2: Manuelle lokale Einrichtung

#### Voraussetzungen
- **Python**: 3.10 oder höher
- **Node.js**: 18.x oder höher
- **PostgreSQL**: 14.x oder höher
- **Redis**: 6.x oder höher

---

### 1. Backend-Einrichtung

```bash
# In das Backend-Verzeichnis wechseln
cd backend

# Virtuelle Python-Umgebung erstellen und aktivieren
python3 -m venv venv
source venv/bin/activate  # Unter Windows: venv\Scripts\activate

# Abhängigkeiten installieren
pip install -r requirements.txt

# Konfiguration aus Vorlage erstellen
cp .env.example .env
# backend/.env bearbeiten für DATABASE_URL, REDIS_URL, R2, API-Schlüssel
```

#### Datenbank initialisieren & Seed-Daten laden

```bash
# Alembic-Migrationen ausführen
alembic upgrade head

# Master-Seed-Skript ausführen
python scripts/seed_all.py
```

#### FastAPI-Entwicklungsserver ausführen

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
- **API Docs (Swagger UI)**: `http://localhost:8000/docs`

---

### 2. Celery Worker Einrichtung (Asynchrone Aufgaben)

```bash
cd backend
source venv/bin/activate

# Celery Worker für Bild- & Videogenerierungsaufgaben starten
celery -A app.celery_app worker --loglevel=info -c 4
```

---

### 3. Frontend Web Einrichtung (Port 3000)

```bash
cd web

# Abhängigkeiten installieren
npm install

# Konfiguration aus Vorlage erstellen
cp .env.example .env

# Nuxt 3 Entwicklungsserver starten
npm run dev
```
- **Web App**: `http://localhost:3000`

---

### 4. Admin-Panel Einrichtung (Port 3001)

```bash
cd admin

# Abhängigkeiten installieren
npm install

# Admin-Panel Entwicklungsserver starten
npm run dev
```
- **Admin Panel**: `http://localhost:3001`
- **Standard-Anmeldedaten**: Erstellt über `python scripts/create_first_admin.py` (`admin` / `admin123`)

---

## 🚢 Dienstverwaltung & Produktions-Bereitstellung

VidGen enthält einen produktionsbereiten **systemd einheitlichen Dienstmanager** im Verzeichnis `systemd/`:

```bash
# Interaktiven Dienstmanager ausführen
chmod +x systemd/manage-services.sh
./systemd/manage-services.sh
```

Verfügbare Dienstbefehle:
- **`manage-services.sh status`**: Echtzeit-Status von Web, Admin, Backend API und Celery Workern anzeigen.
- **`manage-services.sh start`**: Alle Dienste gleichzeitig starten.
- **`manage-services.sh restart`**: Alle Dienste ordnungsgemäß neu starten.
- **`deploy.sh`**: Automatisiertes Ein-Klick-Produktionsskript.

Detaillierte Nginx- und aaPanel-Bereitstellungsanweisungen finden Sie unter [docs/05-deployment/production-deployment.md](docs/05-deployment/production-deployment.md).

---

## 🛠️ CLI-Wartungstools

Der Ordner `backend/scripts/` bietet Nützlichkeitsskripte für die administrative Wartung:

```bash
# Guthaben zu einem Benutzerkonto hinzufügen
python scripts/add_credits.py --email user@example.com --amount 1000

# Neue KI-Modelle in die Datenbank importieren
python scripts/import_models.py

# Werk-Slugs und Tags aktualisieren
python scripts/update_url_slugs_from_titles.py
```

---

## 📄 Lizenz

Dieses Projekt ist Open-Source unter der **MIT-Lizenz**. Siehe die Datei [LICENSE](LICENSE) für Details.

---

## 🤝 Mitwirken & Community

Beiträge, Problemmeldungen und Funktionsanfragen sind herzlich willkommen!  
Fühlen Sie sich frei, ein Issue zu öffnen oder ein Pull Request einzureichen.

*Wenn Sie VidGen nützlich finden, geben Sie uns bitte ein ⭐️ Star auf GitHub!*
