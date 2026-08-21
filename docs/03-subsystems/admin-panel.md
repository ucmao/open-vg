# Admin Panel Architecture & Tooling

This document describes VidGen's **Admin Panel** (`admin/`), an independent Nuxt 3 SPA on Port 3001.

---

## 🔧 Subsystems Breakdown

### 1. VueFlow Workflow Builder (`/workflows`)
Visual node graph editor using `@vue-flow/core` to build and test node pipelines.

### 2. Sockpuppet Synthetic User Generator (`/sockpuppets`)
Generates synthetic accounts via `faker` and Cloudflare R2 avatars to seed initial community prompt galleries.

### 3. Bilingual i18n
100% English UI default with a 1-click runtime toggle to Chinese (`admin/locales/en.json` & `zh.json`).
