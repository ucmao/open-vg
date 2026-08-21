# Systemd

 Vidgen  Systemd Management Script。

---

## 📁

### Service

|  |  |  |  |
|------|------|------|------|
| `backend.service` | FastAPI  API  | ✅ | 8000 |
| `web.service` | Nuxt C  (web) | ✅ | 3000 |
| `admin.service` | Nuxt  (admin) | ✅ | 3001 |
| `celery-worker.service` | Celery Worker（） | ✅ | - |
| `celery-beat.service` | Celery Beat（） | ⚠️  | - |
| `flower.service` | Flower  | ⚠️  | 5555 |


|  |  |
|------|------|
| `deploy.sh` | Deployment Script（） |
| `manage-services.sh` | Management Script（） |
| `manage-celery.sh` | Celery Management Script |
| `README.md` | Systemd  |
| `README_CN.md` | （） |

---

## 🚀

### （）

```bash
# 1.
cd systemd/

# 2. Deployment Script（ sudo）
sudo ./deploy.sh

```


 [CELERY_SYSTEMD_DEPLOYMENT.md](../docs/CELERY_SYSTEMD_DEPLOYMENT.md)

---

## 🎮

### Management Script（）

```bash
# Start（backend, celery, frontend, admin）
sudo ./manage-services.sh start

# Start（ beat, flower）
sudo ./manage-services.sh start all

# Restart
sudo ./manage-services.sh restart backend

# Restart Celery Worker
sudo ./manage-services.sh restart celery

# Restart
sudo ./manage-services.sh restart admin

# Service Status
sudo ./manage-services.sh status

#  Celery
sudo ./manage-services.sh logs celery

sudo ./manage-services.sh enable

./manage-services.sh help
```

###  systemctl（）

```bash
# Start
sudo systemctl start vidgen-backend celery-worker vidgen-web vidgen-admin

# Stop
sudo systemctl stop vidgen-backend celery-worker vidgen-web vidgen-admin

# Restart
sudo systemctl restart vidgen-backend
sudo systemctl restart celery-worker
sudo systemctl restart vidgen-web
sudo systemctl restart vidgen-admin

sudo systemctl status vidgen-backend celery-worker vidgen-web vidgen-admin

# View Logs
sudo journalctl -u celery-worker -f
sudo journalctl -u vidgen-backend -f
sudo journalctl -u vidgen-web -f
sudo journalctl -u vidgen-admin -f

sudo systemctl enable vidgen-backend celery-worker vidgen-web vidgen-admin
```

---

## ⚙️

### celery-worker.service（）

**：** ， AI

**：**
- `--concurrency=4`: （ CPU ）
- `--queues=workflow`:  workflow
- `--max-tasks-per-child=100`:  100 Restart（）

**：**
- `WorkingDirectory=/path/to/vidgen/backend` →
- `Environment="PATH=/path/to/.../venv/bin..."` →
- `ExecStart=/path/to/.../venv/bin/celery...` →

---

### celery-beat.service（）

**：** （，Start）

**：**  Beat ，

---

### flower.service（）

**：** Celery  Web

**：** http://localhost:5555  Nginx

**：**
- （`--basic_auth=admin:change_this_password`）
-  Nginx  IP

---

### admin.service（）

**：**  Nuxt  (admin)， `https://admin.yourdomain.com`。

**：**
- `PORT=3001`： C  frontend (3000)
- `WorkingDirectory`： `admin`
-  `admin`  `npm run build`， `npm run preview`  `.output/server/index.mjs`

**Nginx：**  `admin.yourdomain.com`  `http://127.0.0.1:3001`。

---

## 📋


- [ ] Redis （`redis-cli ping`）
- [ ] PostgreSQL
- [ ] Python
- [ ] Celery （`pip install celery flower`）
- [ ]


- [ ] （`/var/log/celery`）
- [ ]  PID （`/var/run/celery`）
- [ ]  service  `/etc/systemd/system/`
- [ ]
- [ ] `sudo systemctl daemon-reload`
- [ ] `sudo systemctl start celery-worker`
- [ ] `sudo systemctl enable celery-worker`


- [ ] `systemctl status celery-worker`  active (running)
- [ ] `celery inspect active`  Worker
- [ ] （`journalctl -u celery-worker -n 50`）
- [ ]
- [ ] Flower （）

---

## 🆘


- [Celery Systemd ](../docs/CELERY_SYSTEMD_DEPLOYMENT.md) -
- [Celery ](../backend/CELERY_README.md) -
- [](../docs/COMMAND_LINE_DEPLOYMENT_CN.md) -


**Q:  3 ？**
A:  `celery-worker`（），`celery-beat`  `flower` 。

**Q: Start API Start Worker ？**
A: API ，，""。

**Q: Worker Restart？**
A: 。（ 10 ），。

**Q: ？**
A:  Flower ，：`celery -A app.celery_app inspect reserved`

---

**？！** 📚
