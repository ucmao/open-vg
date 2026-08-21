# Nuxt 3 SSR Troubleshooting Guide

This guide addresses common SSR hydration errors, network issues, and environment variable misconfigurations when running Nuxt 3 in production.

---

## ⚠️ Symptom: Refreshing Page Shows "Network Error"

### Root Cause
1. **Client Navigation**: Request originates in browser -> resolves relative URL -> works.
2. **SSR Page Refresh**: Request originates inside Nuxt Server (Node.js) -> resolves relative URL against Node.js localhost -> fails to hit FastAPI backend!

---

## 🛠️ Solution

Add `NUXT_INTERNAL_API_URL` to `web/.env`:

```env
# Client-side base URL (empty string when Nginx proxies /api)
NUXT_PUBLIC_API_BASE_URL=

# Server-side Nuxt SSR internal URL (REQUIRED for direct backend access)
NUXT_INTERNAL_API_URL=http://127.0.0.1:8000
```

Rebuild after modifying `.env`:
```bash
cd web
rm -rf .nuxt .output
npm run build
pm2 restart vidgen-web  # or systemctl restart vidgen-web
```
