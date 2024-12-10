from fastapi import APIRouter, Depends
from fastapi.openapi.models import APIKey
from starlette import status

from commons.schemas.document_input import DocumentIngestionIn
from memory import Memory
from webapp.auth_middleware import check_auth_token
from workers.tasks.documents.document_indexing import process_document_ingestion

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
    _ = process_document_ingestion.apply_async(
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

    return "Ingestion is running ..."
