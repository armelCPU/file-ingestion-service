# File Service

A RAG (Retrieval-Augmented Generation) file ingestion service built with FastAPI and Celery, following a **hexagonal (port-and-adapter) architecture**.

---

## Running the service

**API server**
```bash
python app.py
```

**Celery worker** (concurrency = 4, dedicated queue)
```bash
celery -A worker.celery_app worker --loglevel=info --concurrency=4 --without-heartbeat --without-mingle --without-gossip -Q file_queue
```

**Purge the queue**
```bash
celery -A worker.celery_app purge -Q file_queue
```

---

## Architecture

The codebase is organised in four concentric layers. Inner layers know nothing about outer layers.

```
┌─────────────────────────────────────────────────────┐
│  web/              FastAPI routes & schemas          │
├─────────────────────────────────────────────────────┤
│  workers/          Celery tasks                      │
├─────────────────────────────────────────────────────┤
│  services/         Domain orchestration              │
├─────────────────────────────────────────────────────┤
│  infrastructure/   Concrete adapters (mocks)         │
├─────────────────────────────────────────────────────┤
│  domain/           Entities & port interfaces        │
└─────────────────────────────────────────────────────┘
```

### `domain/` — Core (no dependencies)

| Path | Role |
|------|------|
| `domain/entities/document.py` | `Document` — the central data model (id, url, text, embedding, status) |
| `domain/ports/file_downloader.py` | `IFileDownloader` — contract for fetching a file from a URL |
| `domain/ports/text_extractor.py` | `ITextExtractor` — contract for extracting plain text from raw bytes |
| `domain/ports/embedding_repository.py` | `IEmbeddingRepository` — contract for computing a vector embedding from text |
| `domain/ports/document_repository.py` | `IDocumentRepository` — contract for persisting a document |
| `domain/ports/ingestion_job_repository.py` | `IIngestionJobRepository` — contract for tracking running tasks per user |

Ports are pure Python ABCs. They define *what* is needed, never *how*.

---

### `infrastructure/adapters/` — Mock implementations

Each adapter implements one port. All are mocked (no real I/O).

| Adapter | Port it implements | Behaviour |
|---------|-------------------|-----------|
| `file_downloader_mock.py` | `IFileDownloader` | Returns fixed bytes |
| `text_extractor_mock.py` | `ITextExtractor` | Returns a fixed string |
| `embedding_repository_mock.py` | `IEmbeddingRepository` | Returns a random 1536-dim vector (OpenAI ada-002 shape) |
| `document_repository_in_memory.py` | `IDocumentRepository` | Stores documents in an in-memory dict with auto-incremented IDs |
| `ingestion_job_repository_redis.py` | `IIngestionJobRepository` | Uses a Redis set (`ingestion:running:{user_id}`) to count and track running tasks per user |

To swap in real implementations (PostgreSQL, OpenAI API, S3…), create a new adapter that implements the same port and wire it in — no other layer changes.

---

### `services/` — Orchestration

`DocumentIngestionService` wires the four pipeline ports together and executes the ingestion sequence:

```
download(url) → extract(bytes) → compute(text) → save(document)
```

It receives all dependencies through constructor injection and has no knowledge of FastAPI, Celery, or any concrete infrastructure.

---

### `workers/tasks/documents/process_document_ingestion.py` — Celery task

This is where the infrastructure, service, and concurrency constraint meet.

**Per-user concurrency guard**

The Celery worker pool has a global concurrency of 4. On top of that, each user is limited to 3 simultaneously running tasks. The guard is enforced at the start of every task execution:

```
1. Query Redis: how many tasks are currently running for this user_id?
2. If >= 3 → reschedule the task (self.retry, countdown=30 s) and exit.
3. Otherwise → mark this task as running in Redis, proceed.
4. On exit (success or error) → mark this task as done in Redis (finally block).
```

The Redis set key is `ingestion:running:{user_id}`. Adding a task ID to the set marks it running; removing it marks it done.

**Full execution flow**

```
Celery worker picks up task
    │
    ├─ count_running(user_id) >= 3?
    │       └─ YES → retry in 30 s
    │
    ├─ mark_running(user_id, task_id)
    │
    ├─ DocumentIngestionService.ingest(document)
    │       ├─ FileDownloaderMock.download(url)       → bytes
    │       ├─ TextExtractorMock.extract(bytes)        → str
    │       ├─ EmbeddingRepositoryMock.compute(text)   → list[float]
    │       └─ DocumentRepositoryInMemory.save(doc)    → Document
    │
    └─ mark_done(user_id, task_id)   ← always, in finally
```

---

### `web/` — HTTP layer

| Path | Role |
|------|------|
| `web/schemas/document_schema.py` | `DocumentIngestionIn` — request body schema |
| `web/api/v1/document_endpoint.py` | `POST /api/v1/documents/index` — validates input, dispatches Celery task, returns 202 immediately |

The endpoint is intentionally thin: it does no business logic, only validates the request and enqueues the task.

**Authentication** is handled by `webapp/auth_middleware.py` via a static API key passed in the `Authorization` header.

---

## Request lifecycle

```
Client
  │
  │  POST /api/v1/documents/index
  │  Authorization: <token>
  │  { document_id, workspace_id, document_url, user_id, document_name }
  ▼
FastAPI endpoint (web/api/v1/document_endpoint.py)
  │
  │  apply_async(kwargs={...}, countdown=3)
  ▼
Redis (Celery broker — file_queue)
  │
  │  worker picks up task after 3 s
  ▼
Celery task (workers/tasks/documents/process_document_ingestion.py)
  │
  ├─ concurrency guard (Redis)
  └─ DocumentIngestionService → mock adapters
```

---

## Project structure

```
file-service/
├── app.py                          # FastAPI application factory
├── settings.py                     # Environment configuration
├── worker.py                       # Celery application factory
│
├── domain/
│   ├── entities/
│   │   └── document.py             # Document domain entity
│   └── ports/
│       ├── document_repository.py
│       ├── embedding_repository.py
│       ├── file_downloader.py
│       ├── ingestion_job_repository.py
│       └── text_extractor.py
│
├── infrastructure/
│   └── adapters/
│       ├── document_repository_in_memory.py
│       ├── embedding_repository_mock.py
│       ├── file_downloader_mock.py
│       ├── ingestion_job_repository_redis.py
│       └── text_extractor_mock.py
│
├── services/
│   └── document_ingestion_service.py
│
├── web/
│   ├── api/v1/
│   │   └── document_endpoint.py
│   └── schemas/
│       └── document_schema.py
│
└── workers/
    └── tasks/documents/
        └── process_document_ingestion.py
```
