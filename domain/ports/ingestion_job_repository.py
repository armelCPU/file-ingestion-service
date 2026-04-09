from abc import ABC, abstractmethod


class IIngestionJobRepository(ABC):
    @abstractmethod
    def count_running(self, user_id: int) -> int:
        """Return number of running ingestion tasks for a user."""

    @abstractmethod
    def mark_running(self, user_id: int, task_id: str) -> None:
        """Register a task as running for a user."""

    @abstractmethod
    def mark_done(self, user_id: int, task_id: str) -> None:
        """Remove a task from the running set for a user."""
