from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from fastapi.openapi.models import APIKey
from starlette import status

from settings import settings
from memory import Memory
from commons.schemas.document_input import DocumentIngestionIn
from webapp.auth_middleware import check_auth_token
from webapp.database.db import SessionLocal
from webapp.database.models import IngestionTask, TaskStatus
from workers.tasks.documents.document_indexing import process_document_ingestion

import logging

memory = Memory.getInstance()

router = APIRouter(
    prefix="/api/v1/documents",
    tags=["Document ingestion"],
    responses={404: {"description": "Not found"}},
)


@router.post(
    "/index",
    summary="Index document, create pages and index, index document text and create word coordinates.",
    status_code=status.HTTP_200_OK,
    response_description="Ingest document",
)
async def ingest_document(
    document_in: DocumentIngestionIn, api_key: APIKey = Depends(check_auth_token)
):
    logging.info("Received document ingestion request")
    logging.info(f"document_id={document_in.document_id}")
    logging.info(f"document_url={document_in.document_url}")

    db = SessionLocal()
    try:
        # Check the number of currently running tasks for this user
        logging.info("Checking task quota for user")
        active_tasks = db.query(IngestionTask).filter(
            IngestionTask.user_id == document_in.user_id,
            IngestionTask.status == TaskStatus.running
        ).count()

        if active_tasks >= 3:
            logging.warning(f"User {document_in.user_id} has too many active tasks")
            return JSONResponse(
                status_code=429,
                content={"message": "Limit of 3 concurrent tasks reached."}
            )

        # Launch the Celery task for document ingestion
        result = process_document_ingestion.apply_async(
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
        logging.info(f"Celery task launched: task_id={result.id}")

        # Register the task in the ingestion_tasks table
        new_task = IngestionTask(
            task_id=result.id,
            user_id=document_in.user_id,
            document_id=document_in.document_id,
            status=TaskStatus.running
        )
        db.add(new_task)
        db.commit()

        return JSONResponse(content={"message": "Ingestion started successfully", "task_id": result.id})

    except Exception as e:
        logging.exception("Failed to launch document ingestion task")
        return JSONResponse(
            status_code=500,
            content={"message": "Failed to launch ingestion task", "error": str(e)},
        )
    finally:
        db.close()