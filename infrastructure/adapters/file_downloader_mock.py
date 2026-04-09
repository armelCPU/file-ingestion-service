from domain.ports.file_downloader import IFileDownloader


class FileDownloaderMock(IFileDownloader):
    def download(self, url: str) -> bytes:
        return b"mock file content"
