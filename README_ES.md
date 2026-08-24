<div align="center">

<img src="docs/assets/logo.png" alt="VidGen Logo" width="320" style="border-radius: 20px; box-shadow: 0 4px 20px rgba(0,0,0,0.15);" />

# VidGen 🎨⚡

**Plataforma de generación de video e imagen con IA de código abierto de grado de producción**

[![Live Demo](https://img.shields.io/badge/Demo_en_Vivo-vidgenerator.ai-0070f3?style=for-the-badge&logo=google-chrome&logoColor=white)](https://vidgenerator.ai)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Nuxt 3](https://img.shields.io/badge/Nuxt-3.x-00DC82?style=for-the-badge&logo=nuxt.js&logoColor=white)](https://nuxt.com/)
[![FastAPI](https://img.shields.io/badge/FastAPI-Async-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![PRs Welcome](https://img.shields.io/badge/PRs-Bienvenidos-brightgreen.svg?style=for-the-badge)](.github/CONTRIBUTING.md)

[English](README.md) | [简体中文](README_CN.md) | [日本語](README_JA.md) | [한국어](README_KO.md) | [Español](README_ES.md) | [Português](README_PT.md)

</div>

<p align="center">
  <a href="https://vidgenerator.ai"><b>🚀 Demo en Vivo</b></a> •
  <a href="#-características-principales"><b>✨ Características</b></a> •
  <a href="#️-stack-tecnológico"><b>🛠️ Stack Tecnológico</b></a> •
  <a href="#-inicio-rápido"><b>⚡ Inicio Rápido</b></a> •
  <a href="#-estructura-del-repositorio"><b>📁 Arquitectura</b></a>
</p>

---

> 🚀 **Demo en Vivo y Probado en Producción Commercial (Battle-Tested)**: VidGen impulsa la plataforma comercial en vivo [vidgenerator.ai](https://vidgenerator.ai).

## 🌟 Descripción General

**VidGen** es una plataforma moderna, de alto rendimiento y código abierto para la generación de imágenes y videos con IA, diseñada para creadores, desarrolladores y emprendedores. Construida sobre una arquitectura Monorepo limpia, VidGen combina sin problemas un portal web rápido SSR en Nuxt 3, un panel de administración multilingüe en Nuxt 3 y un backend asíncrono en Python FastAPI impulsado por colas de tareas Celery.

Ya sea que esté lanzando una plataforma de generación de imágenes/videos con IA o construyendo canalizaciones de flujo de trabajo personalizadas, VidGen proporciona una base sólida y probada en batalla con monetización de créditos integrada, intercambio comunitario, optimización SEO y moderación de contenido.

---

## ✨ Características Principales

### 🎨 Generación de IA Multimodal
- **Texto a Imagen (Text2Img)**: Genere imágenes de alta resolución utilizando modelos de vanguardia (FLUX.1, SDXL, Midjourney).
- **Imagen a Imagen (Img2Img)**: Transforme imágenes existentes con guía de prompts personalizados y parámetros de intensidad.
- **Texto a Video (Text2Video)**: Cree clips de video dinámicos a partir de prompts de texto (HunyuanVideo, Luma, Pika, Runway).
- **Imagen a Video (Img2Video)**: Anime fotos estáticas en videos de alta definición con control de movimiento.

### 🤖 Motor de Flujos de Trabajo Multiproveedor
- **Integración Flexible de IA**: Soporte integrado para SiliconFlow, Replicate, Gemini API y canalizaciones de proveedores personalizados.
- **Ejecutor de Flujo de Trabajo Basado en Nodos**: Ejecute flujos de trabajo complejos de múltiples pasos (`backend/app/services/workflow_executor.py`).
- **Cola de Tareas Asíncronas**: Procesador de tareas Celery para trabajos pesados de generación, evitando el bloqueo de hilos de API.
- **Actualizaciones en Tiempo Real**: Notificaciones de progreso transmitidas en tiempo real vía WebSocket y Redis Pub/Sub.

### 💰 Sistema de Monetización y Créditos
- **Pasarelas de Pago**: Integración nativa con **PayPal** y **Stripe** para suscripciones globales y paquetes de créditos.
- **Economía de Créditos**: Deducción de créditos de pago por uso con precios personalizables por opción de modelo.
- **Motor de Descuentos y Promociones**: Soporte para ofertas con descuento, códigos promocionales y paquetes de venta especiales.
- **Recompensas por Check-in Diario**: Función interactiva de check-in diario con multiplicadores por racha y créditos de bonificación.

### 🌐 Comunidad de Prompts y Funciones Sociales
- **Galería de Exploración**: Diseño Masonry que muestra creaciones de la comunidad, prompts, modelos utilizados y parámetros de generación.
- **Perfiles de Creadores**: Handles personalizados (`@username`), biografías, avatares y galerías personales.
- **Interacción Social**: Me gusta, favoritos, comentarios en trabajos y seguimiento de creadores.
- **Páginas de SEO y Agregación**: Metadatos SEO dinámicos, generador de sitemaps, páginas de agregación de temas (`/topic/...`), categorías (`/category/...`) y efectos (`/effects/...`).

### 🔧 Panel de Administración Completo
- **Soporte Multilingüe (i18n)**: Interfaz disponible en Inglés, Chino, Japonés, Coreano, Español y Portugués.
- **Generador de Usuarios Virtuales**: Cree usuarios sintéticos realistas con `faker` y recuperación automática de avatares en Cloudflare R2.
- **Moderación de Contenido**: Filtro automático de imágenes NSFW, administrador de léxico de palabras clave sensibles, gestión de reportes y bloqueo de trabajos.
- **Gestión de Modelos y Precios**: Configure modelos de IA, costos base de créditos, multiplicadores de opciones y plantillas de flujo de trabajo sin volver a desplegar.
- **Gestión Operativa**: Administrador de banners y carruseles, editor de entradas de blog y configuración del sistema.

---

## 🛠️ Stack Tecnológico

| Capa | Tecnologías |
| :--- | :--- |
| **Portal Web Frontend** | **Nuxt 3** (Vue 3, SSR/ISR), **Pinia**, **Tailwind CSS**, **Lucide Icons**, Axios, Socket.io |
| **Panel de Administración** | **Nuxt 3** (Vue 3), **Tailwind CSS**, **Vue i18n** (6 idiomas), Axios |
| **API Backend** | **FastAPI** (Python 3.10+), **SQLAlchemy** (Async ORM), **Pydantic v2**, JWT |
| **Cola de Tareas y Workers** | **Celery**, **Flower** (Monitoreo), **Redis** (Broker y Caché) |
| **Base de Datos** | **PostgreSQL** 14+ con rastreo de migraciones **Alembic** |
| **Almacenamiento y CDN** | **Cloudflare R2** / AWS S3 / Aliyun OSS (compatible con S3) |
| **Proveedores de IA** | SiliconFlow, Replicate, Google Gemini, Adaptadores Personalizados |
| **Pasarelas de Pago** | PayPal SDK, Stripe API |
| **Contenedores** | **Docker**, **Docker Compose** (Orquestación en un solo clic) |
| **Gestión de Servicios** | Suite de servicios **systemd** unificada (`systemd/`), Proxy Inverso Nginx |

---

## 📁 Estructura del Repositorio

```
vidgen/
├── web/                     # 🌐 Aplicación Web Frontend (Nuxt 3, Puerto 3000)
│   ├── pages/               # Rutas de páginas (explorar, generar, perfil, recarga, etc.)
│   ├── components/          # Componentes de UI reutilizables
│   ├── composables/         # Hooks composables personalizados
│   ├── stores/              # Tiendas de estado Pinia
│   └── nuxt.config.ts       # Configuración de Nuxt 3
│
├── admin/                   # 🔧 Panel de Administración (Nuxt 3, Puerto 3001)
│   ├── pages/               # Rutas de admin (usuarios, trabajos, moderación, modelos, etc.)
│   ├── composables/         # Composables de API e i18n de admin (useAdminI18n.ts)
│   ├── locales/             # Diccionarios de UI multilingües (en.ts, es.ts, etc.)
│   └── nuxt.config.ts
│
├── backend/                 # 🐍 API Backend y Motor Asíncrono (FastAPI, Puerto 8000)
│   ├── app/
│   │   ├── main.py          # Punto de entrada de FastAPI y registro de rutas
│   │   ├── celery_app.py    # Configuración de cola de tareas Celery
│   │   ├── routes/          # Manejadores de rutas de API (auth, works, generation, admin*.py)
│   │   ├── models/          # Modelos de base de datos SQLAlchemy
│   │   ├── services/        # Servicios de Almacenamiento, Email, Gemini, Moderación, Pagos
│   │   ├── tasks/           # Tareas asíncronas de flujo de trabajo en Celery
│   │   └── utils/           # Utilidades de i18n, Logger, Auth, Slug, Validación
│   ├── migrations/          # Scripts de migración de base de datos Alembic
│   ├── scripts/             # Herramientas CLI de inicialización y mantenimiento
│   └── requirements.txt     # Dependencias de Python
│
├── systemd/                 # ⚙️ Scripts de Despliegue y Gestión Unificada de Servicios
│   ├── deploy.sh            # Script de despliegue automatizado
│   ├── manage-services.sh   # Gestor interactivo de servicios systemd
│   └── *.service            # Archivos de configuración de unidades de servicio
│
└── docs/                    # 📚 Documentación Técnica y Guías
    ├── AA_PANEL_DEPLOYMENT_GUIDE.md
    ├── SYSTEMD_UNIFIED_GUIDE.md
    └── ...
```

---

## ⚡ Inicio Rápido

### 🐳 Opción 1: Docker Compose en un Clic (Recomendado)

Inicie todo el stack de VidGen (Web, Admin, Backend, Celery, Postgres, Redis) con un solo comando:

```bash
# Clonar el repositorio
git clone https://github.com/ucmao/vidgen.git
cd vidgen

# Iniciar los 6 servicios mediante Docker Compose
docker compose up -d
```

- 🌐 **Portal Web**: `http://localhost:3000`
- 🔧 **Panel de Administración**: `http://localhost:3001` (Admin por defecto: `admin` / Contraseña: `admin123`)
- 🐍 **Documentación API (Swagger Docs)**: `http://localhost:8000/docs`

> 💡 **Datos Semilla Automáticos (Seed Data)**: Al iniciar el contenedor, `scripts/seed_all.py` se ejecuta automáticamente para migrar el esquema, crear el superadministrador inicial, importar modelos de IA, paquetes de recarga y ajustes SEO en menos de 1 minuto.

---

### 🛠️ Opción 2: Configuración Manual Local

#### Requisitos Previos
- **Python**: 3.10 o superior
- **Node.js**: 18.x o superior
- **PostgreSQL**: 14.x o superior
- **Redis**: 6.x o superior

---

### 1. Configuración del Backend

```bash
# Entrar al directorio del backend
cd backend

# Crear y activar el entorno virtual de Python
python3 -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Crear configuración desde la plantilla
cp .env.example .env
# Editar backend/.env para configurar DATABASE_URL, REDIS_URL, R2, claves de API
```

#### Inicializar Base de Datos y Datos Semilla

```bash
# Ejecutar migraciones de Alembic
alembic upgrade head

# Ejecutar script maestro de semillas
python scripts/seed_all.py
```

#### Ejecutar Servidor de Desarrollo FastAPI

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
- **Documentación API (Swagger UI)**: `http://localhost:8000/docs`

---

### 2. Configuración de Celery Worker (Tareas Asíncronas)

```bash
cd backend
source venv/bin/activate

# Iniciar worker de Celery para generación de imágenes y videos
celery -A app.celery_app worker --loglevel=info -c 4
```

---

### 3. Configuración del Frontend Web (Puerto 3000)

```bash
cd web

# Instalar dependencias
npm install

# Crear configuración desde la plantilla
cp .env.example .env

# Iniciar servidor de desarrollo de Nuxt 3
npm run dev
```
- **Portal Web**: `http://localhost:3000`

---

### 4. Configuración del Panel de Administración (Puerto 3001)

```bash
cd admin

# Instalar dependencias
npm install

# Iniciar servidor de desarrollo del Panel de Administración
npm run dev
```
- **Panel de Administración**: `http://localhost:3001`
- **Credenciales por Defecto**: Creadas vía `python scripts/create_first_admin.py` (`admin` / `admin123`)

---

## 🚢 Gestión de Servicios y Despliegue en Producción

VidGen incluye un **gestor unificado de servicios systemd** listo para producción ubicado en `systemd/`:

```bash
# Ejecutar gestor interactivo de servicios
chmod +x systemd/manage-services.sh
./systemd/manage-services.sh
```

Comandos disponibles:
- **`manage-services.sh status`**: Ver estado en tiempo real de Web, Admin, Backend API y Workers de Celery.
- **`manage-services.sh start`**: Iniciar todos los servicios simultáneamente.
- **`manage-services.sh restart`**: Reiniciar todos los servicios de forma segura.
- **`deploy.sh`**: Script de despliegue automatizado en producción con un solo clic.

Para instrucciones detalladas de despliegue en Nginx y aaPanel, consulte [docs/05-deployment/production-deployment.md](docs/05-deployment/production-deployment.md).

---

## 🛠️ Herramientas CLI de Mantenimiento

La carpeta `backend/scripts/` ofrece scripts de utilidad para mantenimiento administrativo:

```bash
# Añadir créditos a una cuenta de usuario
python scripts/add_credits.py --email usuario@ejemplo.com --amount 1000

# Importar nuevos modelos de IA en la base de datos
python scripts/import_models.py

# Actualizar slugs y etiquetas de trabajos
python scripts/update_url_slugs_from_titles.py
```

---

## 📄 Licencia

Este proyecto es de código abierto bajo la **Licencia MIT**. Consulte el archivo [LICENSE](LICENSE) para más detalles.

---

## 🤝 Contribuciones y Comunidad

¡Las contribuciones, reportes de problemas y solicitudes de funciones son bienvenidas!  
Síntase libre de abrir un Issue o enviar un Pull Request.

*Si encuentra útil VidGen, ¡por favor denos una ⭐️ Star en GitHub!*
