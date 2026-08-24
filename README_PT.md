<div align="center">

<img src="docs/assets/logo.png" alt="VidGen Logo" width="320" style="border-radius: 20px; box-shadow: 0 4px 20px rgba(0,0,0,0.15);" />

**Plataforma de geração de vídeo e imagem com IA open-source de nível de produção**

[![Live Demo](https://img.shields.io/badge/Demo_ao_Vivo-vidgenerator.ai-0070f3?style=for-the-badge&logo=google-chrome&logoColor=white)](https://vidgenerator.ai)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.11%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Nuxt 3](https://img.shields.io/badge/Nuxt-3.x-00DC82?style=for-the-badge&logo=nuxt.js&logoColor=white)](https://nuxt.com/)
[![FastAPI](https://img.shields.io/badge/FastAPI-Async-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![PRs Welcome](https://img.shields.io/badge/PRs-Bem--vindos-brightgreen.svg?style=for-the-badge)](.github/CONTRIBUTING.md)

[English](README.md) | [简体中文](README_CN.md) | [日本語](README_JA.md) | [한국어](README_KO.md) | [Español](README_ES.md) | [Português](README_PT.md)

</div>

<p align="center">
  <a href="https://vidgenerator.ai"><b>🚀 Demo ao Vivo</b></a> •
  <a href="#-principais-recursos"><b>✨ Recursos</b></a> •
  <a href="#️-stack-tecnológica"><b>🛠️ Stack Tecnológica</b></a> •
  <a href="#-início-rápido"><b>⚡ Início Rápido</b></a> •
  <a href="#-estrutura-do-repositório"><b>📁 Arquitetura</b></a>
</p>

---

> 🚀 **Demo ao Vivo e Testado em Produção Comercial (Battle-Tested)**: O VidGen alimenta a plataforma comercial ao vivo [vidgenerator.ai](https://vidgenerator.ai).

## 🌟 Visão Geral

**VidGen** é uma plataforma moderna, de alta performance e open-source para geração de imagens e vídeos com IA, projetada para criadores, desenvolvedores e empreendedores. Construída sobre uma arquitetura Monorepo limpa, o VidGen integra perfeitamente um portal web rápido SSR em Nuxt 3, um painel administrativo multilíngue em Nuxt 3 e um backend assíncrono em Python FastAPI alimentado por filas de tarefas Celery.

Quer você esteja lançando uma plataforma de geração de imagens/vídeos com IA ou construindo fluxos de trabalho personalizados, o VidGen oferece uma base sólida e testada em produção com monetização de créditos integrada, compartilhamento na comunidade, otimização SEO e moderação de conteúdo.

---

## ✨ Principais Recursos

### 🎨 Geração de IA Multimodal
- **Texto para Imagem (Text2Img)**: Gere imagens de alta resolução utilizando modelos de ponta (FLUX.1, SDXL, Midjourney).
- **Imagem para Imagem (Img2Img)**: Transforme imagens existentes com orientação de prompts personalizados e controle de intensidade.
- **Texto para Vídeo (Text2Video)**: Crie clipes de vídeo dinâmicos a partir de prompts de texto (HunyuanVideo, Luma, Pika, Runway).
- **Imagem para Vídeo (Img2Video)**: Anime fotos estáticas em vídeos de alta definição com controle de movimento.

### 🤖 Motor de Fluxo de Trabalho Multiproduto
- **Integração Flexível de IA**: Suporte nativo para SiliconFlow, Replicate, Gemini API e adaptadores de provedores personalizados.
- **Executor de Fluxo de Trabalho Baseado em Nós**: Execute fluxos de trabalho complexos de múltiplas etapas (`backend/app/services/workflow_executor.py`).
- **Fila de Tarefas Assíncronas**: Processador de tarefas Celery para trabalhos pesados de geração, evitando bloqueios na API.
- **Atualizações em Tempo Real**: Notificações de progresso transmitidas em tempo real via WebSocket e Redis Pub/Sub.

### 💰 Sistema de Monetização e Créditos
- **Meios de Pagamento**: Integração nativa com **PayPal** e **Stripe** para assinaturas globais e pacotes de créditos.
- **Economia de Créditos**: Dedução de créditos por uso com preços customizáveis por opção de modelo.
- **Motor de Descontos e Promoções**: Suporte para ofertas com desconto, códigos promocionais e pacotes de vendas especiais.
- **Recompensas de Check-in Diário**: Recurso interativo de check-in diário com multiplicadores por sequência e bônus de créditos.

### 🌐 Comunidade de Prompts e Recursos Sociais
- **Galeria de Exploração**: Layout estilo Masonry exibindo criações da comunidade, prompts, modelos utilizados e parâmetros de geração.
- **Perfis de Criadores**: Handles personalizados (`@username`), biografias, avatares e galerias pessoais.
- **Engajamento Social**: Curtir, favoritar, comentar em trabalhos e seguir criadores.
- **Páginas de SEO e Agregação**: Metadados SEO dinâmicos, gerador de sitemaps, páginas de agregação por tema (`/topic/...`), categorias (`/category/...`) e efeitos (`/effects/...`).

### 🔧 Painel Administrativo Completo
- **Suporte Multilíngue (i18n)**: Interface disponível em Inglês, Chinês, Japonês, Coreano, Espanhol e Português.
- **Gerador de Usuários Virtuais**: Crie usuários sintéticos realistas com `faker` e busca automática de avatares no Cloudflare R2.
- **Moderação de Conteúdo**: Filtro automático de imagens NSFW, gerenciador de léxico de palavras-chave sensíveis, gestão de denúncias e bloqueio de trabalhos.
- **Gestão de Modelos e Preços**: Configure modelos de IA, custos base de créditos, multiplicadores de opções e modelos de fluxo de trabalho sem fazer novo deploy.
- **Gestão Operacional**: Gerenciador de banners e carrosséis, editor de posts de blog e configurações do sistema.

---

## 🛠️ Stack Tecnológica

| Camada | Tecnologias |
| :--- | :--- |
| **Portal Web Frontend** | **Nuxt 3** (Vue 3, SSR/ISR), **Pinia**, **Tailwind CSS**, **Lucide Icons**, Axios, Socket.io |
| **Painel Administrativo** | **Nuxt 3** (Vue 3), **Tailwind CSS**, **Vue i18n** (6 idiomas), Axios |
| **API Backend** | **FastAPI** (Python 3.11+), **SQLAlchemy** (Async ORM), **Pydantic v2**, JWT |
| **Fila de Tarefas e Workers** | **Celery**, **Flower** (Monitoramento), **Redis** (Broker e Cache) |
| **Banco de Dados** | **PostgreSQL** 14+ com rastreamento de migrações **Alembic** |
| **Armazenamento e CDN** | **Cloudflare R2** / AWS S3 / Aliyun OSS (compatível com S3) |
| **Provedores de IA** | SiliconFlow, Replicate, Google Gemini, Adaptadores Personalizados |
| **Meios de Pagamento** | PayPal SDK, Stripe API |
| **Contêineres** | **Docker**, **Docker Compose** (Orquestração em um clique) |
| **Gestão de Serviços** | Suite de serviços **systemd** unificada (`systemd/`), Proxy Reverso Nginx |

---

## 📁 Estrutura do Repositório

```
vidgen/
├── web/                     # 🌐 Aplicação Web Frontend (Nuxt 3, Porta 3000)
│   ├── pages/               # Rotas de páginas (explorar, gerar, perfil, recarga, etc.)
│   ├── components/          # Componentes de UI reutilizáveis
│   ├── composables/         # Hooks composables personalizados
│   ├── stores/              # Lojas de estado Pinia
│   └── nuxt.config.ts       # Configuração do Nuxt 3
│
├── admin/                   # 🔧 Painel Administrativo (Nuxt 3, Porta 3001)
│   ├── pages/               # Rotas de admin (usuários, trabalhos, moderação, modelos, etc.)
│   ├── composables/         # Composables de API e i18n de admin (useAdminI18n.ts)
│   ├── locales/             # Dicionários de UI multilíngues (en.ts, pt.ts, etc.)
│   └── nuxt.config.ts
│
├── backend/                 # 🐍 API Backend e Motor Assíncrono (FastAPI, Porta 8000)
│   ├── app/
│   │   ├── main.py          # Ponto de entrada do FastAPI e registro de rotas
│   │   ├── celery_app.py    # Configuração da fila de tarefas Celery
│   │   ├── routes/          # Manipuladores de rotas de API (auth, works, generation, admin*.py)
│   │   ├── models/          # Modelos de banco de dados SQLAlchemy
│   │   ├── services/        # Serviços de Armazenamento, Email, Gemini, Moderação, Pagamentos
│   │   ├── tasks/           # Tarefas assíncronas de fluxo de trabalho no Celery
│   │   └── utils/           # Utilitários de i18n, Logger, Auth, Slug, Validação
│   ├── migrations/          # Scripts de migração de banco de dados Alembic
│   ├── scripts/             # Ferramentas CLI de inicialização e manutenção
│   └── requirements.txt     # Dependências do Python
│
├── systemd/                 # ⚙️ Scripts de Deploy e Gestão Unificada de Serviços
│   ├── deploy.sh            # Script de deploy automatizado
│   ├── manage-services.sh   # Gerenciador interativo de serviços systemd
│   └── *.service            # Arquivos de configuração de unidades de serviço
│
└── docs/                    # 📚 Documentação Técnica e Guias
    ├── AA_PANEL_DEPLOYMENT_GUIDE.md
    ├── SYSTEMD_UNIFIED_GUIDE.md
    └── ...
```

---

## ⚡ Início Rápido

### 🐳 Opção 1: Docker Compose em Um Clique (Recomendado)

Inicie toda a stack do VidGen (Web, Admin, Backend, Celery, Postgres, Redis) com um único comando:

```bash
# Clonar o repositório
git clone https://github.com/ucmao/vidgen.git
cd vidgen

# Iniciar todos os 6 serviços via Docker Compose
docker compose up -d
```

- 🌐 **Portal Web**: `http://localhost:3000`
- 🔧 **Painel Administrativo**: `http://localhost:3001` (Admin padrão: `admin` / Senha: `admin123`)
- 🐍 **Documentação da API (Swagger Docs)**: `http://localhost:8000/docs`

> 💡 **Dados Semente Automáticos (Seed Data)**: Ao iniciar o contêiner, o script `scripts/seed_all.py` roda automaticamente para migrar o banco, criar o superadministrador inicial, importar modelos de IA, pacotes de recarga e configurações SEO em menos de 1 minuto!

---

### 🛠️ Opção 2: Configuração Manual Local

#### Pré-requisitos
- **Python**: 3.11 ou superior
- **Node.js**: 18.x ou superior
- **PostgreSQL**: 14.x ou superior
- **Redis**: 6.x ou superior

---

### 1. Configuração do Backend

```bash
# Entrar no diretório do backend
cd backend

# Criar e ativar ambiente virtual do Python
python3 -m venv venv
source venv/bin/activate  # No Windows: venv\Scripts\activate

# Instalar dependências
pip install -r requirements.txt

# Criar configuração a partir do modelo
cp .env.example .env
# Editar backend/.env para configurar DATABASE_URL, REDIS_URL, R2, chaves de API
```

#### Inicializar Banco de Dados e Dados Semente

```bash
# Executar migrações do Alembic
alembic upgrade head

# Executar script mestre de sementes
python scripts/seed_all.py
```

#### Executar Servidor de Desenvolvimento FastAPI

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
- **Documentação da API (Swagger UI)**: `http://localhost:8000/docs`

---

### 2. Configuração do Celery Worker (Tarefas Assíncronas)

```bash
cd backend
source venv/bin/activate

# Iniciar worker do Celery para geração de imagens e vídeos
celery -A app.celery_app worker --loglevel=info -c 4
```

---

### 3. Configuração do Frontend Web (Porta 3000)

```bash
cd web

# Instalar dependências
npm install

# Criar configuração a partir do modelo
cp .env.example .env

# Iniciar servidor de desenvolvimento do Nuxt 3
npm run dev
```
- **Portal Web**: `http://localhost:3000`

---

### 4. Configuração do Painel Administrativo (Porta 3001)

```bash
cd admin

# Instalar dependências
npm install

# Iniciar servidor de desenvolvimento do Painel Administrativo
npm run dev
```
- **Painel Administrativo**: `http://localhost:3001`
- **Credenciais Padrão**: Criadas via `python scripts/create_first_admin.py` (`admin` / `admin123`)

---

## 🚢 Gestão de Serviços e Deploy em Produção

O VidGen inclui um **gerenciador unificado de serviços systemd** pronto para produção localizado em `systemd/`:

```bash
# Executar gerenciador interativo de serviços
chmod +x systemd/manage-services.sh
./systemd/manage-services.sh
```

Comandos disponíveis:
- **`manage-services.sh status`**: Ver status em tempo real da Web, Admin, Backend API e Workers do Celery.
- **`manage-services.sh start`**: Iniciar todos os serviços simultaneamente.
- **`manage-services.sh restart`**: Reiniciar todos os serviços de forma segura.
- **`deploy.sh`**: Script de deploy automatizado em produção em um clique.

Para instruções detalhadas de deploy no Nginx e aaPanel, consulte [docs/05-deployment/production-deployment.md](docs/05-deployment/production-deployment.md).

---

## 🛠️ Ferramentas CLI de Manutenção

A pasta `backend/scripts/` oferece scripts utilitários para manutenção administrativa:

```bash
# Adicionar créditos a uma conta de usuário
python scripts/add_credits.py --email usuario@exemplo.com --amount 1000

# Importar novos modelos de IA no banco de dados
python scripts/import_models.py

# Atualizar slugs e tags de trabalhos
python scripts/update_url_slugs_from_titles.py
```

---

## 📄 Licença

Este projeto é open-source sob a **Licença MIT**. Consulte o arquivo [LICENSE](LICENSE) para mais detalhes.

---

## 🤝 Contribuições e Comunidade

Contribuições, relatos de problemas e solicitações de recursos são muito bem-vindos!  
Sinta-se à vontade para abrir uma Issue ou enviar um Pull Request.

*Se você achar o VidGen útil, por favor nos dê uma ⭐️ Star no GitHub!*
