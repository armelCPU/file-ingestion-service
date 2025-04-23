# Implémentation du service RAG

## Objectif

Ce service FastAPI permet :
- l’ingestion de fichiers PDF,
- le découpage en chunks,
- la génération d'embeddings via OpenAI (ou en mode mocké),
- le stockage dans PostgreSQL,
- la recherche sémantique via un endpoint `/search`.

## Fonctionnalités Implémentées

- Ingestion de fichiers PDF via une tâche Celery
- Enregistrement dans PostgreSQL (`document_embeddings`, `document_chunks`, `ingestion_tasks`)
- Limite à 3 tâches Celery simultanées par utilisateur
- Génération d’embeddings (OpenAI ou mock)
- Endpoint de recherche sémantique
- Mode `MOCK_MODE` activable pour tests sans OpenAI
- Docker + Docker Compose
- Makefile (build, up,, down, logs, ...)

## Fichiers Clés

`document_ingestion.py`: Endpoint pour démarrer l'ingestion
`document_indexing.py`: Logique Celery pour découper et indexer le document
`search_endpoint.py`: Endpoint de recherche sémantique
`mock_openai.py`: Génère des embeddings simulés
`docker-compose.yml`: Conteneurs FastAPI, Celery, Redis, PostgreSQL
`Makefile`: Commandes simplifiées (`make docker-build`, ` make docker-up`, ` make docker-logs CONTAINER=<Nom_container>`)

## Fichier .env requis

APP_AUTH_TOKEN=token
REDIS_HOST=redis
REDIS_PORT=6379
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/1
POSTGRES_USER=rag_user
POSTGRES_PASSWORD=rag_pass
POSTGRES_DB=rag_db
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
OPENAI_API_KEY=sk-...
MOCK_MODE=false

## Lancer le projet
```bash
# Construction des images
make docker-build

# Lancement des conteneurs
make docker-up

# Logs d'un conteneur
make docker-logs CONTAINER=rag_backend # Permet d'afficher les logs de l’API FastAPI (endpoints /index, /search, etc.).
make docker-logs CONTAINER=rag_celery # Affiche les logs des tâches Celery d’ingestion et de traitement des documents (process_document_ingestion).
```

## Initialiser la base de données
- Pour initialiser les tables dans la base de données, exécutez la commande suivante dans le conteneur Docker :

```bash
docker exec -it rag_backend bash -c "PYTHONPATH=. python3 webapp/database/init_db.py"
```

## Tester l’ingestion d’un document
Endpoint POST /api/v1/documents/index

{
  "document_id": 1,
  "workspace_id": 1,
  "document_url": "https://www.conseil-constitutionnel.fr/sites/default/files/as/root/bank_mm/constitution/constitution.pdf",
  "user_id": 1,
  "document_name": "constitution.pdf"
}

## Effectuer une recherche sémantique
Endpoint POST /search
{
  "question": "Exemple de question à poser : Quels sont les droits fondamentaux garantis par la République?",
  "user_id": 1
}
- La réponse retourne les 5 meilleurs extraits classés par similarité cosinus :
    - document_id
    - document_name
    - chunk_index
    - score (cosine)
    - excerpt (texte extrait)
    - mock_used (true/false)

## Mode Mock
En développement, il est possible de mocker les embeddings OpenAI pour éviter les appels réels à l’API :
MOCK_MODE=true

##  Nettoyage
Arrêt des conteneurs et suppression des volumes
make docker-down
