# Document Ingestion — Clean Architecture Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Refactor the document ingestion pipeline into a hexagonal architecture (entities → ports → adapters → service → worker/endpoint) with all infrastructure mocked.

**Architecture:** Domain entities and port interfaces live in `domain/`. Mock adapters in `infrastructure/adapters/`. A pure `DocumentIngestionService` orchestrates the pipeline. The Celery task in `workers/tasks/documents/` enforces a per-user concurrency limit (max 3) via Redis before delegating to the service.

**Tech Stack:** FastAPI, Celery, Redis, Pydantic v2, pytest, fakeredis

---

## File Map

| Action | Path | Responsibility |
|--------|------|----------------|
| Create | `domain/__init__.py` | Package marker |
| Create | `domain/entities/__init__.py` | Package marker |
| Create | `domain/entities/document.py` | `Document` domain entity |
| Create | `domain/ports/__init__.py` | Package marker |
| Create | `domain/ports/file_downloader.py` | `IFileDownloader` ABC |
| Create | `domain/ports/text_extractor.py` | `ITextExtractor` ABC |
| Create | `domain/ports/embedding_repository.py` | `IEmbeddingRepository` ABC |
| Create | `domain/ports/document_repository.py` | `IDocumentRepository` ABC |
| Create | `domain/ports/ingestion_job_repository.py` | `IIngestionJobRepository` ABC |
| Create | `infrastructure/__init__.py` | Package marker |
| Create | `infrastructure/adapters/__init__.py` | Package marker |
| Create | `infrastructure/adapters/file_downloader_mock.py` | Returns fixed bytes |
| Create | `infrastructure/adapters/text_extractor_mock.py` | Returns fixed string |
| Create | `infrastructure/adapters/embedding_repository_mock.py` | Returns random 1536-dim vector |
| Create | `infrastructure/adapters/document_repository_in_memory.py` | In-memory dict store |
| Create | `infrastructure/adapters/ingestion_job_repository_redis.py` | Redis set per user |
| Create | `services/__init__.py` | Package marker |
| Create | `services/document_ingestion_service.py` | download → extract → embed → save |
| Create | `web/__init__.py` | Package marker |
| Create | `web/schemas/__init__.py` | Package marker |
| Create | `web/schemas/document_schema.py` | `DocumentIngestionIn` schema |
| Create | `web/api/__init__.py` | Package marker |
| Create | `web/api/v1/__init__.py` | Package marker |
| Create | `web/api/v1/document_endpoint.py` | Thin FastAPI route handler |
| Replace | `workers/tasks/documents/document_indexing.py` → `workers/tasks/documents/process_document_ingestion.py` | Celery task with retry guard |
| Modify | `workers/tasks/__init__.py` | Import new task module |
| Modify | `webapp/routes.py` | Point to new endpoint router |
| Create | `tests/__init__.py` | Package marker |
| Create | `tests/test_document_entity.py` | Entity validation tests |
| Create | `tests/test_mock_adapters.py` | Adapter contract tests |
| Create | `tests/test_ingestion_job_repository_redis.py` | Redis adapter tests (fakeredis) |
| Create | `tests/test_document_ingestion_service.py` | Service unit tests |
| Create | `tests/test_process_document_ingestion.py` | Task concurrency guard tests |
| Create | `tests/test_document_endpoint.py` | FastAPI endpoint tests |

---

## Task 1: Domain Entity

**Files:**
- Create: `domain/__init__.py`
- Create: `domain/entities/__init__.py`
- Create: `domain/entities/document.py`
- Create: `tests/__init__.py`
- Create: `tests/test_document_entity.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_document_entity.py
from domain.entities.document import Document


def test_document_default_status_is_pending():
    doc = Document(document_id=1, workspace_id=10, user_id=42, url="https://example.com/a.pdf")
    assert doc.status == "pending"


def test_document_optional_fields_default_to_none():
    doc = Document(document_id=1, workspace_id=10, user_id=42, url="https://example.com/a.pdf")
    assert doc.id is None
    assert doc.name is None
    assert doc.text is None
    assert doc.embedding is None
```

