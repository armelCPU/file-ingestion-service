from worker import celery_app


def get_task_info(task_id: str):
    """
    return task info for the given task_id
    """
    task_result = celery_app.AsyncResult(task_id)

    result = {
        "task_id": task_id,
        "task_status": task_result.status,
        "task_result": task_result.result,
    }

    return result
