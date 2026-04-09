from domain.entities.document import Document
from domain.ports.document_repository import IDocumentRepository


class DocumentRepositoryInMemory(IDocumentRepository):
    """In-memory document store. Each instance has its own isolated state."""

    def __init__(self) -> None:
        self._store: dict[int, Document] = {}
        self._next_id = 1

    def save(self, document: Document) -> Document:
        if document.id is None:
            saved = document.model_copy(update={"id": self._next_id})
            self._next_id += 1
        else:
            saved = document
        self._store[saved.id] = saved
        return saved
