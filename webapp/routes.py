from fastapi import APIRouter
from webapp.endpoints.documents.document_ingestion import router as document_router

router = APIRouter()
router.include_router(document_router)