- [ ] **Step 2: Run test to confirm it fails**

```bash
pytest tests/test_document_entity.py -v
```

Expected: `ModuleNotFoundError: No module named 'domain'`

- [ ] **Step 3: Create package markers and entity**

```python
# domain/__init__.py
# (empty)
```

```python
# domain/entities/__init__.py
# (empty)
```

```python
# domain/entities/document.py
from typing import Optional
from pydantic import BaseModel


class Document(BaseModel):
    id: Optional[int] = None
    document_id: int
    workspace_id: int
    user_id: int
    name: Optional[str] = None
    url: str
    text: Optional[str] = None
    embedding: Optional[list[float]] = None
    status: str = "pending"
```

```python
# tests/__init__.py
# (empty)
```

- [ ] **Step 4: Run tests and confirm they pass**

```bash
pytest tests/test_document_entity.py -v
```

Expected: `2 passed`

- [ ] **Step 5: Commit**

```bash
git add domain/ tests/__init__.py tests/test_document_entity.py
git commit -m "feat: add Document domain entity"
```

---

## Task 2: Domain Ports

**Files:**
- Create: `domain/ports/__init__.py`
- Create: `domain/ports/file_downloader.py`
- Create: `domain/ports/text_extractor.py`
- Create: `domain/ports/embedding_repository.py`
- Create: `domain/ports/document_repository.py`
- Create: `domain/ports/ingestion_job_repository.py`

Ports are pure ABCs — no runtime behaviour to test. We verify they can be imported and subclassed.

- [ ] **Step 1: Write the failing test**

```python
# tests/test_document_entity.py  (append to existing file)
from domain.ports.file_downloader import IFileDownloader
from domain.ports.text_extractor import ITextExtractor
from domain.ports.embedding_repository import IEmbeddingRepository
from domain.ports.document_repository import IDocumentRepository
from domain.ports.ingestion_job_repository import IIngestionJobRepository


def test_ports_are_importable():
    assert IFileDownloader
    assert ITextExtractor
    assert IEmbeddingRepository
    assert IDocumentRepository
    assert IIngestionJobRepository
```

- [ ] **Step 2: Run test to confirm it fails**

```bash
pytest tests/test_document_entity.py::test_ports_are_importable -v
```

Expected: `ModuleNotFoundError: No module named 'domain.ports'`

- [ ] **Step 3: Create port files**

```python
# domain/ports/__init__.py
# (empty)
```

```python
# domain/ports/file_downloader.py
from abc import ABC, abstractmethod


class IFileDownloader(ABC):
    @abstractmethod
    def download(self, url: str) -> bytes:
        """Download file content from a URL."""
```

```python
# domain/ports/text_extractor.py
from abc import ABC, abstractmethod


class ITextExtractor(ABC):
    @abstractmethod
    def extract(self, content: bytes) -> str:
        """Extract plain text from raw file content."""
```

```python
# domain/ports/embedding_repository.py
from abc import ABC, abstractmethod


class IEmbeddingRepository(ABC):
    @abstractmethod
    def compute(self, text: str) -> list[float]:
        """Compute the embedding vector for a given text."""
```

```python
# domain/ports/document_repository.py
from abc import ABC, abstractmethod

from domain.entities.document import Document


class IDocumentRepository(ABC):
    @abstractmethod
    def save(self, document: Document) -> Document:
        """Persist a document and return the saved instance."""
```

```python
# domain/ports/ingestion_job_repository.py
from abc import ABC, abstractmethod


class IIngestionJobRepository(ABC):
    @abstractmethod
    def count_running(self, user_id: int) -> int:
        """Return number of running ingestion tasks for a user."""

    @abstractmethod
    def mark_running(self, user_id: int, task_id: str) -> None:
        """Register a task as running for a user."""

    @abstractmethod
    def mark_done(self, user_id: int, task_id: str) -> None:
        """Remove a task from the running set for a user."""
```

- [ ] **Step 4: Run tests and confirm they pass**

```bash
pytest tests/test_document_entity.py -v
```

