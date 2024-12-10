# File Service
## Run App
```commandline
python app.py
```

## Run celery
```commandline
celery -A worker.celery_app worker --loglevel=info --concurrency=3 --without-heartbeat --without-mingle --without-gossip -Q file_queue
```

## Purge the queue
```commandline
celery -A worker.celery_app purge -Q file_queue
```