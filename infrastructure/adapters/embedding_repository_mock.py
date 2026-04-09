import random

from domain.ports.embedding_repository import IEmbeddingRepository

EMBEDDING_DIM = 1536


class EmbeddingRepositoryMock(IEmbeddingRepository):
    """Mock embedding repository that returns a random 1536-dim vector. Not deterministic."""

    def compute(self, text: str) -> list[float]:
        return [random.uniform(-1.0, 1.0) for _ in range(EMBEDDING_DIM)]
