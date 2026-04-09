from abc import ABC, abstractmethod


class ITextExtractor(ABC):
    @abstractmethod
    def extract(self, content: bytes) -> str:
        """Extract plain text from raw file content."""
