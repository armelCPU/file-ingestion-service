# File Service
```commandline
celery -A worker.celery_app worker --loglevel=info --concurrency=3 --without-heartbeat --without-mingle --without-gossip -Q file_management_queue
```


Make sure packages are always with the correct version before merge.

## Purge the queue
```commandline
celery -A worker.celery_app purge -Q file_management_queue
```