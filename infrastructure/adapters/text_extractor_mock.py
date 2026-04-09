from domain.ports.text_extractor import ITextExtractor


class TextExtractorMock(ITextExtractor):
    def extract(self, content: bytes) -> str:
        return "extracted text from mock"
