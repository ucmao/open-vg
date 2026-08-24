<div align="center">

<img src="docs/assets/logo.png" alt="VidGen Logo" width="320" style="border-radius: 20px; box-shadow: 0 4px 20px rgba(0,0,0,0.15);" />

**상용 환경을 위한 오픈소스 AI 비디오 및 이미지 생성 플랫폼**

[![Live Demo](https://img.shields.io/badge/라이브데모-vidgenerator.ai-0070f3?style=for-the-badge&logo=google-chrome&logoColor=white)](https://vidgenerator.ai)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.11%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Nuxt 3](https://img.shields.io/badge/Nuxt-3.x-00DC82?style=for-the-badge&logo=nuxt.js&logoColor=white)](https://nuxt.com/)
[![FastAPI](https://img.shields.io/badge/FastAPI-Async-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![PRs Welcome](https://img.shields.io/badge/PRs-환영합니다-brightgreen.svg?style=for-the-badge)](.github/CONTRIBUTING.md)

[English](README.md) | [简体中文](README_CN.md) | [日本語](README_JA.md) | [한국어](README_KO.md) | [Español](README_ES.md) | [Português](README_PT.md)

</div>

<p align="center">
  <a href="https://vidgenerator.ai"><b>🚀 라이브 데모</b></a> •
  <a href="#-핵심-기능"><b>✨ 핵심 기능</b></a> •
  <a href="#️-기술-스택-일람"><b>🛠️ 기술 스택</b></a> •
  <a href="#-빠른-시작-가이드"><b>⚡ 빠른 시작</b></a> •
  <a href="#-디렉터리-구조"><b>📁 디렉터리 구조</b></a>
</p>

---

> 🚀 **상용화 검증 완료 (Battle-Tested)**: VidGen은 실제 운영 서비스인 [vidgenerator.ai](https://vidgenerator.ai)의 핵심 엔진으로 활용되고 있습니다.

## 🌟 프로젝트 소개

**VidGen**은 크리에이터, 개발자 및 창업가를 위해 설계된 고성능 오픈소스 AI 비디오 및 이미지 생성 플랫폼입니다. 세련된 모노레포(Monorepo) 아키텍처를 기반으로 설계되었으며, Nuxt 3 기반의 고성능 SSR 유저 포털, 다국어를 지원하는 Nuxt 3 어드민 패널, Celery 비동기 작업 큐를 갖춘 Python FastAPI 백엔드를 완벽하게 통합했습니다.

상용 AI 이미지/비디오 생성 플랫폼의 신규 론칭이나 커스텀 AI 워크플로 구축 등, VidGen은 크레딧 결제, 구독, 커뮤니티 공유, SEO 최적화, 콘텐츠 감수 등 상용 서비스에 필요한 모든 핵심 기능을 기본으로 제공합니다.

---

## ✨ 핵심 기능

### 🎨 멀티 모달 AI 생성 엔진
- **텍스트 기반 이미지 생성 (Text2Img)**: FLUX.1, SDXL, Midjourney 등 최신 모델을 활용한 초고화질 이미지 생성.
- **이미지 기반 이미지 생성 (Img2Img)**: 원본 이미지, 프롬프트 프롬프트 및 유사도 제어를 통한 이미지 변환 및 스타일 재구성.
- **텍스트 기반 비디오 생성 (Text2Video)**: HunyuanVideo, Luma, Pika, Runway 등을 활용한 동적 비디오 클립 생성.
- **이미지 기반 비디오 생성 (Img2Video)**: 정적인 사진을 고프레임의 동적 비디오로 일괄 변환 (모션 크기 미세 조정 지원).

### 🤖 멀티 벤더 워크플로 및 비동기 작업 큐
- **멀티 벤더 API 호환**: SiliconFlow, Replicate, Google Gemini API 및 커스텀 Provider 확장 메커니즘 내장.
- **노드 기반 워크플로 엔진**: 복잡한 다단계 AI 워크플로의 시각적 구성 및 실행 (`backend/app/services/workflow_executor.py`).
- **Celery 비동기 작업 큐**: 시간이 오래 걸리는 비디오/대형 이미지 생성 작업을 완전 비동기화하여 API 스레드 차단 방지.
- **WebSocket 실시간 상태 알림**: Redis Pub/Sub 및 WebSocket 기술을 통해 생성 진행 상황을 실시간 스트리밍.

### 💰 수익화 및 크레딧 결제 시스템
- **글로벌 결제 통합**: **PayPal** 및 **Stripe** 결제 게이트웨이 표준 통합. 글로벌 구독 및 크레딧 패키지 구매 지원.
- **종량제 크레딧 차감**: 모델 및 파라미터 옵션별로 동적 크레딧 소모량 설정 지원.
- **할인 및 프로모션 엔진**: 이벤트 배너, 충전 할인 쿠폰, 프로모션 패키지 설정 지원.
- **일일 출석 체크 보상**: 연속 출석에 따른 계단식 보상 및 배율 가산 시스템.

### 🌐 프롬프트 커뮤니티 및 소셜 기능
- **탐색 갤러리**: 커뮤니티 우수 작품, 공개 프롬프트, 사용 모델, 생성 파라미터를 폭포수(Masonry) 레이아웃으로 전시.
- **크리에이터 마이페이지**: 커스텀 핸들명 (`@username`), 프로필, 아바타 및 개인 작품집 전시.
- **소셜 상호작용**: 좋아요, 즐겨찾기, 작품 댓글 및 크리에이터 팔로우 기능.
- **SEO 심층 최적화**: 동적 Meta 태그, 자동 Sitemap 생성, 기획전 페이지 (`/topic/...`), 카테고리 페이지 (`/category/...`), 이펙트 페이지 (`/effects/...`).

### 🔧 고기능 어드민 패널 (Admin Panel)
- **다국어 (i18n) 지원**: 영어, 중국어, 일본어, 한국어, 스페인어, 포르투갈어 6개 국어 전환 지원.
- **가상 계정(Sockpuppet) 생성기**: `faker` 라이브러리와 Cloudflare R2 아바타 수집을 통해 실제와 같은 가상 유저 일괄 생성.
- **콘텐츠 세이프티 및 감수**: NSFW 이미지 자동 판정, 금칙어 키워드 필터, 유저 신고 처리 및 계정 제재.
- **모델 및 가격 관리**: AI 모델 활성화 상태, 기본 크레딧 소모, 옵션 가산, 워크플로 템플릿을 코드 수정 없이 비주얼 설정.
- **운영 툴**: 배너 및 캐러셀 슬라이더 관리, 블로그 게시글 에디터, 전반 시스템 설정.

---

## 🛠️ 기술 스택 일람

| 아키텍처 계층 | 기술 선정 |
| :--- | :--- |
| **프론트엔드 Web** | **Nuxt 3** (Vue 3, SSR/ISR), **Pinia**, **Tailwind CSS**, **Lucide Icons**, Axios, Socket.io |
| **어드민 패널 Admin** | **Nuxt 3** (Vue 3), **Tailwind CSS**, **Vue i18n** (6개 국어 지원), Axios |
| **백엔드 API** | **FastAPI** (Python 3.11+), **SQLAlchemy** (Async ORM), **Pydantic v2**, JWT |
| **작업 큐 및 모니터링** | **Celery**, **Flower** (큐 모니터링), **Redis** (Broker & 캐시) |
| **데이터베이스** | **PostgreSQL** 14+ , **Alembic** 데이터베이스 마이그레이션 관리 |
| **스토리지 및 CDN** | **Cloudflare R2** / AWS S3 / Aliyun OSS (S3 호환 오브젝트 스토리지) |
| **AI 프로바이더** | SiliconFlow, Replicate, Google Gemini, 커스텀 Adapter |
| **결제 게이트웨이** | PayPal SDK, Stripe API |
| **컨테이너 오케스트레이션** | **Docker**, **Docker Compose** (전체 스택 일괄 컨테이너 구동) |
| **운영 및 배포** | 통합 **systemd** 서비스 매니저 (`systemd/`), Nginx 리버스 프록시 |

---

## 📁 디렉터리 구조

```
vidgen/
├── web/                     # 🌐 프론트엔드 Web 애플리케이션 (Nuxt 3, 포트 3000)
│   ├── pages/               # 페이지 라우팅 (탐색, 생성, 마이페이지, 충전 등)
│   ├── components/          # 재사용 가능한 Vue 컴포넌트
│   ├── composables/         # 커스텀 Composable 훅
│   ├── stores/              # Pinia 상태 관리
│   └── nuxt.config.ts       # Nuxt 3 설정 파일
│
├── admin/                   # 🔧 어드민 패널 애플리케이션 (Nuxt 3, 포트 3001)
│   ├── pages/               # 어드민 라우팅 (유저 관리, 작품 관리, 감수, 모델 등)
│   ├── composables/         # API 및 i18n 훅 (useAdminI18n.ts)
│   ├── locales/             # 6개 국어 사전 파일 (en.ts, zh.ts, ko.ts 등)
│   └── nuxt.config.ts
│
├── backend/                 # 🐍 백엔드 API 및 비동기 엔진 (FastAPI, 포트 8000)
│   ├── app/
│   │   ├── main.py          # FastAPI 엔트리포인트 및 라우터 등록
│   │   ├── celery_app.py    # Celery 작업 큐 설정
│   │   ├── routes/          # API 라우팅 (auth, works, generation, admin*.py)
│   │   ├── models/          # SQLAlchemy 데이터베이스 모델
│   │   ├── services/        # 스토리지, 이메일, Gemini, 감수, 결제 등 핵심 서비스
│   │   ├── tasks/           # Celery 비동기 작업
│   │   └── utils/           # i18n, 로거, 인증, Slug 생성 등 유틸리티
│   ├── migrations/          # Alembic DB 마이그레이션 스크립트
│   ├── scripts/             # 시스템 초기화 및 유지보수 CLI 툴
│   └── requirements.txt     # Python 의존성 리스트
│
├── systemd/                 # ⚙️ 통합 서비스 관리 및 배포 스크립트
│   ├── deploy.sh            # 자동 배포 스크립트
│   ├── manage-services.sh   # 대화형 systemd 서비스 매니저
│   └── *.service            # systemd 서비스 설정 파일
│
└── docs/                    # 📚 기술 개발 및 배포 문서
    ├── AA_PANEL_DEPLOYMENT_GUIDE.md
    ├── SYSTEMD_UNIFIED_GUIDE.md
    └── ...
```

---

## ⚡ 빠른 시작 가이드

### 🐳 방법 1: Docker Compose 실행 (권장)

단 한 줄의 명령어 전체 VidGen 서비스(Web, Admin, FastAPI Backend, Celery Worker, PostgreSQL, Redis)를 일괄 구동합니다:

```bash
# 리포지토리 클론
git clone https://github.com/ucmao/vidgen.git
cd vidgen

# 전체 6개 서비스 컨테이너 일괄 구동
docker compose up -d
```

- 🌐 **웹 포털**: `http://localhost:3000`
- 🔧 **어드민 패널**: `http://localhost:3001` (초기 관리자: `admin` / 비밀번호: `admin123`)
- 🐍 **API 문서 (Swagger UI)**: `http://localhost:8000/docs`

> 💡 **자동 시드 데이터 (Seed Data)**: 컨테이너 실행 시 `scripts/seed_all.py`가 자동 실행되어 1분 이내에 DB 마이그레이션, 관리자 생성, AI 모델 임포트, 충전 패키지 및 SEO 설정이 자동 초기화됩니다.

---

### 🛠️ 방법 2: 로컬 소스 직접 실행

#### 환경 요구사항
- **Python**: 3.11 이상
- **Node.js**: 18.x 이상
- **PostgreSQL**: 14.x 이상
- **Redis**: 6.x 이상

---

### 1. 백엔드 설정

```bash
# backend 디렉터리로 이동
cd backend

# Python 가상 환경 생성 및 활성화
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 의존성 패키지 설치
pip install -r requirements.txt

# 환경 설정 파일 생성
cp .env.example .env
# backend/.env 파일에서 DATABASE_URL, REDIS_URL, R2 정보 등 설정
```

#### 데이터베이스 초기화 및 시드 데이터 주입

```bash
# Alembic 마이그레이션 실행
alembic upgrade head

# CLI 초기화 스크립트 실행
python scripts/seed_all.py
```

#### FastAPI 개발 서버 실행

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
- **API 문서**: `http://localhost:8000/docs`

---

### 2. Celery Worker 실행 (비동기 작업 처리)

```bash
cd backend
source venv/bin/activate

# 비디오 및 이미지 생성 작업용 Celery 워커 실행
celery -A app.celery_app worker --loglevel=info -c 4
```

---

### 3. 프론트엔드 Web 애플리케이션 실행 (포트 3000)

```bash
cd web

# 의존성 패키지 설치
npm install

# 환경 설정 파일 생성
cp .env.example .env

# Nuxt 3 개발 서버 실행
npm run dev
```
- **웹 포털**: `http://localhost:3000`

---

### 4. 어드민 패널 Admin 실행 (포트 3001)

```bash
cd admin

# 의존성 패키지 설치
npm install

# 어드민 패널 개발 서버 실행
npm run dev
```
- **어드민 패널 Admin**: `http://localhost:3001`
- **초기 로그인 계정**: `python scripts/create_first_admin.py`로 생성된 계정 (기본값 `admin` / `admin123`)

---

## 🚢 서비스 관리 및 배포

VidGen에는 상용 환경에 대응하는 **systemd 통합 서비스 매니저**가 내장되어 있습니다 (`systemd/`):

```bash
# 대화형 서비스 매니저 실행
chmod +x systemd/manage-services.sh
./systemd/manage-services.sh
```

사용 가능한 명령어:
- **`manage-services.sh status`**: Web, Admin, Backend API, Celery의 실시간 상태 확인.
- **`manage-services.sh start`**: 전체 서비스 일괄 구동.
- **`manage-services.sh restart`**: 전체 서비스 안전 재시작.
- **`deploy.sh`**: 원클릭 자동 배포 스크립트.

자세한 Nginx 및 aaPanel 배포 절차는 [docs/05-deployment/production-deployment.md](docs/05-deployment/production-deployment.md)를 참조하세요.

---

## 🛠️ CLI 유지보수 툴

`backend/scripts/` 폴더에는 운영 관리를 위한 유용한 CLI 스크립트가 제공됩니다:

```bash
# 사용자 계정에 크레딧 수동 지급
python scripts/add_credits.py --email user@example.com --amount 1000

# 시스템에 신규 AI 모델 일괄 임포트
python scripts/import_models.py

# 작품 URL Slug 및 태그 일괄 업데이트
python scripts/update_url_slugs_from_titles.py
```

---

## 📄 라이선스

본 프로젝트는 **MIT 라이선스**에 따라 오픈소스로 공개되어 있습니다. 자세한 내용은 [LICENSE](LICENSE) 파일을 참조하세요.

---

## 🤝 기여 및 커뮤니티

Issue 제보, 기능 제안, Pull Request를 열렬히 환영합니다!  
언제든지 Issue를 생성하거나 PR을 제출해 주세요.

*VidGen이 도움이 되셨다면 GitHub에서 ⭐️ Star를 눌러주세요!*
