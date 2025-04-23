from fastapi import APIRouter
from webapp.endpoints.documents.document_ingestion import router as document_router
from webapp.endpoints.search.search_endopoint import router as search_router

router = APIRouter()
# Include document ingestion routes
router.include_router(document_router)

# Include search routes
router.include_router(search_router)
