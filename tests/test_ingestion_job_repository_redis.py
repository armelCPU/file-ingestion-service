import fakeredis
from infrastructure.adapters.ingestion_job_repository_redis import IngestionJobRepositoryRedis


def _make_repo() -> IngestionJobRepositoryRedis:
    client = fakeredis.FakeRedis()
    return IngestionJobRepositoryRedis(client)


def test_count_running_starts_at_zero():
    repo = _make_repo()
    assert repo.count_running(user_id=1) == 0


def test_mark_running_increments_count():
    repo = _make_repo()
    repo.mark_running(user_id=1, task_id="task-abc")
    assert repo.count_running(user_id=1) == 1


def test_mark_done_decrements_count():
    repo = _make_repo()
    repo.mark_running(user_id=1, task_id="task-abc")
    repo.mark_done(user_id=1, task_id="task-abc")
    assert repo.count_running(user_id=1) == 0


def test_multiple_tasks_counted_independently():
    repo = _make_repo()
    repo.mark_running(user_id=1, task_id="task-1")
    repo.mark_running(user_id=1, task_id="task-2")
    assert repo.count_running(user_id=1) == 2


def test_different_users_are_isolated():
    repo = _make_repo()
    repo.mark_running(user_id=1, task_id="task-1")
    repo.mark_running(user_id=1, task_id="task-2")
    assert repo.count_running(user_id=2) == 0


def test_mark_done_only_removes_specified_task():
    repo = _make_repo()
    repo.mark_running(user_id=1, task_id="task-1")
    repo.mark_running(user_id=1, task_id="task-2")
    repo.mark_done(user_id=1, task_id="task-1")
    assert repo.count_running(user_id=1) == 1
