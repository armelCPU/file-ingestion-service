import logging

from domain.entities.document import Document
from domain.ports.document_repository import IDocumentRepository
from domain.ports.embedding_repository import IEmbeddingRepository
from domain.ports.file_downloader import IFileDownloader
from domain.ports.text_extractor import ITextExtractor

logger = logging.getLogger(__name__)


class DocumentIngestionService:
    """Orchestrates the full ingestion pipeline: download → extract → embed → save."""

    def __init__(
        self,
        file_downloader: IFileDownloader,
        text_extractor: ITextExtractor,
        embedding_repository: IEmbeddingRepository,
        document_repository: IDocumentRepository,
    ) -> None:
        self._file_downloader = file_downloader
        self._text_extractor = text_extractor
        self._embedding_repository = embedding_repository
        self._document_repository = document_repository

    def ingest(self, document: Document) -> Document:
        """Download, extract text, compute embedding and persist the document."""
        logger.info("Starting ingestion for document %s", document.document_id)
        content = self._file_downloader.download(document.url)
        text = self._text_extractor.extract(content)
        embedding = self._embedding_repository.compute(text)
        updated = document.model_copy(update={
            "text": text,
            "embedding": embedding,
            "status": "done",
        })
        return self._document_repository.save(updated)
