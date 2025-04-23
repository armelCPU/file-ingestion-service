import gc
import logging
import io
import requests
import tiktoken
import PyPDF2
import numpy as np
from celery.exceptions import SoftTimeLimitExceeded
from typing import Optional
import openai
from settings import settings
from worker import celery_app
from memory import Memory
from webapp.database.db import SessionLocal
from webapp.database.models import DocumentEmbedding, DocumentChunk, IngestionTask
from webapp.services.mock_openai import mock_embedding

memory = Memory.getInstance()

def _mark_task_status(document_id: int, user_id: int, status: str):
    try:
        db = SessionLocal()
        task = db.query(IngestionTask).filter(
            IngestionTask.document_id == document_id,
            IngestionTask.user_id == user_id,
            IngestionTask.status == "running"
        ).first()
        if task:
            task.status = status
            db.commit()
    except Exception as update_err:
        logging.exception(f"\u26a0\ufe0f Failed to update task status: {update_err}")
    finally:
        db.close()

def chunk_text(text, max_tokens=8191):
    encoding = tiktoken.encoding_for_model("text-embedding-ada-002")
    tokens = encoding.encode(text)
    chunks = []
    for i in range(0, len(tokens), max_tokens):
        chunk = tokens[i:i + max_tokens]
        chunk_text = encoding.decode(chunk)
        chunks.append(chunk_text)
    return chunks

@celery_app.task(bind=True)
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
    db = None
    try:
        logging.info(f"Downloading PDF from URL: {document_url}")
        response = requests.get(document_url)
        response.raise_for_status()

        with io.BytesIO(response.content) as pdf_file:
            reader = PyPDF2.PdfReader(pdf_file)
            text = ""
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text

        # Extract text
        if text.strip():
            chunks = chunk_text(text)
            logging.info(f"Total {len(chunks)} chunks")

            db = SessionLocal()
            # Save main document record
            doc_record = DocumentEmbedding(
                document_id=document_id,
                workspace_id=workspace_id,
                user_id=user_id,
                document_name=document_name,
                text=text
            )
            db.add(doc_record)
            db.commit()
            db.refresh(doc_record)

            # Generate and save embeddings per chunk
            for idx, chunk in enumerate(chunks):
                # Use mock or real embedding provider depending on MOCK_MODE
                if settings.MOCK_MODE:
                    chunk_embedding = mock_embedding(chunk)
                else:
                    openai.api_key = settings.OPENAI_API_KEY
                    res = openai.Embedding.create(
                        input=chunk,
                        model="text-embedding-ada-002"
                    )
                    chunk_embedding = res["data"][0]["embedding"]

                chunk_record = DocumentChunk(
                    document_id=document_id,
                    document_name=document_name,
                    user_id=user_id,
                    workspace_id=workspace_id,
                    chunk_index=idx,
                    text=chunk,
                    embedding=chunk_embedding
                )
                db.add(chunk_record)

                db.commit()
                logging.info("Document and chunks saved successfully")

    except SoftTimeLimitExceeded:
        logging.exception(f"Timeout Error for document: {document_id} ingestion")
        _mark_task_status(document_id, user_id, "failed")

    except Exception as e:
        logging.exception(f"Error during ingestion of: {document_id}")
        _mark_task_status(document_id, user_id, "failed")

    else:
        _mark_task_status(document_id, user_id, "completed")

    finally:
        if db:
           db.close()
        gc.collect()
