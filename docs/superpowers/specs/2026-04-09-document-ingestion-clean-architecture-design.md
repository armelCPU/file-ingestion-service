# Document Ingestion — Clean Architecture Design

**Date:** 2026-04-09  
**Context:** Refactor the file-service ingestion endpoint and Celery worker to follow a hexagonal (port-and-adapter) architecture matching the pi-backend pattern.

---

## Problem

The current codebase has no layering: the FastAPI endpoint imports the Celery task directly, the task body is empty, and infrastructure concerns (Redis, Postgres, OpenAI) live in an uninitialized singleton (`Memory`). The goal is to restructure around entities, ports, adapters, and a service layer — all mocked for now.

---

## Architecture

### Folder structure

```
domain/
  entities/
    document.py
    ingestion_job.py
  ports/
    file_downloader.py
    text_extractor.py
    embedding_repository.py
    document_repository.py
    ingestion_job_repository.py

infrastructure/
  adapters/
    file_downloader_mock.py
    text_extractor_mock.py
    embedding_repository_mock.py
    document_repository_in_memory.py
    ingestion_job_repository_redis.py

services/
  document_ingestion_service.py

web/
  api/
    v1/
      document_endpoint.py
  schemas/
    document_schema.py
  dependencies.py

worker/
  tasks/
    documents/
      process_document_ingestion.py
```

Existing files that move or are replaced:
- `webapp/endpoints/documents/document_ingestion.py` → `web/api/v1/document_endpoint.py`
- `workers/tasks/documents/document_indexing.py` → `worker/tasks/documents/process_document_ingestion.py`
- `commons/schemas/document_input.py` → `web/schemas/document_schema.py`

---

## Domain Entities

### `Document`
```python
class Document(BaseModel):
    id: Optional[int] = None
    document_id: int
    workspace_id: int
    user_id: int
    name: Optional[str]
    url: str
    text: Optional[str] = None
    embedding: Optional[list[float]] = None
    status: str = "pending"   # pending | done | failed
```

---

## Domain Ports (interfaces)

All are abstract base classes (`ABC`).

| Port | Methods |
|------|---------|
| `IFileDownloader` | `download(url: str) -> bytes` |
| `ITextExtractor` | `extract(content: bytes) -> str` |
| `IEmbeddingRepository` | `compute(text: str) -> list[float]` |
| `IDocumentRepository` | `save(document: Document) -> Document` |
| `IIngestionJobRepository` | `count_running(user_id: int) -> int`<br>`mark_running(user_id: int, task_id: str) -> None`<br>`mark_done(user_id: int, task_id: str) -> None` |

---

## Infrastructure Adapters (mocked)

| Adapter | Behaviour |
|---------|-----------|
| `FileDownloaderMock` | Returns `b"mock file content"` |
| `TextExtractorMock` | Returns `"extracted text from mock"` |
| `EmbeddingRepositoryMock` | Returns a list of 1536 random floats (OpenAI ada-002 dimension) |
| `DocumentRepositoryInMemory` | Stores documents in a module-level `dict[int, Document]` |
| `IngestionJobRepositoryRedis` | Uses a Redis sorted set `ingestion:running:{user_id}` — members are task IDs, scores are timestamps. `count_running` counts members, `mark_running` adds the task_id, `mark_done` removes it. |

---

## Service

### `DocumentIngestionService`

Receives all ports via constructor injection. No framework dependency.

```python
class DocumentIngestionService:
    def __init__(
        self,
        file_downloader: IFileDownloader,
        text_extractor: ITextExtractor,
        embedding_repository: IEmbeddingRepository,
        document_repository: IDocumentRepository,
    ): ...

    def ingest(self, document: Document) -> Document:
        content = self.file_downloader.download(document.url)
        text = self.text_extractor.extract(content)
        embedding = self.embedding_repository.compute(text)
        document.text = text
        document.embedding = embedding
        document.status = "done"
        return self.document_repository.save(document)
```

---

## Worker Task

### `process_document_ingestion` (Celery `@shared_task`)

Per-user concurrency guard: max 3 running tasks per user. If the limit is reached, the task reschedules itself with a 30-second countdown.

```
1. Build concrete adapters (mock implementations)
2. Build IngestionJobRepository (Redis)
3. Check count_running(user_id)
   - If >= 3: self.retry(countdown=30)
4. mark_running(user_id, self.request.id)
5. Build DocumentIngestionService with mock adapters
6. Call service.ingest(document)
7. mark_done(user_id, self.request.id)  ← always in finally
```

Error handling: any exception is caught, logged, `mark_done` is still called in `finally`, and `document.status = "failed"` is saved.

---

## Web Layer

### `web/schemas/document_schema.py`
Replaces `commons/schemas/document_input.py`. Same fields, same Pydantic model.

### `web/api/v1/document_endpoint.py`
Thin handler — validates input, dispatches Celery task, returns immediately.

```python
@router.post("/index", status_code=200)
async def ingest_document(document_in: DocumentIngestionIn, api_key: APIKey = Depends(check_auth_token)):
    process_document_ingestion.apply_async(
        kwargs={...},
        countdown=3,
        soft_time_limit=720,
        time_limit=720,
        priority=0,
    )
    return {"message": "Ingestion is running"}
```

### `web/dependencies.py`
FastAPI dependency functions for DI (not strictly needed for the worker path, but sets up the pattern for future endpoints that need services synchronously).

---

## Data Flow

```
POST /api/v1/documents/index
  └─ document_endpoint.py
       └─ process_document_ingestion.apply_async(...)
            └─ [Celery worker]
                 ├─ check count_running(user_id) via Redis
                 │    └─ if >= 3: retry in 30s
                 ├─ mark_running(user_id, task_id)
                 ├─ DocumentIngestionService.ingest(document)
                 │    ├─ FileDownloaderMock.download(url)
                 │    ├─ TextExtractorMock.extract(bytes)
                 │    ├─ EmbeddingRepositoryMock.compute(text)
                 │    └─ DocumentRepositoryInMemory.save(document)
                 └─ mark_done(user_id, task_id)  [finally]
```

---

## What is NOT in scope

- Real OpenAI API integration
- Real PostgreSQL persistence
- Semantic search endpoint
- Migration of `memory.py` singleton (removed, not replaced)