Expected: `3 passed`

- [ ] **Step 5: Commit**

```bash
git add domain/ports/ tests/test_document_entity.py
git commit -m "feat: add domain port interfaces"
```

---

## Task 3: Mock Adapters — Downloader, Extractor, Embedding

**Files:**
- Create: `infrastructure/__init__.py`
- Create: `infrastructure/adapters/__init__.py`
- Create: `infrastructure/adapters/file_downloader_mock.py`
- Create: `infrastructure/adapters/text_extractor_mock.py`
- Create: `infrastructure/adapters/embedding_repository_mock.py`
- Create: `tests/test_mock_adapters.py`

- [ ] **Step 1: Write the failing tests**

```python
# tests/test_mock_adapters.py
from infrastructure.adapters.file_downloader_mock import FileDownloaderMock
from infrastructure.adapters.text_extractor_mock import TextExtractorMock
from infrastructure.adapters.embedding_repository_mock import EmbeddingRepositoryMock


def test_file_downloader_mock_returns_bytes():
    result = FileDownloaderMock().download("https://example.com/file.pdf")
    assert isinstance(result, bytes)
    assert len(result) > 0


def test_text_extractor_mock_returns_string():
    result = TextExtractorMock().extract(b"some content")
    assert isinstance(result, str)
    assert len(result) > 0


def test_embedding_repository_mock_returns_1536_floats():
    result = EmbeddingRepositoryMock().compute("some text")
    assert isinstance(result, list)
    assert len(result) == 1536
    assert all(isinstance(v, float) for v in result)


def test_embedding_repository_mock_values_in_range():
    result = EmbeddingRepositoryMock().compute("some text")
    assert all(-1.0 <= v <= 1.0 for v in result)
```

- [ ] **Step 2: Run tests to confirm they fail**

```bash
pytest tests/test_mock_adapters.py -v
```

Expected: `ModuleNotFoundError: No module named 'infrastructure'`

- [ ] **Step 3: Create adapters**

```python
# infrastructure/__init__.py
# (empty)
```

```python
# infrastructure/adapters/__init__.py
# (empty)
```

```python
# infrastructure/adapters/file_downloader_mock.py
from domain.ports.file_downloader import IFileDownloader


class FileDownloaderMock(IFileDownloader):
    def download(self, url: str) -> bytes:
        return b"mock file content"
```

```python
# infrastructure/adapters/text_extractor_mock.py
from domain.ports.text_extractor import ITextExtractor


class TextExtractorMock(ITextExtractor):
    def extract(self, content: bytes) -> str:
        return "extracted text from mock"
```

```python
# infrastructure/adapters/embedding_repository_mock.py
import random

from domain.ports.embedding_repository import IEmbeddingRepository

EMBEDDING_DIM = 1536


class EmbeddingRepositoryMock(IEmbeddingRepository):
    def compute(self, text: str) -> list[float]:
        return [random.uniform(-1.0, 1.0) for _ in range(EMBEDDING_DIM)]
```

- [ ] **Step 4: Run tests and confirm they pass**

```bash
pytest tests/test_mock_adapters.py -v
```

Expected: `4 passed`

- [ ] **Step 5: Commit**

```bash
git add infrastructure/ tests/test_mock_adapters.py
git commit -m "feat: add mock adapters for downloader, extractor and embedding"
```

---

## Task 4: Mock Adapters — Document Repository + Redis Job Repository

**Files:**
- Create: `infrastructure/adapters/document_repository_in_memory.py`
- Create: `infrastructure/adapters/ingestion_job_repository_redis.py`
- Create: `tests/test_ingestion_job_repository_redis.py`

Install `fakeredis` first (needed for Redis tests without a live Redis):

```bash
pip install fakeredis
```

- [ ] **Step 1: Write the failing tests**

