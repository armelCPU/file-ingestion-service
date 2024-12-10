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

# Contexte

Tu développes un service de RAG dont la vocation est d'ingérer des fichiers.
L'ingestion est implémentée dans des tâches Celery qui prennent en paramètre le user_id, notamment. Un utilisateur peut lancer l'upload de N fichiers en même temps.
L'API d'OpenAI est utilisée pour calculer les embeddings de chaque document. Ces embeddings et le texte sont stockés dans PostgreSQL.
- La concurrence des workers Celery est de 4.
- Chaque utilisateur ne peut pas avoir plus de 3 tâches qui s'exécutent en même temps.

# TODO :
Implémenter une version mockée de l'API et du worker dans le framework Python de ton choix.
 - Bonus : Créer un endpoint pour implémenter la recherche sémantique dans la base des fichiers.

