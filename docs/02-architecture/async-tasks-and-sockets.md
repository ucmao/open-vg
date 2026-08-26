# Asynchronous Tasks & Authenticated Job Updates

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
                                     (4) Render & Persist Status
                                                   │
                                                   v
                                            [ PostgreSQL ]
                                                   │
                                            (5) Status Polling
                                                   │
                                                   v
[ User Browser ] <────── Job Status ──────── [ FastAPI Server ]
```

---

## 🚀 Celery Worker Pool Options

- **Linux Production**: Prefork multi-process mode (`--concurrency=4`).
- **macOS Development**: Solo pool mode (`--pool solo`) to prevent Python `prefork` segfaults.

---

## 🌸 WebSocket acceleration

The browser connects to `/api/webhook/ws` with its JWT in the WebSocket
subprotocol header. The server derives the user ID from that verified token;
clients cannot choose a user ID in the URL.

API and Celery processes publish user events to a namespaced Redis Pub/Sub
channel. Every API instance subscribes to that channel and forwards matching
events to its own in-process WebSocket connections, so worker completions cross
process and container boundaries. PostgreSQL remains the durable job-state
source and browser polling remains the recovery path because Redis Pub/Sub is
intentionally transient.
