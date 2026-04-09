from domain.ports.text_extractor import ITextExtractor


class TextExtractorMock(ITextExtractor):
    """Mock text extractor that returns a fixed string regardless of input."""

    def extract(self, content: bytes) -> str:
        return "extracted text from mock"
