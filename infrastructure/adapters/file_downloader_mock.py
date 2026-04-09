from domain.ports.file_downloader import IFileDownloader


class FileDownloaderMock(IFileDownloader):
    """Mock file downloader that returns fixed content regardless of URL."""

    def download(self, url: str) -> bytes:
        return b"mock file content"