```python
# tests/test_mock_adapters.py  (append to existing file)
from infrastructure.adapters.document_repository_in_memory import DocumentRepositoryInMemory
from domain.entities.document import Document


def _make_document():
    return Document(document_id=1, workspace_id=10, user_id=42, url="https://example.com/a.pdf")


def test_document_repository_save_assigns_id():
    repo = DocumentRepositoryInMemory()
    saved = repo.save(_make_document())
    assert saved.id is not None


def test_document_repository_save_increments_id():
    repo = DocumentRepositoryInMemory()
    first = repo.save(_make_document())
    second = repo.save(_make_document())
    assert second.id == first.id + 1


def test_document_repository_save_does_not_mutate_input():
    repo = DocumentRepositoryInMemory()
    doc = _make_document()
    repo.save(doc)
    assert doc.id is None  # original unchanged
```

```python
# tests/test_ingestion_job_repository_redis.py
import fakeredis
from infrastructure.adapters.ingestion_job_repository_redis import IngestionJobRepositoryRedis


def _make_repo() -> IngestionJobRepositoryRedis:
    client = fakeredis.FakeRedis()
    return IngestionJobRepositoryRedis(client)


def test_count_running_starts_at_zero():
    repo = _make_repo()
    assert repo.count_running(user_id=1) == 0


def test_mark_running_increments_count():
    repo = _make_repo()
    repo.mark_running(user_id=1, task_id="task-abc")
    assert repo.count_running(user_id=1) == 1


def test_mark_done_decrements_count():
    repo = _make_repo()
    repo.mark_running(user_id=1, task_id="task-abc")
    repo.mark_done(user_id=1, task_id="task-abc")
    assert repo.count_running(user_id=1) == 0


def test_multiple_tasks_counted_independently():
    repo = _make_repo()
    repo.mark_running(user_id=1, task_id="task-1")
    repo.mark_running(user_id=1, task_id="task-2")
    assert repo.count_running(user_id=1) == 2


def test_different_users_are_isolated():
    repo = _make_repo()
    repo.mark_running(user_id=1, task_id="task-1")
    repo.mark_running(user_id=1, task_id="task-2")
    assert repo.count_running(user_id=2) == 0


def test_mark_done_only_removes_specified_task():
    repo = _make_repo()
    repo.mark_running(user_id=1, task_id="task-1")
    repo.mark_running(user_id=1, task_id="task-2")
    repo.mark_done(user_id=1, task_id="task-1")
    assert repo.count_running(user_id=1) == 1
```

- [ ] **Step 2: Run tests to confirm they fail**

```bash
pytest tests/test_mock_adapters.py tests/test_ingestion_job_repository_redis.py -v
```

Expected: failures on the new tests only (`ModuleNotFoundError` for missing adapters)

- [ ] **Step 3: Create adapters**

```python
# infrastructure/adapters/document_repository_in_memory.py
from domain.entities.document import Document
from domain.ports.document_repository import IDocumentRepository


class DocumentRepositoryInMemory(IDocumentRepository):
    def __init__(self) -> None:
        self._store: dict[int, Document] = {}
        self._next_id = 1

    def save(self, document: Document) -> Document:
        if document.id is None:
            saved = document.model_copy(update={"id": self._next_id})
            self._next_id += 1
        else:
            saved = document
        self._store[saved.id] = saved
        return saved
```

```python
# infrastructure/adapters/ingestion_job_repository_redis.py
import redis

from domain.ports.ingestion_job_repository import IIngestionJobRepository


class IngestionJobRepositoryRedis(IIngestionJobRepository):
    def __init__(self, redis_client: redis.Redis) -> None:
        self._redis = redis_client

    def _key(self, user_id: int) -> str:
        return f"ingestion:running:{user_id}"

    def count_running(self, user_id: int) -> int:
        return self._redis.scard(self._key(user_id))

    def mark_running(self, user_id: int, task_id: str) -> None:
        self._redis.sadd(self._key(user_id), task_id)

    def mark_done(self, user_id: int, task_id: str) -> None:
        self._redis.srem(self._key(user_id), task_id)
```

- [ ] **Step 4: Run tests and confirm they pass**

```bash
pytest tests/test_mock_adapters.py tests/test_ingestion_job_repository_redis.py -v
```

Expected: `13 passed`

