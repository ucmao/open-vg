# User Web Portal Architecture (Nuxt 3)

This document covers the frontend architecture of VidGen's **User Web Portal** (`web/`), built on **Nuxt 3** (Vue 3, TypeScript, Tailwind CSS, Pinia).

---

## 🌐 Hybrid Rendering Strategy

```
                          +-----------------------------------+
                          |      Nuxt 3 Web Portal (web/)     |
                          +-----------------+-----------------+
                                            |
                    +-----------------------+-----------------------+
                    |                                               |
                    v                                               v
        +-----------------------+                       +-----------------------+
        |  SSR / ISR (Server)   |                       |    CSR (Client SPA)   |
        |  /                    |                       |  /generate            |
        |  /prompt/[slug]       |                       |  /recharge            |
        |  /topic/[slug]        |                       |  /profile             |
        |  /category/[slug]     |                       +-----------------------+
        +-----------------------+
```

---

## 📦 Pinia State Management

- **`userStore`**: Manages auth state, active credits, user handle `@username`, and avatar.
- **`generationStore`**: Holds current prompt inputs, selected model configurations, and live generation state.
