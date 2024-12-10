from celery import Celery
from kombu import Exchange, Queue

from settings import settings

celery_app = Celery(
    "file_worker",
    broker_heartbeat=0,
    backend=settings.CELERY_RESULT_BACKEND,
    broker=settings.CELERY_BROKER_URL,
    include=["workers.tasks"],
)
celery_app.conf.update(task_track_started=True)
celery_app.conf.update(result_persistent=True)
celery_app.conf.update(ignore_result=False)
celery_app.conf.update(max_retries=3)
celery_app.conf.update(default_retry_delay=30)
celery_app.conf.update(worker_send_task_events=True)
celery_app.conf.update(task_send_sent_event=True)
celery_app.conf.update(broker_connection_retry_on_startup=True)
celery_app.conf.update(broker_pool_limit=None)
celery_app.conf.update(task_time_limit=3600)
celery_app.conf.update(task_soft_time_limit=3600)
celery_app.conf.update(worker_cancel_long_running_tasks_on_connection_loss=True)
celery_app.conf.update(worker_prefetch_multiplier=1)
celery_app.conf.update(timezone="Europe/Paris")
celery_app.conf.update(result_expires=60 * 60 * 24)
celery_app.conf.update(broker_connection_timeout=30.0)
celery_app.conf.update(broker_heartbeat=0)
celery_app.conf.update(
    broker_transport_options={
        "max_retries": 3,
        "interval_start": 0,
        "interval_step": 0.2,
        "interval_max": 0.5,
        "retry_policy": {"timeout": 5.0},
        "visibility_timeout": 43200,
        "socket_keepalive": True,
        "health_check_interval": 4,
    }
)

celery_app.conf.update(
    task_queues={
        "file_queue": {
            "queue_arguments": {"x-max-priority": 10},
        }
    }
)

celery_app.conf.update(task_routes={"workers.*": {"queue": "file_queue"}})
