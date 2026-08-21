# Local Development Guide & Conventions

This guide covers local development workflows, debugging techniques, and coding conventions across VidGen's Python FastAPI backend and Nuxt 3 frontend applications.

---

## 💻 Recommended Local Stack Setup

- **IDE**: VS Code or PyCharm / WebStorm
- **VS Code Extensions**:
  - Python / Pylance
  - Vue Language Features (Volar)
  - Tailwind CSS IntelliSense
  - ESLint / Prettier

---

## 🛠️ Multi-Terminal Development Workflow

When developing locally, run the four core components in separate terminals:

```
Terminal 1 (Backend API)  : uvicorn app.main:app --reload --port 8000
Terminal 2 (Celery Worker): celery -A app.celery_app worker -l info --pool solo
Terminal 3 (Web Portal)   : cd web && npm run dev
Terminal 4 (Admin Panel)  : cd admin && npm run dev
```

### 🧪 Zero-Cost Mock AI Generation Mode
For local UI testing and contribution without API keys, set `MOCK_AI_GENERATION=true` in `backend/.env`.
This simulates generation delay, produces placeholder assets, and broadcasts WebSocket completion notifications automatically.

---

## 🐍 Python & Backend Conventions

### 1. Pydantic v2 Schemas & ORM Compatibility
- Always use `from_attributes = True` (formerly `orm_mode = True`) in Pydantic schemas when serializing SQLAlchemy ORM model instances.

### 2. SQLAlchemy Enum Mapping Rule
To prevent database enum string mismatch bugs across PostgreSQL and SQLite:
```python
from enum import Enum
from sqlalchemy import Column, Enum as SQLEnum

class WorkStatus(str, Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

# Always use values_callable to serialize Enum values
status = Column(
    SQLEnum(WorkStatus, values_callable=lambda obj: [e.value for e in obj]),
    default=WorkStatus.PENDING,
    nullable=False
)
```

### 3. Database Session Dependency
- Inject async database sessions via FastAPI's `get_db()` dependency helper.
- Avoid persistent global DB session state across request handlers.

---

## 🎨 Vue 3 & Nuxt 3 Conventions

### 1. Composition API & `<script setup>`
- All Vue components must use the `<script setup lang="ts">` syntax.
- Store reactive state in Pinia modules (`web/stores/` or `admin/stores/`).

### 2. Tailored Toast & Modal System
- Use `useToast()` and `useConfirm()` composable hooks for clean UI notifications and deletion confirmation modals instead of browser native `alert()`.
