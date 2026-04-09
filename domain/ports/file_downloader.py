from abc import ABC, abstractmethod


class IFileDownloader(ABC):
    @abstractmethod
    def download(self, url: str) -> bytes:
        """Download file content from a URL."""
