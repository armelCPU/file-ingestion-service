import os
from typing import List

from pydantic import AnyHttpUrl
from envparse import env


class BaseConfig:
    APP_NAME: str = env("APP_NAME", "Data Service Pipeline")
    APP_DESCRIPTION: str = env("APP_DESCRIPTION", "Data Service Pipeline")
    APP_BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = ["*"]
    APP_VERSION: str = env("APP_VERSION", "1.0.0")
    # APP_AUTH_TOKEN: str = env("APP_AUTH_TOKEN", "token")

    SWAGGER_UI: bool = env("SWAGGER_UI", True)

    # MongoDB config
    MONGO_HOST = env("MONGO_HOST", "localhost")
    MONGO_PORT = env("MONGO_PORT", 27017, cast=int)
    MONGO_USERNAME = env("MONGO_USERNAME", "user")
    MONGO_PASSWORD = env("MONGO_PASSWORD", "user")
    MONGO_DATABASE = env("MONGO_DATABASE", "qualitia")

    CELERY_BROKER_URL: str = env(
        "CELERY_BROKER_URL", "amqp://guest:guest@localhost:5672//"
    )
    CELERY_RESULT_BACKEND: str = env("CELERY_RESULT_BACKEND", None)

    if CELERY_RESULT_BACKEND is None or CELERY_RESULT_BACKEND == "":
        CELERY_RESULT_BACKEND = (
            f"mongodb://{MONGO_USERNAME}:{MONGO_PASSWORD}@{MONGO_HOST}:{MONGO_PORT}"
        )

    # OCR configuration
    MEANINGFUL_MODEL = f"{os.getcwd()}/resources/meaningful_model.pickle"

    TMP_DIR = env("TMP_DIR", "/tmp/")
    ENV = env("ENV", "local")
    IMAGE_DPI = env("IMAGE_DPI", 150, cast=int)
    OCR_MIN_NB_TOKEN_IN_PAGE = env("OCR_MIN_NB_TOKEN_IN_PAGE", 10, cast=int)
    OCR_MIN_THRESHOLD_ON_DOC = env("OCR_MIN_THRESHOLD_ON_DOC", 0.25, cast=float)

    # Elastic Config
    ES_HOST = env("ES_HOST", "localhost")
    ES_PORT = env("ES_PORT", 9200, cast=int)
    ES_USERNAME = env("ES_USERNAME", "elastic")
    ES_PASSWORD = env("ES_PASSWORD", "Armel123456")
    ES_CERTIFICATE = env("ES_CERTIFICATE", None)
    ES_INSERT_BATCH_SIZE = env("ES_INSERT_BATCH_SIZE", 9200, cast=int)
    ES_RETRIEVE_BATCH_SIZE = env("ES_RETRIEVE_BATCH_SIZE", 9200, cast=int)
    ES_TIMEOUT = env("ES_TIMEOUT", 300, cast=int)

    COMMON_AUTH_URL = env("COMMON_AUTH_URL", "http://localhost:8001")
    GATEWAY_URL = env("GATEWAY_URL", "http://localhost:8000")
    BROADCAST_URL = env("BROADCAST_URL", "http://localhost:8003")

    # Storage location config.
    SAAS_MODE = env("SAAS_MODE", 0, cast=int)
    GCP_BUCKET = env("GCP_BUCKET", "kumbu_local")
    GCP_ACCESS_KEY = env("GCP_ACCESS_KEY", "")

    if GCP_ACCESS_KEY != "":
        with open("gcp_access_key.json", "w") as google_file:
            google_file.write(GCP_ACCESS_KEY)

    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "gcp_access_key.json"

    # Indexing time out
    INDEX_TIMEOUT = env("INDEX_TIMEOUT", default=3600 * 24, cast=int)
    
    BATCH_SIZE = env("BATCH_SIZE", default=30, cast=int)
    
    # Redis config
    REDIS_HOST = env("REDIS_HOST", "localhost")
    REDIS_PORT = env("REDIS_PORT", 6379, cast=int)

    # Max number of upload per user
    MAX_UPLOAD_PER_USER = env("MAX_UPLOAD_PER_USER", 4, cast=int)


settings = BaseConfig()
