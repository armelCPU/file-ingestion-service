from fastapi import APIRouter, Depends
from fastapi.security.api_key import APIKey
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