- [ ] **Step 5: Commit**

```bash
git add infrastructure/adapters/document_repository_in_memory.py \
        infrastructure/adapters/ingestion_job_repository_redis.py \
        tests/test_mock_adapters.py \
        tests/test_ingestion_job_repository_redis.py
git commit -m "feat: add in-memory document repo and Redis job repo adapter"
```

---

## Task 5: Document Ingestion Service

**Files:**
- Create: `services/__init__.py`
- Create: `services/document_ingestion_service.py`
- Create: `tests/test_document_ingestion_service.py`

- [ ] **Step 1: Write the failing tests**

```python
# tests/test_document_ingestion_service.py
from domain.entities.document import Document
from infrastructure.adapters.document_repository_in_memory import DocumentRepositoryInMemory
from infrastructure.adapters.embedding_repository_mock import EmbeddingRepositoryMock
from infrastructure.adapters.file_downloader_mock import FileDownloaderMock
from infrastructure.adapters.text_extractor_mock import TextExtractorMock
from services.document_ingestion_service import DocumentIngestionService


def _make_service() -> DocumentIngestionService:
    return DocumentIngestionService(
        file_downloader=FileDownloaderMock(),
        text_extractor=TextExtractorMock(),
        embedding_repository=EmbeddingRepositoryMock(),
        document_repository=DocumentRepositoryInMemory(),
    )


def _make_document() -> Document:
    return Document(
        document_id=1,
        workspace_id=10,
        user_id=42,
        url="https://example.com/file.pdf",
    )


def test_ingest_sets_text():
    result = _make_service().ingest(_make_document())
    assert result.text == "extracted text from mock"


def test_ingest_sets_embedding_of_correct_dimension():
    result = _make_service().ingest(_make_document())
    assert isinstance(result.embedding, list)
    assert len(result.embedding) == 1536


def test_ingest_sets_status_done():
    result = _make_service().ingest(_make_document())
    assert result.status == "done"


def test_ingest_persists_and_assigns_id():
    result = _make_service().ingest(_make_document())
    assert result.id is not None


def test_ingest_does_not_mutate_input():
    doc = _make_document()
    _make_service().ingest(doc)
    assert doc.text is None
    assert doc.status == "pending"
```

- [ ] **Step 2: Run tests to confirm they fail**

```bash
pytest tests/test_document_ingestion_service.py -v
```

Expected: `ModuleNotFoundError: No module named 'services'`

- [ ] **Step 3: Implement the service**

```python
# services/__init__.py
# (empty)
```

```python
# services/document_ingestion_service.py
import logging

from domain.entities.document import Document
from domain.ports.document_repository import IDocumentRepository
from domain.ports.embedding_repository import IEmbeddingRepository
from domain.ports.file_downloader import IFileDownloader
from domain.ports.text_extractor import ITextExtractor

logger = logging.getLogger(__name__)


class DocumentIngestionService:
    def __init__(
        self,
        file_downloader: IFileDownloader,
        text_extractor: ITextExtractor,
        embedding_repository: IEmbeddingRepository,
        document_repository: IDocumentRepository,
    ) -> None:
        self._file_downloader = file_downloader
        self._text_extractor = text_extractor
        self._embedding_repository = embedding_repository
        self._document_repository = document_repository

    def ingest(self, document: Document) -> Document:
        logger.info("Starting ingestion for document %s", document.document_id)
        content = self._file_downloader.download(document.url)
        text = self._text_extractor.extract(content)
        embedding = self._embedding_repository.compute(text)
        updated = document.model_copy(update={
            "text": text,
            "embedding": embedding,
            "status": "done",
        })
        return self._document_repository.save(updated)
```

- [ ] **Step 4: Run tests and confirm they pass**

```bash
pytest tests/test_document_ingestion_service.py -v
```

Expected: `5 passed`

- [ ] **Step 5: Commit**

```bash
git add services/ tests/test_document_ingestion_service.py
git commit -m "feat: add DocumentIngestionService"
```

---

## Task 6: Celery Task with Per-User Concurrency Guard

