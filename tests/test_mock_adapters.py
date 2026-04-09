from infrastructure.adapters.file_downloader_mock import FileDownloaderMock
from infrastructure.adapters.text_extractor_mock import TextExtractorMock
from infrastructure.adapters.embedding_repository_mock import EmbeddingRepositoryMock
from infrastructure.adapters.document_repository_in_memory import DocumentRepositoryInMemory
from domain.entities.document import Document


def test_file_downloader_mock_returns_bytes():
    result = FileDownloaderMock().download("https://example.com/file.pdf")
    assert isinstance(result, bytes)
    assert len(result) > 0


def test_text_extractor_mock_returns_string():
    result = TextExtractorMock().extract(b"some content")
    assert isinstance(result, str)
    assert len(result) > 0


def test_embedding_repository_mock_returns_1536_floats():
    result = EmbeddingRepositoryMock().compute("some text")
    assert isinstance(result, list)
    assert len(result) == 1536
    assert all(isinstance(v, float) for v in result)


def test_embedding_repository_mock_values_in_range():
    result = EmbeddingRepositoryMock().compute("some text")
    assert all(-1.0 <= v <= 1.0 for v in result)


def _make_document():
    return Document(document_id=1, workspace_id=10, user_id=42, url="https://example.com/a.pdf")


def test_document_repository_save_assigns_id():
    repo = DocumentRepositoryInMemory()
    saved = repo.save(_make_document())
    assert saved.id is not None


def test_document_repository_save_increments_id():
    repo = DocumentRepositoryInMemory()
    first = repo.save(_make_document())
    second = repo.save(_make_document())
    assert second.id == first.id + 1


def test_document_repository_save_does_not_mutate_input():
    repo = DocumentRepositoryInMemory()
    doc = _make_document()
    repo.save(doc)
    assert doc.id is None  # original unchanged
