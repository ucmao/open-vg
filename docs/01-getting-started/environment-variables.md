# Exhaustive Environment Variables Reference

This document serves as the authoritative reference for all environment variables used across **Backend (`backend/.env`)**, **User Web Portal (`web/.env`)**, and **Admin Panel (`admin/.env`)**.

---

## ⚙️ Backend Environment Variables (`backend/.env`)

### Database & Redis Configuration

| Variable Name | Required | Default Value | Description |
|---|---|---|---|
| `DATABASE_URL` | **Yes** | `postgresql://user:password@localhost:5432/aigc_platform` | SQLAlchemy database URI for PostgreSQL 15+ |
| `REDIS_URL` | **Yes** | `redis://localhost:6379` | Redis 7+ connection URI for Celery broker & WebSocket Pub/Sub |

### Authentication & Security

| Variable Name | Required | Default Value | Description |
|---|---|---|---|
| `JWT_SECRET` | **Yes** | `your_jwt_secret_key_at_least_16_chars_long` | Secret key used for user and admin JWT token signatures |
| `CONFIG_ENCRYPTION_KEY` | **Yes** | `your_random_config_encryption_key_here` | Secret key used to encrypt vendor API Keys in the database |
| `OVERSEAS_PARSER_TOKEN` | **Yes** | `your_random_overseas_parser_token_here` | Secret token for authenticating overseas parser requests |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | No | `10080` (7 days) | Token expiration duration in minutes |

### AI Model Provider API Keys

| Variable Name | Required | Default Value | Description |
|---|---|---|---|
| `REPLICATE_API_KEY` | No | `""` | Replicate API key; the backend passes it to the Replicate SDK |
| `GEMINI_API_KEY` | No | `""` | Google Gemini API Key |
| `MIDJOURNEY_API_KEY` | No | `""` | Midjourney Proxy API Key |

### Object Storage (Cloudflare R2 / S3 / OSS)

| Variable Name | Required | Default Value | Description |
|---|---|---|---|
| `STORAGE_PROVIDER` | No | `local` | Storage provider (`local`, `r2`, `s3`, `oss`) |
| `S3_BUCKET_NAME` | No | `vidgen-media` | Bucket name for storing generated images and videos |
| `S3_ACCESS_KEY_ID` | No | `""` | AWS S3 / Cloudflare R2 Access Key ID |
| `S3_SECRET_ACCESS_KEY` | No | `""` | AWS S3 / Cloudflare R2 Secret Access Key |
| `S3_ENDPOINT_URL` | No | `""` | Custom S3 endpoint URL (Required for Cloudflare R2) |
| `STORAGE_CDN_URL` / `R2_PUBLIC_DOMAIN` | No | `""` | Public CDN base URL for media assets (e.g. `https://cdn.yourdomain.com`) |
| `MOCK_AI_GENERATION` | No | `false` | Enable zero-cost mock AI generation for local development and UI testing |

### Payment Gateways (PayPal & Stripe)

| Variable Name | Required | Default Value | Description |
|---|---|---|---|
| `PAYPAL_CLIENT_ID` | No | `""` | PayPal REST API v2 Client ID |
| `PAYPAL_CLIENT_SECRET` | No | `""` | PayPal REST API v2 Secret Key |
| `PAYPAL_MODE` | No | `sandbox` | PayPal operation mode (`sandbox` or `live`) |
| `STRIPE_SECRET_KEY` | No | `""` | Stripe API Secret Key |
| `STRIPE_WEBHOOK_SECRET` | No | `""` | Stripe Webhook signing secret |

### Daily Check-in & Rewards Rules

| Variable Name | Required | Default Value | Description |
|---|---|---|---|
| `CHECKIN_BASE_REWARD` | No | `5` | Base credit reward for Day 1 check-in |
| `CHECKIN_CONSECUTIVE_BONUS` | No | `2` | Additional streak bonus credits per consecutive day |
| `CHECKIN_MAX_CONSECUTIVE` | No | `7` | Consecutive streak multiplier cap in days |
| `CHECKIN_REWARD_EXPIRY_DAYS` | No | `60` | Expiration window for rewarded credits in days |

---

## 🌐 User Web Portal Variables (`web/.env`)

| Variable Name | Required | Default Value | Description |
|---|---|---|---|
| `NUXT_PUBLIC_API_BASE_URL` | **Yes** | `http://localhost:8000` | Client-side API base URL (Must be `""` in production Nginx proxy) |
| `NUXT_INTERNAL_API_URL` | **Yes** (SSR) | `http://127.0.0.1:8000` | Server-side Nuxt SSR internal API URL for Direct Backend Calls |
| `NUXT_PUBLIC_WS_URL` | **Yes** | `ws://localhost:8000` | WebSocket server origin; the client appends `/api/webhook/ws` |
| `NUXT_PUBLIC_SITE_URL` | No | `http://localhost:3000` | Public website domain URL for SSR fallback & canonical tags |

---

## 🔧 Admin Panel Variables (`admin/.env`)

| Variable Name | Required | Default Value | Description |
|---|---|---|---|
| `NUXT_PUBLIC_API_BASE_URL` | **Yes** | `http://localhost:8000` | Admin API base URL |
| `NUXT_PUBLIC_WS_URL` | No | `ws://localhost:8000` | WebSocket server origin |
