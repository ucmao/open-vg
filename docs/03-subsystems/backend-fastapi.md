# Backend FastAPI Services Architecture

This document describes the structure, authentication scopes, and data validation layers of VidGen's FastAPI REST API server (`backend/`).

---

## ⚙️ REST API Route Structure

```
backend/app/routes/
├── admin.py                  # Superadmin core settings & user controls
├── admin_auth.py             # Admin login & token issuance
├── admin_moderation.py       # Content moderation, lexicons & reports
├── admin_sockpuppets.py      # Synthetic user account generator
├── checkin.py                # Daily check-in & streak rewards API
├── generation.py             # Work generation dispatch & status polling
├── payment.py                # PayPal & Stripe top-up checkout endpoints
└── works.py                  # Community gallery, like/favorite & comments
```

---

## 🔒 JWT Scopes & Dependencies

- **User Authentication**: `get_current_user` dependency verifies bearer JWTs signed with `JWT_SECRET_KEY`.
- **Admin Authentication**: `get_current_admin_user` dependency enforces `is_admin = True` and validates tokens signed with `ADMIN_JWT_SECRET_KEY`.
