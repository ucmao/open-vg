# Asynchronous Tasks & WebSocket Progress Streaming

This document details VidGen's task queuing architecture built on **Celery**, **Redis Broker**, and **WebSockets**.

---

## ⚡ Task Lifecycle Flow

```
[ User Browser ] ──(1) POST /api/generate ──> [ FastAPI Server ]
                                                   │
                                            (2) Instant Ack (<100ms)
                                                   │
                                                   v
                                          [ Redis Task Broker ]
                                                   │
                                            (3) Task Pickup
                                                   │
                                                   v
                                         [ Celery Worker Node ]
                                                   │
                                     (4) Render & Progress Updates
                                                   │
                                                   v
                                         [ Redis Pub/Sub Channel ]
                                                   │
                                            (5) WS Event Relay
                                                   │
                                                   v
[ User Browser ] <──(6) Real-time Progress ─── [ FastAPI WebSocket ]
```

---

## 🚀 Celery Worker Pool Options

- **Linux Production**: Prefork multi-process mode (`--concurrency=4`).
- **macOS Development**: Solo pool mode (`--pool solo`) to prevent Python `prefork` segfaults.

---

## 🌸 Real-Time WebSocket Streaming

1. **Celery Worker**: Publishes progress payloads to Redis Pub/Sub channel `work_progress_{work_id}`.
2. **FastAPI WS Server**: Listens on `/ws` and streams progress percentages and status updates live to the user browser.
