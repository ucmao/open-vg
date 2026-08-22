# Systemd

 Systemd  Celery Worker、Celery Beat  Flower 。

---

## 📋

- [](#)
- [](#)
- [](#)
- [](#)
- [](#)
- [](#)
- [](#)

---

## 🏗️


```
┌─────────────────────────────────────────────────┐
│  (Systemd )                             │
│ ├─ Nuxt C  (web)    : 3000       │
│ ├─ Nuxt  (admin)   : 3001       │
│ └─ : systemctl start vidgen-web vidgen-admin │
├─────────────────────────────────────────────────┤
│  (Systemd )                            │
│ ├─ FastAPI                    : 8000        │
│ ├─ Celery Worker                        │
│ ├─ Celery Beat ()                   │
│ ├─ Flower ()              : 5555        │
│ └─ : systemctl start/stop/restart           │
├─────────────────────────────────────────────────┤
│  ()                                │
│ ├─ PostgreSQL                 : 5432        │
│ └─ Redis                      : 6379        │
└─────────────────────────────────────────────────┘
```

### Systemd

|  |  |  |  |
|--------|------|------|------|
| `vidgen-backend` | FastAPI  API | ✅  | 8000 |
| `vidgen-web` | Nuxt C  | ✅  | 3000 |
| `vidgen-admin` | Nuxt  (admin) | ✅  | 3001 |
| `celery-worker` |  | ✅  | - |
| `celery-beat` |  | ⚠️  | - |
| `flower` | Celery  | ⚠️  | 5555 |

---

## 🚀

###  A: Deployment Script（）

```bash
# 1.  systemd
cd systemd/

# 2. Deployment Script（ sudo）
sudo ./deploy.sh

# ：
# -  PID
# -  service
# -  systemd
# - Start
```

###  B:

""。

---

## 🛠️

Deployment Script，：

### 1.

```bash
sudo mkdir -p /var/log/celery
sudo chown www-data:www-data /var/log/celery

#  PID
sudo mkdir -p /var/run/celery
sudo chown www-data:www-data /var/run/celery
```

### 2.

 service ， `/path/to/vidgen` ：

```bash
# ： /home/user/vidgen
# ：
WorkingDirectory=/home/user/vidgen/backend
Environment="PATH=/home/user/vidgen/backend/venv/bin:..."
ExecStart=/home/user/vidgen/backend/venv/bin/celery ...
```

**：**
```bash
#  /home/user/vidgen
PROJECT_PATH="/home/user/vidgen"

#  celery-worker.service
sed "s|/path/to/vidgen|$PROJECT_PATH|g" \
    celery-worker.service > /tmp/celery-worker.service
```

### 3.  service

```bash
#  systemd
sudo cp celery-worker.service /etc/systemd/system/
sudo cp celery-beat.service /etc/systemd/system/      #
sudo cp flower.service /etc/systemd/system/           #

sudo chmod 644 /etc/systemd/system/celery-*.service
sudo chmod 644 /etc/systemd/system/flower.service
```

### 4.  Systemd

```bash
#  systemd
sudo systemctl daemon-reload
```

### 5. Start

```bash
# Start Celery Worker（）
sudo systemctl start celery-worker

# Start Celery Beat（，）
sudo systemctl start celery-beat

# Start Flower（，）
sudo systemctl start flower
```

### 6.

```bash
sudo systemctl enable celery-worker
sudo systemctl enable celery-beat    #
sudo systemctl enable flower         #
```

---

## 🎮

### Management Script（）

```bash
# Start
sudo ./manage-celery.sh start

# Restart Worker
sudo ./manage-celery.sh restart worker

sudo ./manage-celery.sh status

#  Worker
sudo ./manage-celery.sh logs worker
```

###  systemctl

#### Start
```bash
sudo systemctl start celery-worker
sudo systemctl start celery-beat
sudo systemctl start flower
```

#### Stop
```bash
sudo systemctl stop celery-worker
sudo systemctl stop celery-beat
sudo systemctl stop flower
```

#### Restart
```bash
sudo systemctl restart celery-worker
sudo systemctl restart celery-beat
sudo systemctl restart flower
```

```bash
sudo systemctl status celery-worker

sudo systemctl status celery-worker celery-beat flower
```

```bash
sudo systemctl enable celery-worker
sudo systemctl enable celery-beat
sudo systemctl enable flower
```

```bash
sudo systemctl disable celery-worker
```

---

## 📋

### View Logs

```bash
#  Worker
sudo journalctl -u celery-worker -f

#  Beat
sudo journalctl -u celery-beat -f

#  Flower
sudo journalctl -u flower -f
```


```bash
#  100
sudo journalctl -u celery-worker -n 100

sudo journalctl -u celery-worker --since today

#  1
sudo journalctl -u celery-worker --since "1 hour ago"

sudo journalctl -u celery-worker --since "2026-02-11 10:00:00" --until "2026-02-11 11:00:00"
```


```bash
sudo journalctl -u celery-worker -p err

sudo journalctl -u celery-worker -p warning
```


```bash
sudo journalctl -u celery-worker --since today > celery-worker.log
```

---

## 🐛

###  1: Start

**：**

```bash
# 1.
sudo systemctl status celery-worker -l

# 2. View Logs
sudo journalctl -u celery-worker -n 50

# 3.
sudo systemd-analyze verify /etc/systemd/system/celery-worker.service
```

**：**
- ❌ （WorkingDirectory, ExecStart）
- ❌
- ❌ （User/Group）
- ❌ Redis Start

---

###  2: Restart

**：**
```bash
# Restart
sudo journalctl -u celery-worker | grep "Started\|Stopped"

sudo journalctl -u celery-worker -p err
```

**：**
- ❌ （ Bug）
- ❌ （OOM）
- ❌
- ❌ Redis

---

###  3:

**：**
```bash
# 1.
sudo systemctl status celery-worker

# 2.  Worker
cd /path/to/backend
source venv/bin/activate
celery -A app.celery_app inspect active

# 3.
celery -A app.celery_app inspect reserved

# 4.  Redis
redis-cli ping
```

---

###  4: Stop

**：**

**：**
```bash
# Stop（ service ）
TimeoutStopSec=600  #  10

# Restart
sudo systemctl daemon-reload
sudo systemctl restart celery-worker
```

---

## ⚙️

### 1.

 CPU ：

```ini
#  /etc/systemd/system/celery-worker.service
ExecStart=... --concurrency=8  #  CPU
```

### 2.  Worker（）

** Worker ：**

```bash
sudo cp /etc/systemd/system/celery-worker.service \
        /etc/systemd/system/celery-worker@.service

#  hostname（）
# --hostname=worker-%i@%%h
```

**Start：**
```bash
sudo systemctl start celery-worker@1
sudo systemctl start celery-worker@2
sudo systemctl start celery-worker@3
```

### 3.

：

```ini
# （ 2GB）
MemoryLimit=2G

#  CPU （ 200%， 2 ）
CPUQuota=200%

LimitNOFILE=65536
```

### 4.

：

```bash
#  Prometheus + Grafana
# Celery  Prometheus exporter

#  Monit
```

---

## 🔐

### 1.

```bash
#  celery
sudo useradd -r -s /bin/false celery

#  service
User=celery
Group=celery

sudo chown -R celery:celery /var/log/celery
sudo chown -R celery:celery /var/run/celery
```

### 2.

 service ：

```ini
# ❌
Environment="REDIS_URL=redis://:password@localhost:6379"

# ✅ ： EnvironmentFile
EnvironmentFile=/path/to/backend/.env
```

### 3. （）

```ini
RestrictAddressFamilies=AF_INET AF_INET6
PrivateNetwork=false
```

---

## 📊 Start

Systemd Start：

```
1. Redis ()
2. PostgreSQL ()
3. Backend FastAPI (Systemd)
4. Celery Worker (Systemd) ←  Redis
5. Celery Beat (Systemd) ←  Redis
6. Flower (Systemd) ←  Celery Worker
```

 service  `[Unit]` ：
```ini
After=redis.service postgresql.service
Wants=redis.service
```

---

## 🔄


```bash
# 1.
git pull

# 2.
cd backend
source venv/bin/activate
pip install -r requirements.txt

# 3. （）
alembic upgrade head

# 4. Restart
sudo systemctl restart celery-worker
sudo systemctl restart backend  #
```


```bash
# 1.  service
sudo vim /etc/systemd/system/celery-worker.service

# 2.  systemd
sudo systemctl daemon-reload

# 3. Restart
sudo systemctl restart celery-worker
```

---

## 📈

###  systemctl

```bash
sudo systemctl status celery-worker

# ：
# ● celery-worker.service
#    Active: active (running) since ...
#    Main PID: 1234
#    Tasks: 5 (limit: 4915)
#    Memory: 256.3M
#    CPU: 2min 34.123s
```

###  Flower

 http://your-server:5555

###  journalctl

```bash
sudo journalctl -u celery-worker --since today | grep ERROR | wc -l

sudo journalctl -u celery-worker -p err | grep -oP 'ERROR.*' | sort | uniq -c | sort -rn
```

---

## 🧪

### 1. Service Status

```bash
sudo systemctl status celery-worker
```

：
```
● celery-worker.service - Celery Worker for Vidgen
   Loaded: loaded (/etc/systemd/system/celery-worker.service; enabled)
   Active: active (running) since ...
```

### 2.  Worker

```bash
cd /path/to/backend
source venv/bin/activate
celery -A app.celery_app inspect active

# ：
# -> worker1@hostname: OK
```

### 3.

```bash
python -c "
from app.tasks.workflow_tasks import execute_workflow_task
result = execute_workflow_task.delay(work_id=9999, user_id=1)
print(f': {result.id}')
"

# View Logs
sudo journalctl -u celery-worker -f
```

---

## 🆘

```bash
# ===  ===
sudo systemctl start celery-worker       # Start
sudo systemctl stop celery-worker        # Stop
sudo systemctl restart celery-worker     # Restart
sudo systemctl reload celery-worker      #
sudo systemctl status celery-worker      #

# ===  ===
sudo systemctl enable celery-worker      #
sudo systemctl disable celery-worker     #
sudo systemctl is-enabled celery-worker  #

# ===  ===
sudo journalctl -u celery-worker -f      #
sudo journalctl -u celery-worker -n 100  #  100
sudo journalctl -u celery-worker --since today  #

# ===  ===
sudo systemctl daemon-reload             #
sudo systemctl edit celery-worker        # （）
sudo systemctl cat celery-worker         #

# ===  ===
sudo systemctl list-units --failed       #
sudo systemctl reset-failed celery-worker  #
```

---

## 🎯


- [ ] Redis
- [ ] PostgreSQL
- [ ] Python
- [ ] requirements.txt
- [ ] .env
- [ ]


- [ ]  PID
- [ ]  service
- [ ]  /etc/systemd/system/
- [ ]  systemd
- [ ] Start
- [ ]
- [ ]
- [ ]
- [ ] （）
- [ ] （）


- [ ] `systemctl status celery-worker`  active (running)
- [ ] `celery inspect active`  Worker
- [ ]
- [ ]
- [ ] Flower （）

---

## 📚

- [Deployment Documentation](../docs/05-deployment/)
- [Celery Documentation](https://docs.celeryq.dev/)
- [Systemd Documentation](https://www.freedesktop.org/software/systemd/man/)

---

**！** 🚀
