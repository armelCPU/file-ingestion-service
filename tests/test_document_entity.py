from domain.entities.document import Document
from domain.ports.file_downloader import IFileDownloader
from domain.ports.text_extractor import ITextExtractor
from domain.ports.embedding_repository import IEmbeddingRepository
from domain.ports.document_repository import IDocumentRepository
from domain.ports.ingestion_job_repository import IIngestionJobRepository


def test_document_default_status_is_pending():
    doc = Document(document_id=1, workspace_id=10, user_id=42, url="https://example.com/a.pdf")
    assert doc.status == "pending"


def test_document_optional_fields_default_to_none():
    doc = Document(document_id=1, workspace_id=10, user_id=42, url="https://example.com/a.pdf")
    assert doc.id is None
    assert doc.name is None
    assert doc.text is None
    assert doc.embedding is None


def test_ports_are_importable():
    assert IFileDownloader
    assert ITextExtractor
    assert IEmbeddingRepository
    assert IDocumentRepository
    assert IIngestionJobRepository
