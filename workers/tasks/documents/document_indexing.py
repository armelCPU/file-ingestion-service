import logging

import requests
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
) -> None:
    """
    Process a document and index its text and pages

    :param document_uuid:
    :param document_owner:
    :param document_workspace_min:
    :param user_id:
    :return:
    """
    logging.info(f"Processing document ingestion of: {document_uuid}")


    except SoftTimeLimitExceeded:
        publish_progression(
       
        logging.exception(f"Timeout Error for document: {document_uuid} ingestion")

    except Exception as e:
        
        logging.exception(f"Error during ingestion of: {document_uuid}")
    finally:
        gc.collect()