**Files:**
- Create: `workers/tasks/documents/process_document_ingestion.py`
- Delete: `workers/tasks/documents/document_indexing.py`
- Modify: `workers/tasks/__init__.py`
- Create: `tests/test_process_document_ingestion.py`

- [ ] **Step 1: Write the failing tests**

```python
# tests/test_process_document_ingestion.py
from unittest.mock import MagicMock, patch, call
import pytest


def _make_mock_job_repo(running_count: int = 0) -> MagicMock:
    repo = MagicMock()
    repo.count_running.return_value = running_count
    return repo


@patch("workers.tasks.documents.process_document_ingestion.IngestionJobRepositoryRedis")
@patch("workers.tasks.documents.process_document_ingestion.redis")
def test_task_calls_service_when_under_limit(mock_redis, mock_repo_cls):
    mock_repo = _make_mock_job_repo(running_count=0)
    mock_repo_cls.return_value = mock_repo

    from workers.tasks.documents.process_document_ingestion import process_document_ingestion
    process_document_ingestion.apply(kwargs={
        "document_id": 1,
        "workspace_id": 10,
        "document_url": "https://example.com/file.pdf",
        "user_id": 42,
        "document_name": "test.pdf",
    })

    mock_repo.mark_running.assert_called_once()
    mock_repo.mark_done.assert_called_once()


@patch("workers.tasks.documents.process_document_ingestion.IngestionJobRepositoryRedis")
@patch("workers.tasks.documents.process_document_ingestion.redis")
def test_mark_done_called_even_on_error(mock_redis, mock_repo_cls):
    mock_repo = _make_mock_job_repo(running_count=0)
    mock_repo_cls.return_value = mock_repo

    with patch("workers.tasks.documents.process_document_ingestion.DocumentIngestionService") as mock_svc_cls:
        mock_svc = MagicMock()
        mock_svc.ingest.side_effect = RuntimeError("boom")
        mock_svc_cls.return_value = mock_svc

        from workers.tasks.documents.process_document_ingestion import process_document_ingestion
        process_document_ingestion.apply(kwargs={
            "document_id": 1,
            "workspace_id": 10,
            "document_url": "https://example.com/file.pdf",
            "user_id": 42,
            "document_name": None,
        })

    mock_repo.mark_done.assert_called_once()
```

- [ ] **Step 2: Run tests to confirm they fail**

```bash
pytest tests/test_process_document_ingestion.py -v
```

Expected: `ModuleNotFoundError: No module named 'workers.tasks.documents.process_document_ingestion'`

- [ ] **Step 3: Create the task file**

```python
# workers/tasks/documents/process_document_ingestion.py
import gc
import logging
from typing import Optional

import redis
from celery import shared_task
from celery.exceptions import SoftTimeLimitExceeded

from domain.entities.document import Document
from infrastructure.adapters.document_repository_in_memory import DocumentRepositoryInMemory
from infrastructure.adapters.embedding_repository_mock import EmbeddingRepositoryMock
from infrastructure.adapters.file_downloader_mock import FileDownloaderMock
from infrastructure.adapters.ingestion_job_repository_redis import IngestionJobRepositoryRedis
from infrastructure.adapters.text_extractor_mock import TextExtractorMock
from services.document_ingestion_service import DocumentIngestionService
from settings import settings

MAX_CONCURRENT_PER_USER = 3
RETRY_COUNTDOWN = 30

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=None)
def process_document_ingestion(
    self,
    document_id: int,
    workspace_id: int,
    document_url: str,
    user_id: int,
    document_name: Optional[str],
) -> None:
    redis_client = redis.Redis.from_url(settings.CELERY_BROKER_URL)
    job_repo = IngestionJobRepositoryRedis(redis_client)

    if job_repo.count_running(user_id) >= MAX_CONCURRENT_PER_USER:
        logger.info(
            "User %s has %d running tasks, retrying in %ds",
            user_id, MAX_CONCURRENT_PER_USER, RETRY_COUNTDOWN,
        )
        raise self.retry(countdown=RETRY_COUNTDOWN)

    task_id: str = self.request.id or "local"
    job_repo.mark_running(user_id, task_id)

    document = Document(
        document_id=document_id,
        workspace_id=workspace_id,
        user_id=user_id,
        name=document_name,
        url=document_url,
    )

    try:
        service = DocumentIngestionService(
            file_downloader=FileDownloaderMock(),
            text_extractor=TextExtractorMock(),
            embedding_repository=EmbeddingRepositoryMock(),
            document_repository=DocumentRepositoryInMemory(),
        )
        service.ingest(document)
        logger.info("Successfully ingested document %s", document_id)
    except SoftTimeLimitExceeded:
        logger.exception("Timeout during ingestion of document %s", document_id)
    except Exception:
        logger.exception("Error during ingestion of document %s", document_id)
    finally:
        job_repo.mark_done(user_id, task_id)
        gc.collect()
```

