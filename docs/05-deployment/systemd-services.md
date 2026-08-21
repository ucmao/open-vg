# Systemd Services Suite Reference

This document covers Systemd unit definitions and operational control scripts for VidGen.

---

## 📋 Systemd Units

Located in `systemd/`:

| Unit File Name | Service Identifier | Description | Port |
|---|---|---|---|
| `backend.service` | `vidgen-backend.service` | FastAPI Core REST API | 8000 |
| `celery-worker.service` | `celery-worker.service` | Celery AI generation worker | N/A |
| `web.service` | `vidgen-web.service` | Nuxt 3 user portal Node SSR | 3000 |
| `admin.service` | `vidgen-admin.service` | Nuxt 3 admin panel SPA | 3001 |

---

## 🎮 Operations Commands

```bash
cd /www/wwwroot/vidgen/systemd

# Start all core services
sudo ./manage-services.sh start

# Restart services after code pull
sudo ./manage-services.sh restart

# Check status
sudo ./manage-services.sh status

# Tail live logs
sudo ./manage-services.sh logs backend
```
