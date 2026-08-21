<div align="center">

<img src="docs/assets/logo.png" alt="VidGen Logo" width="160" style="border-radius: 20px; box-shadow: 0 4px 20px rgba(0,0,0,0.15);" />

# VidGen 🎨⚡

**Plateforme de génération de vidéo et d'image par IA open source de niveau production**

[![Live Demo](https://img.shields.io/badge/Demo_en_Direct-vidgenerator.ai-0070f3?style=for-the-badge&logo=google-chrome&logoColor=white)](https://vidgenerator.ai)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Nuxt 3](https://img.shields.io/badge/Nuxt-3.x-00DC82?style=for-the-badge&logo=nuxt.js&logoColor=white)](https://nuxt.com/)
[![FastAPI](https://img.shields.io/badge/FastAPI-Async-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![PRs Welcome](https://img.shields.io/badge/PRs-Bienvenus-brightgreen.svg?style=for-the-badge)](https://github.com/)

[English](README.md) | [简体中文](README_CN.md) | [日本語](README_JA.md) | [한국어](README_KO.md) | [Español](README_ES.md) | [Português](README_PT.md) | [Deutsch](README_DE.md) | [Français](README_FR.md)

</div>

<p align="center">
  <a href="https://vidgenerator.ai"><b>🚀 Démo en Direct</b></a> •
  <a href="#-fonctionnalités-principales"><b>✨ Fonctionnalités</b></a> •
  <a href="#️-stack-technologique"><b>🛠️ Stack Technologique</b></a> •
  <a href="#-démarrage-rapide"><b>⚡ Démarrage Rapide</b></a> •
  <a href="#-architecture-du-dépôt"><b>📁 Architecture</b></a>
</p>

---

> 🚀 **Démo en Direct et Éprouvé en Production (Battle-Tested)** : VidGen alimente la plateforme commerciale en direct [vidgenerator.ai](https://vidgenerator.ai).

## 🌟 Vue d'ensemble

**VidGen** est une plateforme moderne, performante et open source de génération d'images et de vidéos par IA, conçue pour les créateurs, développeurs et entrepreneurs. Construite sur une architecture Monorepo propre, VidGen combine de manière transparente un portail utilisateur rapide en SSR Nuxt 3, un panneau d'administration multilingue en Nuxt 3 et un backend asynchrone en Python FastAPI propulsé par des files d'attente Celery.

Que vous lanciez une plateforme de génération d'images/vidéos par IA ou que vous construisiez des flux de travail personnalisés, VidGen fournit une base solide éprouvée avec monétisation par crédits, partage communautaire, optimisation SEO et modération de contenu intégrés.

---

## ✨ Fonctionnalités Principales

### 🎨 Moteur de Génération IA Multimodal
- **Texte vers Image (Text2Img)** : Générez des images haute résolution avec des modèles de pointe (FLUX.1, SDXL, Midjourney).
- **Image vers Image (Img2Img)** : Transformez des images existantes avec guidage par prompt et contrôle d'intensité.
- **Texte vers Vidéo (Text2Video)** : Créez des clips vidéo dynamiques à partir de prompts textuels (HunyuanVideo, Luma, Pika, Runway).
- **Image vers Vidéo (Img2Video)** : Animez des photos statiques en vidéos haute définition avec contrôle de mouvement.

### 🤖 Moteur de Flux de Travail Multi-Fournisseurs
- **Intégration IA Flexible** : Support natif pour SiliconFlow, Replicate, Gemini API et adaptateurs sur mesure.
- **Exécuteur de Flux de Travail basé sur des Nœuds** : Exécutez des flux complexes multi-étapes (`backend/app/services/workflow_executor.py`).
- **File d'Attente de Tâches Asynchrones** : Processeur de tâches Celery pour les lourds travaux de génération, évitant le blocage des API.
- **Mises à Jour en Temps Réel** : Notifications de progression diffusées en temps réel via WebSocket et Redis Pub/Sub.

### 💰 Système de Monétisation et Crédits
- **Passerelles de Paiement** : Intégration native avec **PayPal** et **Stripe** pour abonnements globaux et achats de paquets de crédits.
- **Économie de Crédits** : Déduction de crédits à l'usage avec tarification personnalisable par option de modèle.
- **Moteur de Réductions & Promos** : Support pour offres promotionnelles, codes promo et paquets de vente spéciaux.
- **Récompenses de Check-in Quotidien** : Fonctionnalité interactive de check-in quotidien avec multiplicateurs de série.

### 🌐 Communauté de Prompts et Fonctions Sociales
- **Galerie d'Exploration** : Disposition Masonry présentant les créations de la communauté, prompts, modèles et paramètres.
- **Profils de Créateurs** : Handles personnalisés (`@username`), biographies, avatars et vitrines de travaux personnels.
- **Engagement Social** : Aimer, ajouter aux favoris, commenter les œuvres et suivre les créateurs.
- **Pages SEO et d'Agrégation** : Métadonnées SEO dynamiques, générateur de sitemap, pages d'agrégation de thèmes (`/topic/...`), catégories (`/category/...`) et effets (`/effects/...`).

### 🔧 Panneau d'Administration Complet
- **Support Multilingue (i18n)** : Disponible en Anglais, Chinois, Japonais, Coréen, Espagnol, Portugais, Allemand et Français.
- **Générateur d'Utilisateurs Virtuels (Sockpuppets)** : Créez des comptes synthétiques réalistes avec `faker` et récupération d'avatars Cloudflare R2.
- **Modération de Contenu** : Filtre automatique d'images NSFW, gestionnaire de lexique de mots-clés sensibles, gestion des signalements.
- **Gestion des Modèles et Tarifs** : Configurez modèles IA, coûts de base en crédits, multiplicateurs et modèles de flux sans redéploiement.
- **Gestion Opérationnelle** : Gestionnaire de bannières et carrousels, éditeur d'articles de blog et configuration système.

---

## 🛠️ Stack Technologique

| Couche | Technologies |
| :--- | :--- |
| **Portail Web Frontend** | **Nuxt 3** (Vue 3, SSR/ISR), **Pinia**, **Tailwind CSS**, **Lucide Icons**, Axios, Socket.io |
| **Panneau d'Administration** | **Nuxt 3** (Vue 3), **Tailwind CSS**, **Vue i18n** (8 langues), Axios |
| **API Backend** | **FastAPI** (Python 3.10+), **SQLAlchemy** (Async ORM), **Pydantic v2**, JWT |
| **File de Tâches & Workers** | **Celery**, **Flower** (Surveillance), **Redis** (Broker & Cache) |
| **Base de Données** | **PostgreSQL** 14+ avec suivi des migrations **Alembic** |
| **Stockage & CDN** | **Cloudflare R2** / AWS S3 / Aliyun OSS (compatible S3) |
| **Fournisseurs d'IA** | SiliconFlow, Replicate, Google Gemini, Adaptateurs Personnalisés |
| **Passerelles de Paiement** | PayPal SDK, Stripe API |
| **Conteneurisation** | **Docker**, **Docker Compose** (Orchestration en un clic) |
| **Gestion des Services** | Suite de services **systemd** unifiée (`systemd/`), Reverse Proxy Nginx |

---

## 📁 Architecture du Dépôt

```
vidgen/
├── web/                     # 🌐 Application Web Frontend (Nuxt 3, Port 3000)
│   ├── pages/               # Routes de pages (explorer, générer, profil, recharge, etc.)
│   ├── components/          # Composants UI réutilisables
│   ├── composables/         # Hooks composables personnalisés
│   ├── stores/              # Magasins d'état Pinia
│   └── nuxt.config.ts       # Configuration Nuxt 3
│
├── admin/                   # 🔧 Panneau d'Administration (Nuxt 3, Port 3001)
│   ├── pages/               # Routes admin (utilisateurs, œuvres, modération, modèles, etc.)
│   ├── composables/         # Composables d'API et d'i18n admin (useAdminI18n.ts)
│   ├── locales/             # Dictionnaires multilingues (en.ts, fr.ts, etc.)
│   └── nuxt.config.ts
│
├── backend/                 # 🐍 API Backend & Moteur Asynchrone (FastAPI, Port 8000)
│   ├── app/
│   │   ├── main.py          # Point d'entrée FastAPI et enregistrement des routes
│   │   ├── celery_app.py    # Configuration de la file d'attente Celery
│   │   ├── routes/          # Gestionnaires de routes API (auth, works, generation, admin*.py)
│   │   ├── models/          # Modèles de base de données SQLAlchemy
│   │   ├── services/        # Services de Stockage, E-mail, Gemini, Modération, Paiements
│   │   ├── tasks/           # Tâches asynchrones de flux de travail Celery
│   │   └── utils/           # Utilitaires i18n, Logger, Auth, Slug, Validation
│   ├── migrations/          # Scripts de migration de base de données Alembic
│   ├── scripts/             # Outils CLI d'initialisation et de maintenance
│   └── requirements.txt     # Dépendances Python
│
├── systemd/                 # ⚙️ Scripts de Déploiement et de Gestion des Services
│   ├── deploy.sh            # Script de déploiement automatisé
│   ├── manage-services.sh   # Gestionnaire interactif de services systemd
│   └── *.service            # Fichiers de configuration des unités de service
│
└── docs/                    # 📚 Documentation Technique & Guides
    ├── AA_PANEL_DEPLOYMENT_GUIDE.md
    ├── SYSTEMD_UNIFIED_GUIDE.md
    └── ...
```

---

## ⚡ Démarrage Rapide

### 🐳 Option 1 : Docker Compose en Un Clic (Recommandé)

Lancez l'ensemble de la stack VidGen (Web, Admin, Backend, Celery, Postgres, Redis) avec une seule commande :

```bash
# Cloner le dépôt
git clone https://github.com/ucmao/vidgen.git
cd vidgen

# Lancer les 6 services via Docker Compose
docker compose up -d
```

- 🌐 **Portail Web Utilisateur** : `http://localhost:3000`
- 🔧 **Panneau d'Administration** : `http://localhost:3001` (Admin par défaut : `admin` / Mot de passe : `admin123`)
- 🐍 **Documentation API (Swagger Docs)** : `http://localhost:8000/docs`

> 💡 **Données d'Amorçage Automatiques (Seed Data)** : Au démarrage du conteneur, `scripts/seed_all.py` s'exécute automatiquement pour migrer le schéma, créer le superadministrateur, importer les modèles IA, paquets de recharge et réglages SEO en moins d'une minute !

---

### 🛠️ Option 2 : Configuration Manuel Locale

#### Prérequis
- **Python** : 3.10 ou supérieur
- **Node.js** : 18.x ou supérieur
- **PostgreSQL** : 14.x ou supérieur
- **Redis** : 6.x ou supérieur

---

### 1. Configuration du Backend

```bash
# Entrer dans le répertoire backend
cd backend

# Créer et activer l'environnement virtuel Python
python3 -m venv venv
source venv/bin/activate  # Sur Windows : venv\Scripts\activate

# Installer les dépendances
pip install -r requirements.txt

# Créer la configuration à partir du modèle
cp .env.example .env
# Éditer backend/.env pour configurer DATABASE_URL, REDIS_URL, R2, clés API
```

#### Initialiser la Base de Données & Données d'Amorçage

```bash
# Exécuter les migrations Alembic
alembic upgrade head

# Exécuter le script maître d'amorçage
python scripts/seed_all.py
```

#### Exécuter le Serveur de Développement FastAPI

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
- **Documentation API (Swagger UI)** : `http://localhost:8000/docs`

---

### 2. Configuration de Celery Worker (Tâches Asynchrones)

```bash
cd backend
source venv/bin/activate

# Démarrer le worker Celery pour les tâches de génération d'images et vidéos
celery -A app.celery_app worker --loglevel=info -c 4
```

---

### 3. Configuration du Frontend Web (Port 3000)

```bash
cd web

# Installer les dépendances
npm install

# Créer la configuration à partir du modèle
cp .env.example .env

# Démarrer le serveur de développement Nuxt 3
npm run dev
```
- **Application Web** : `http://localhost:3000`

---

### 4. Configuration du Panneau d'Administration (Port 3001)

```bash
cd admin

# Installer les dépendances
npm install

# Démarrer le serveur de développement du panneau d'administration
npm run dev
```
- **Panneau d'Administration** : `http://localhost:3001`
- **Identifiants par Défaut** : Créés via `python scripts/create_first_admin.py` (`admin` / `admin123`)

---

## 🚢 Gestion des Services & Déploiement en Production

VidGen inclut un **gestionnaire unifié de services systemd** prêt pour la production situé dans `systemd/` :

```bash
# Exécuter le gestionnaire de services interactif
chmod +x systemd/manage-services.sh
./systemd/manage-services.sh
```

Commandes de service disponibles :
- **`manage-services.sh status`** : Voir le statut en temps réel de Web, Admin, API Backend et Workers Celery.
- **`manage-services.sh start`** : Démarrer tous les services simultanément.
- **`manage-services.sh restart`** : Redémarrer tous les services proprement.
- **`deploy.sh`** : Script de déploiement automatique en production en un clic.

Pour des instructions détaillées de déploiement Nginx et aaPanel, consultez [docs/05-deployment/production-deployment.md](docs/05-deployment/production-deployment.md).

---

## 🛠️ Outils CLI de Maintenance

Le dossier `backend/scripts/` propose des scripts utilitaires pour la maintenance administrative :

```bash
# Ajouter des crédits à un compte utilisateur
python scripts/add_credits.py --email user@example.com --amount 1000

# Importer de nouveaux modèles d'IA dans la base de données
python scripts/import_models.py

# Mettre à jour les slugs et tags des œuvres
python scripts/update_url_slugs_from_titles.py
```

---

## 📄 Licence

Ce projet est sous licence open source **MIT**. Consultez le fichier [LICENSE](LICENSE) pour plus de détails.

---

## 🤝 Contributions & Communauté

Les contributions, signalements de problèmes et demandes de fonctionnalités sont les bienvenus !  
N'hésitez pas à ouvrir une Issue ou à soumettre une Pull Request.

*Si vous trouvez VidGen utile, donnez-nous une ⭐️ Star sur GitHub !*