- [ ] **Step 4: Update `workers/tasks/__init__.py` to import the new task (replaces the old import)**

```python
# workers/tasks/__init__.py
from .documents.process_document_ingestion import process_document_ingestion  # noqa: F401
```

- [ ] **Step 5: Delete the old task file**

```bash
git rm workers/tasks/documents/document_indexing.py
```

- [ ] **Step 6: Run tests and confirm they pass**

```bash
pytest tests/test_process_document_ingestion.py -v
```

Expected: `2 passed`

- [ ] **Step 7: Commit**

```bash
git add workers/tasks/documents/process_document_ingestion.py workers/tasks/__init__.py
git commit -m "feat: add Celery task with per-user concurrency guard (max 3)"
```

---

## Task 7: Web Layer — Schema and Endpoint

**Files:**
- Create: `web/__init__.py`
- Create: `web/schemas/__init__.py`
- Create: `web/schemas/document_schema.py`
- Create: `web/api/__init__.py`
- Create: `web/api/v1/__init__.py`
- Create: `web/api/v1/document_endpoint.py`
- Create: `tests/test_document_endpoint.py`

- [ ] **Step 1: Write the failing tests**

```python
# tests/test_document_endpoint.py
from unittest.mock import patch
from fastapi.testclient import TestClient

from app import app

client = TestClient(app)
AUTH_HEADER = {"Authorization": "token"}  # matches APP_AUTH_TOKEN default in settings.py


@patch("web.api.v1.document_endpoint.process_document_ingestion")
def test_ingest_returns_202(mock_task):
    mock_task.apply_async.return_value = None

    response = client.post(
        "/api/v1/documents/index",
        json={
            "document_id": 1,
            "workspace_id": 10,
            "document_url": "https://example.com/file.pdf",
            "user_id": 42,
            "document_name": "test.pdf",
        },
        headers=AUTH_HEADER,
    )

    assert response.status_code == 202
    mock_task.apply_async.assert_called_once()


@patch("web.api.v1.document_endpoint.process_document_ingestion")
def test_ingest_without_auth_returns_401(mock_task):
    response = client.post(
        "/api/v1/documents/index",
        json={
            "document_id": 1,
            "workspace_id": 10,
            "document_url": "https://example.com/file.pdf",
            "user_id": 42,
            "document_name": None,
        },
    )

    assert response.status_code == 401
    mock_task.apply_async.assert_not_called()


@patch("web.api.v1.document_endpoint.process_document_ingestion")
def test_ingest_dispatches_correct_kwargs(mock_task):
    mock_task.apply_async.return_value = None

    client.post(
        "/api/v1/documents/index",
        json={
            "document_id": 7,
            "workspace_id": 3,
            "document_url": "https://example.com/doc.pdf",
            "user_id": 99,
            "document_name": "doc.pdf",
        },
        headers=AUTH_HEADER,
    )

    call_kwargs = mock_task.apply_async.call_args.kwargs["kwargs"]
    assert call_kwargs["document_id"] == 7
    assert call_kwargs["workspace_id"] == 3
    assert call_kwargs["user_id"] == 99
    assert call_kwargs["document_url"] == "https://example.com/doc.pdf"
    assert call_kwargs["document_name"] == "doc.pdf"
```

