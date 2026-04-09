from fastapi import APIRouter
from web.api.v1.document_endpoint import router as document_router

router = APIRouter()
router.include_router(document_router)
