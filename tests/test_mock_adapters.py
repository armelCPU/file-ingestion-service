from infrastructure.adapters.file_downloader_mock import FileDownloaderMock
from infrastructure.adapters.text_extractor_mock import TextExtractorMock
from infrastructure.adapters.embedding_repository_mock import EmbeddingRepositoryMock


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