- [ ] **Step 2: Run tests to confirm they fail**

```bash
pytest tests/test_document_endpoint.py -v
```

Expected: `ModuleNotFoundError: No module named 'web'`

- [ ] **Step 3: Create the web layer**

```python
# web/__init__.py
# (empty)
```

```python
# web/schemas/__init__.py
# (empty)
```

```python
# web/schemas/document_schema.py
from typing import Optional
from pydantic import BaseModel


class DocumentIngestionIn(BaseModel):
    document_id: int
    workspace_id: int
    document_url: str
    user_id: int
    document_name: Optional[str] = None
```

```python
# web/api/__init__.py
# (empty)
```

```python
# web/api/v1/__init__.py
# (empty)
```

```python
# web/api/v1/document_endpoint.py
from fastapi import APIRouter, Depends
from fastapi.openapi.models import APIKey
from starlette import status

from web.schemas.document_schema import DocumentIngestionIn
from webapp.auth_middleware import check_auth_token
from workers.tasks.documents.process_document_ingestion import process_document_ingestion

router = APIRouter(
    prefix="/api/v1/documents",
    tags=["Document ingestion"],
    responses={404: {"description": "Not found"}},
)


@router.post(
    "/index",
    summary="Download, extract and embed a document.",
    status_code=status.HTTP_202_ACCEPTED,
)
async def ingest_document(
    document_in: DocumentIngestionIn,
    api_key: APIKey = Depends(check_auth_token),
):
    process_document_ingestion.apply_async(
        kwargs={
            "document_id": document_in.document_id,
            "workspace_id": document_in.workspace_id,
            "document_url": document_in.document_url,
            "user_id": document_in.user_id,
            "document_name": document_in.document_name,
        },
        countdown=3,
        soft_time_limit=720,
        time_limit=720,
        priority=0,
    )
    return {"message": "Ingestion is running"}
```

- [ ] **Step 4: Run tests and confirm they pass**

```bash
pytest tests/test_document_endpoint.py -v
```

Expected: `3 passed`

- [ ] **Step 5: Commit**

```bash
git add web/ tests/test_document_endpoint.py
git commit -m "feat: add web layer schemas and document ingestion endpoint"
```

---

## Task 8: Wiring — Point App to New Endpoint

**Files:**
- Modify: `webapp/routes.py`

- [ ] **Step 1: Update `webapp/routes.py`**

Replace the existing content:

```python
# webapp/routes.py
from fastapi import APIRouter
from web.api.v1.document_endpoint import router as document_router

router = APIRouter()
router.include_router(document_router)
```

- [ ] **Step 2: Run the full test suite**

```bash
pytest tests/ -v
```

Expected: all tests pass. Verify the endpoint test still hits `/api/v1/documents/index`.

- [ ] **Step 3: Smoke-test the app starts**

```bash
python app.py
```

Expected: uvicorn starts without import errors on port 9002. Hit `http://localhost:9002/docs` to see the Swagger UI with the `POST /api/v1/documents/index` route.

- [ ] **Step 4: Commit**

```bash
git add webapp/routes.py
git commit -m "chore: wire app to new clean-architecture endpoint"
```

---

## Task 9: Remove Dead Code

**Files:**
- Delete: `webapp/endpoints/documents/document_ingestion.py`
- Delete: `commons/schemas/document_input.py`
- Delete: `memory.py`

- [ ] **Step 1: Run full tests before deleting**

```bash
pytest tests/ -v
```

Confirm all pass before touching anything.

- [ ] **Step 2: Delete the dead files**

```bash
git rm webapp/endpoints/documents/document_ingestion.py
git rm commons/schemas/document_input.py
git rm memory.py
```

- [ ] **Step 3: Run full tests again**

```bash
pytest tests/ -v
```

Expected: all tests still pass (nothing should import those files anymore).

- [ ] **Step 4: Commit**

```bash
git add -u
git commit -m "chore: remove old endpoint, schema and Memory singleton"
```
