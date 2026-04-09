from abc import ABC, abstractmethod

from domain.entities.document import Document


class IDocumentRepository(ABC):
    @abstractmethod
    def save(self, document: Document) -> Document:
        """Persist a document and return the saved instance."""
