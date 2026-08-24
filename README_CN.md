<div align="center">

<img src="docs/assets/logo.png" alt="VidGen Logo" width="320" style="border-radius: 20px; box-shadow: 0 4px 20px rgba(0,0,0,0.15);" />

# VidGen 🎨⚡

**生产级开源 AI 视频与图像生成平台**

[![Live Demo](https://img.shields.io/badge/在线演示-vidgenerator.ai-0070f3?style=for-the-badge&logo=google-chrome&logoColor=white)](https://vidgenerator.ai)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Nuxt 3](https://img.shields.io/badge/Nuxt-3.x-00DC82?style=for-the-badge&logo=nuxt.js&logoColor=white)](https://nuxt.com/)
[![FastAPI](https://img.shields.io/badge/FastAPI-Async-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![PRs Welcome](https://img.shields.io/badge/PRs-欢迎贡献-brightgreen.svg?style=for-the-badge)](.github/CONTRIBUTING.md)

[English](README.md) | [简体中文](README_CN.md) | [日本語](README_JA.md) | [한국어](README_KO.md) | [Español](README_ES.md) | [Português](README_PT.md) | [Deutsch](README_DE.md) | [Français](README_FR.md)

</div>

<p align="center">
  <a href="https://vidgenerator.ai"><b>🚀 在线演示</b></a> •
  <a href="#-核心功能亮点"><b>✨ 核心功能</b></a> •
  <a href="#-技术栈一览"><b>🛠️ 技术栈</b></a> •
  <a href="#-快速启动指南"><b>⚡ 快速开始</b></a> •
  <a href="#-目录结构"><b>📁 目录结构</b></a>
</p>

---

> 🚀 **在线商业化验证（Battle-Tested）**：VidGen 为真实线上运营项目 [vidgenerator.ai](https://vidgenerator.ai) 提供核心系统支持。

## 🌟 项目简介

**VidGen** 是一款面向创作者、开发者与创业者的高性能开源 AI 视频与图像生成平台。项目基于清晰的 Monorepo 单体多应用架构设计，完美融合了 Nuxt 3 高并发 SSR 前端门户、中英文双语 Nuxt 3 管理后台以及基于 Celery 异步任务队列的 Python FastAPI 后端。

无论您是打算上线商业化 AI 图片/视频生成平台，还是构建自定义 AI 工作流，VidGen 均提供了包含积分充值变现、社区分享、SEO 深度优化、内容安全审核等开箱即用的生产级完整解决方案。

---

## ✨ 核心功能亮点

### 🎨 多模态 AI 生成引擎
- **文生图 (Text-to-Image)**：支持 FLUX.1、SDXL、Midjourney 等先进模型，一键生成超高清图像。
- **图生图 (Image-to-Image)**：上传参考图结合 Prompt 引导词与相似度控制，实现图像重绘与风格转换。
- **文生视频 (Text-to-Video)**：支持 HunyuanVideo、Luma、Pika、Runway 等动态视频生成。
- **图生视频 (Image-to-Video)**：将静态照片一键转化为高帧率动态视频，支持运动幅度微调。

### 🤖 多厂商工作流与异步队列
- **多厂商 API 适配**：内置 SiliconFlow（硅基流动）、Replicate、Gemini API 以及自定义 Provider 拓展机制。
- **节点化工作流引擎**：支持复杂多步骤 AI 工作流的编排与执行 (`backend/app/services/workflow_executor.py`)。
- **Celery 异步任务队列**：耗时视频/大图生成任务完全解耦异步化，防止阻塞 API 响应线程。
- **WebSocket 实时状态推送**：通过 Redis Pub/Sub 与 WebSocket 技术，实时推送作品生成进度。

### 💰 商业化积分与支付变现
- **全球主流支付集成**：原生集成 **PayPal** 与 **Stripe** 支付网关，支持全球化订阅与积分套餐购买。
- **按量积分扣减**：支持针对不同模型、参数选项动态设定积分消耗。
- **折扣与促销引擎**：支持活动横幅、充值折扣优惠卷、促销套餐配置。
- **每日签到奖励系统**：支持连续签到阶梯奖励与倍率加成 (`CHECKIN_FEATURE.md`)。

### 🌐 社区广场与社交生态
- **探索画廊**：瀑布流展示社区优秀作品，公开 Prompt 提示词、生成参数与使用模型。
- **创作者主页**：支持自定义 Handle 域名 (`@username`)、个人简介、头像与个人作品集展示。
- **社交互动**：点赞、收藏、作品评论与创作者关注系统。
- **SEO 深度优化**：动态 Meta 标签、自动 Sitemap 生成、专题聚合页 (`/topic/...`)、分类页 (`/category/...`) 与特效页 (`/effects/...`)。

### 🔧 功能强大的管理后台 (Admin)
- **中英文双语支持**：首次安装默认纯英文，支持顶栏一键切换中文/英文 (`English` / `中文`)。
- **马甲账号虚拟生成器**：基于 `faker` 库与 Cloudflare R2 头像抓取，一键批量生成高真实感虚拟用户。
- **内容安全审核系统**：自动 NSFW 违规图像识别、敏感词库过滤、用户举报处理与一键封禁。
- **模型与定价管理**：可视化配置 AI 模型状态、基础积分、参数加价与工作流模板。
- **运营工具**：首页 Banner 与轮播图管理、博客文章编辑器与全站配置。

---

## 🛠️ 技术栈一览

| 架构层级 | 技术选型 |
| :--- | :--- |
| **前台 Web** | **Nuxt 3** (Vue 3, SSR/ISR), **Pinia**, **Tailwind CSS**, **Lucide Icons**, Axios, Socket.io |
| **管理后台 Admin** | **Nuxt 3** (Vue 3), **Tailwind CSS**, **Vue i18n** (中英双语), Axios |
| **后端 API** | **FastAPI** (Python 3.10+), **SQLAlchemy** (Async ORM), **Pydantic v2**, JWT |
| **任务队列与监控** | **Celery**, **Flower** (队列监控), **Redis** (Broker & 缓存) |
| **数据库** | **PostgreSQL** 14+ , **Alembic** 版本迁移工具 |
| **存储与 CDN** | **Cloudflare R2** / AWS S3 / 阿里云 OSS (兼容 S3 协议) |
| **AI 服务商** | SiliconFlow, Replicate, Google Gemini, 自定义 Adapter |
| **支付网关** | PayPal SDK, Stripe API |
| **容器化编排** | **Docker**, **Docker Compose** (一键全栈容器编排) |
| **运维与部署** | 统一 **systemd** 服务管理器 (`systemd/`), Nginx 反向代理 |

---

## 📁 目录结构

```
vidgen/
├── web/                     # 🌐 前台 Web 应用 (Nuxt 3, 端口 3000)
│   ├── pages/               # 页面路由 (探索、生成、个人中心、充值等)
│   ├── components/          # 可复用 Vue 组件
│   ├── composables/         # 自定义 Composable 钩子
│   ├── stores/              # Pinia 状态管理
│   └── nuxt.config.ts       # Nuxt 3 配置文件
│
├── admin/                   # 🔧 管理后台应用 (Nuxt 3, 端口 3001)
│   ├── pages/               # 后台路由 (用户管理、作品管理、审核、模型等)
│   ├── composables/         # API 与 i18n 钩子 (useAdminI18n.ts)
│   ├── locales/             # 中英文双语语言包 (en.ts, zh.ts)
│   └── nuxt.config.ts
│
├── backend/                 # 🐍 后端 API 与异步引擎 (FastAPI, 端口 8000)
│   ├── app/
│   │   ├── main.py          # FastAPI 主入口与路由注册
│   │   ├── celery_app.py    # Celery 任务队列配置
│   │   ├── routes/          # 接口路由 (auth, works, generation, admin*.py)
│   │   ├── models/          # SQLAlchemy 数据库模型
│   │   ├── services/        # 存储、邮件、Gemini、审核、支付等核心服务
│   │   ├── tasks/           # Celery 异步生成任务
│   │   └── utils/           # i18n、日志、鉴权、 Slug 生成等工具类
│   ├── migrations/          # Alembic 数据库版本迁移脚本
│   ├── scripts/             # 系统初始化与日常维护命令行工具
│   └── requirements.txt     # Python 依赖清单
│
├── systemd/                 # ⚙️ 统一服务管理与部署脚本
│   ├── deploy.sh            # 自动化部署脚本
│   ├── manage-services.sh   # 交互式 systemd 服务管理器
│   └── *.service            # systemd 服务配置文件
│
└── docs/                    # 📚 技术开发与部署文档
    ├── AA_PANEL_DEPLOYMENT_GUIDE.md
    ├── SYSTEMD_UNIFIED_GUIDE.md
    └── ...
```

---

## ⚡ 快速启动指南

### 🐳 方式一：一键 Docker Compose 启动（推荐）

通过单条命令即可一键构建并启动全套 VidGen 服务（前端 Web、管理后台 Admin、FastAPI 后端 API、Celery Worker 异步任务、PostgreSQL 数据库及 Redis）：

```bash
# 克隆项目仓库
git clone https://github.com/ucmao/vidgen.git
cd vidgen

# 一键启动全套 6 大服务容器
docker compose up -d
```

- 🌐 **Web 前端**: `http://localhost:3000`
- 🔧 **Admin 管理后台**: `http://localhost:3001` (默认管理员账号: `admin` / 密码: `admin123`)
- 🐍 **后端 API 文档 (Swagger UI)**: `http://localhost:8000/docs`

> 💡 **自动种子数据（Seed Data）**：容器启动时会自动运行 `scripts/seed_all.py`，1 分钟内自动完成数据库 Migration、初始超级管理员创建、预置 AI 模型导入、积分充值套餐与全站 SEO 配置初始化！

---

### 🛠️ 方式二：本地手动安装部署

#### 环境准备
- **Python**: 3.10 或更高版本
- **Node.js**: 18.x 或更高版本
- **PostgreSQL**: 14.x 或更高版本
- **Redis**: 6.x 或更高版本

---

### 1. 启动后端 API (端口 8000)

```bash
# 进入后端目录
cd backend

# 创建并激活 Python 虚拟环境
python3 -m venv venv
source venv/bin/activate  # Windows 环境: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 创建环境配置文件
cp .env.example .env
# 编辑 backend/.env，配置数据库、Redis、R2 秘钥及 AI API Keys
```

#### 初始化数据库与基础数据

```bash
# 执行 Alembic 数据库迁移
alembic upgrade head

# 执行脚本文档初始化基础数据
python scripts/init_database.py
python scripts/create_first_admin.py
python scripts/init_seo_config.py
python scripts/init_recharge_packages.py
```

#### 启动 FastAPI 服务

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
- **API 交互文档 (Swagger UI)**: `http://localhost:8000/docs`

---

### 2. 启动 Celery 异步任务队列

```bash
cd backend
source venv/bin/activate

# 启动 Celery Worker 监听图片与视频异步生成任务
celery -A app.celery_app worker --loglevel=info -c 4
```

---

### 3. 启动前台 Web 应用 (端口 3000)

```bash
cd web

# 安装依赖
npm install

# 创建配置文件
cp .env.example .env
# 编辑 web/.env，确保 NUXT_PUBLIC_API_BASE_URL 指向 http://localhost:8000

# 启动开发服务器
npm run dev
```
- **前台 Web 应用**: `http://localhost:3000`

---

### 4. 启动管理后台 Admin (端口 3001)

```bash
cd admin

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```
- **管理后台**: `http://localhost:3001`
- **默认管理员**: 通过 `python scripts/create_first_admin.py` 创建

---

## 🚢 生产环境部署与运维

VidGen 提供了开箱即用的 **systemd 统一服务管理器** (`systemd/`):

```bash
# 运行交互式运维脚本
chmod +x systemd/manage-services.sh
./systemd/manage-services.sh
```

常用命令：
- **`manage-services.sh status`**：查看 Web、Admin、Backend API 和 Celery 实时运行状态。
- **`manage-services.sh start`**：一键启动所有后台服务。
- **`manage-services.sh restart`**：平滑重启所有服务。
- **`deploy.sh`**：一键生产部署与拉取更新脚本。

关于详细的 Nginx 配置与宝塔/aaPanel 面板部署教程，请参阅文档：[docs/05-deployment/production-deployment.md](docs/05-deployment/production-deployment.md)。

---

## 🛠️ CLI 运维工具

`backend/scripts/` 目录下提供了丰富的后台管理命令行工具：

```bash
# 为指定账户手动充值积分
python scripts/add_credits.py --email user@example.com --amount 1000

# 导入新的 AI 模型配置
python scripts/import_models.py

# 补全历史作品的标签与 URL Slug
python scripts/update_url_slugs_from_titles.py
```

---

## 📄 开源许可证

本项目基于 **MIT License** 协议开源。详见 [LICENSE](LICENSE) 文件。

---

## 🤝 贡献与社区

欢迎提交 Issue 或 Pull Request 来完善项目！  
如果 VidGen 对您的项目有所帮助，欢迎在 GitHub 上点个 ⭐️ **Star** 支持一下！
