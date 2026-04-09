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
    """Process a document: download, extract text, compute embeddings, persist."""
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
