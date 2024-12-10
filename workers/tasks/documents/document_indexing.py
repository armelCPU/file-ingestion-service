import gc
import logging
from typing import Optional

from celery import shared_task
from celery.exceptions import SoftTimeLimitExceeded
from memory import Memory


memory = Memory.getInstance()


@shared_task(bind=True)
def process_document_ingestion(
    self,
    document_id: int,
    workspace_id: int,
    document_url: str,
    user_id: int,
    document_name: Optional[str],
) -> None:
    """
    Process a document and index its text and pages

    :param document_id:
    :param workspace_id:
    :param document_url:
    :param user_id:
    :param document_name:

    :return:
    """
    logging.info(
        f"Processing document ingestion of: {document_id} in workspace {workspace_id} for user {user_id}"
    )
    try:
        pass
    except SoftTimeLimitExceeded:
        logging.exception(f"Timeout Error for document: {document_id} ingestion")

    except Exception as e:
        logging.exception(f"Error during ingestion of: {document_id}")
    finally:
        gc.collect()
