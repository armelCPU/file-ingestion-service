# Python Technical Assessment — File Ingestion & Semantic Search

## Context

You are working on a RAG (Retrieval-Augmented Generation) service whose role is to ingest documents, compute their vector representations, and enable semantic search over them.

The project already has a clean architecture skeleton in place (entities, port interfaces, mock adapters, a service layer, a Celery task, and a FastAPI endpoint). Your job is to replace the mocks with real implementations and add a semantic search feature.

Read the [README](README.md) before starting — it explains the architecture, the layer structure, and how the pieces fit together.

---

## What is already provided

- `domain/entities/document.py` — the `Document` entity
- `domain/ports/` — all port interfaces (contracts you must implement)
- `infrastructure/adapters/*_mock.py` — mock adapters (to be replaced)
- `services/document_ingestion_service.py` — the ingestion orchestrator (do not modify)
- `workers/tasks/documents/process_document_ingestion.py` — the Celery task with per-user concurrency guard
- `web/api/v1/document_endpoint.py` — the ingestion endpoint (`POST /api/v1/documents/index`)

---

## Task 1 — Implement real ingestion adapters

Replace the four mock adapters with real implementations. Each adapter must implement its port interface (defined in `domain/ports/`).

### 1a. File downloader

**Port:** `IFileDownloader` (`domain/ports/file_downloader.py`)  
**Create:** `infrastructure/adapters/file_downloader_http.py`

Download the file from the given URL over HTTP and return its raw bytes.

### 1b. Text extractor

**Port:** `ITextExtractor` (`domain/ports/text_extractor.py`)  
**Create:** `infrastructure/adapters/text_extractor_pdf.py`

Extract plain text from the raw bytes of a PDF file. You may use any library of your choice (e.g. `pypdf`, `pdfminer.six`, `pymupdf`).

### 1c. Embedding repository

**Port:** `IEmbeddingRepository` (`domain/ports/embedding_repository.py`)  
**Create:** `infrastructure/adapters/embedding_repository_openai.py`

Call the OpenAI Embeddings API (`text-embedding-ada-002`) to compute a 1536-dimensional vector for a given text. The API key must be read from the environment (do not hardcode it).

### 1d. Document repository

**Port:** `IDocumentRepository` (`domain/ports/document_repository.py`)  
**Create:** `infrastructure/adapters/document_repository_sql.py`

Persist documents to PostgreSQL. You must store at minimum: `document_id`, `workspace_id`, `user_id`, `name`, `url`, `text`, `embedding`, `status`.

Choose the ORM or query library of your choice (e.g. SQLAlchemy, psycopg2, asyncpg).

### 1e. Wire the real adapters into the Celery task

Update `workers/tasks/documents/process_document_ingestion.py` to use your new adapters instead of the mocks.

---

## Task 2 — Semantic search endpoint

**Create:** `web/api/v1/search_endpoint.py`  
**Register it** in `webapp/routes.py`

### Endpoint specification

```
POST /api/v1/documents/search
Authorization: <token>

Request body:
{
  "query": "string",
  "workspace_id": int,
  "top_k": int  (optional, default 5)
}

Response:
{
  "results": [
    {
      "document_id": int,
      "document_name": "string",
      "score": float,
      "excerpt": "string"   // first 300 characters of the extracted text
    }
  ]
}
```

### Expected behaviour

1. Compute the embedding of the `query` text using `IEmbeddingRepository`.
2. Retrieve all documents for the given `workspace_id` from `IDocumentRepository`.
3. Rank them by **cosine similarity** between the query embedding and each document embedding.
4. Return the top `top_k` results, sorted by descending score.

You are free to add any methods to `IDocumentRepository` that you need (e.g. `list_by_workspace`).

---

## Constraints

- **Celery concurrency:** the worker pool runs with `--concurrency=4`.
- **Per-user task limit:** each user may have at most **3 tasks running simultaneously**. This guard is already implemented in the Celery task — do not remove it.
- All secrets (OpenAI API key, database URL) must be read from environment variables via `settings.py`.
- Do not modify `domain/` (entities and ports) unless you need to add methods to an existing port for Task 2.
- Do not modify `services/document_ingestion_service.py`.
- The mock adapters must remain untouched (they are used by the existing test suite).

---

## Evaluation criteria

| Area | What we look at |
|------|----------------|
| **Architecture** | Adapters implement their port interface correctly; no business logic leaks into the infrastructure layer |
| **Correctness** | Ingestion pipeline produces stored documents with text and embedding; search returns relevant results ranked by cosine similarity |
| **Code quality** | Clarity, naming, error handling (network failures, missing documents, API errors) |
| **Configuration** | No hardcoded secrets; environment variables used consistently |
| **Bonus** | Meaningful logging, graceful handling of non-PDF files, pagination on the search endpoint |

---

## Deliverable

A working Git branch with:
- The four real adapters implemented
- The search endpoint implemented and registered
- A short note in this file (or a separate `NOTES.md`) explaining any choices you made, trade-offs, and anything you would do differently given more time
