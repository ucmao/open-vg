# Database Schema & Alembic Migrations

This document details VidGen's relational database models, tables, indexes, and Alembic migration workflows.

---

## 🗄️ Database Tables Schema

```
+------------------+         1:N         +------------------+
|      users       | ------------------> |      works       |
+------------------+                     +------------------+
| id (PK)          |                             |
| email            |                             | N:1
| credits          |                             v
| is_admin         |                     +------------------+
+--------+---------+                     |  workflows       |
         |                               +------------------+
         | 1:N                           | id (PK)          |
         v                               | nodes (JSONB)    |
+------------------+                     | edges (JSONB)    |
|  credit_records  |                     +------------------+
+------------------+                             ^
| id (PK)          |                             | 1:1
| user_id (FK)     |                     +------------------+
| type (Enum)      |                     | generation_models|
| amount           |                     +------------------+
+------------------+                     | id (PK)          |
                                         | workflow_id (FK) |
+------------------+                     | model_key        |
|  payment_orders  |                     +------------------+
+------------------+
| id (PK)          |
| user_id (FK)     |
| provider (Enum)  |
| status (Enum)    |
+------------------+
```

---

## 🚀 Alembic Migrations

```bash
cd backend
source venv/bin/activate
alembic revision --autogenerate -m "migration_description"
alembic upgrade head
```
