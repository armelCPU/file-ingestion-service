from abc import ABC, abstractmethod


class IEmbeddingRepository(ABC):
    @abstractmethod
    def compute(self, text: str) -> list[float]:
        """Compute the embedding vector for a given text."""
