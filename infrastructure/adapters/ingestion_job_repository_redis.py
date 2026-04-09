import redis

from domain.ports.ingestion_job_repository import IIngestionJobRepository


class IngestionJobRepositoryRedis(IIngestionJobRepository):
    """Tracks running ingestion tasks per user using a Redis set."""

    def __init__(self, redis_client: redis.Redis) -> None:
        self._redis = redis_client

    def _key(self, user_id: int) -> str:
        return f"ingestion:running:{user_id}"

    def count_running(self, user_id: int) -> int:
        """Return the number of running tasks for the given user."""
        return self._redis.scard(self._key(user_id))

    def mark_running(self, user_id: int, task_id: str) -> None:
        """Add task_id to the user's running set."""
        self._redis.sadd(self._key(user_id), task_id)

    def mark_done(self, user_id: int, task_id: str) -> None:
        """Remove task_id from the user's running set."""
        self._redis.srem(self._key(user_id), task_id)
