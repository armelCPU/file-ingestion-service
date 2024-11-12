import os
from typing import List

from pydantic import AnyHttpUrl
from envparse import env


class BaseConfig:
    APP_NAME: str = env("APP_NAME", "File service")
    APP_DESCRIPTION: str = env("APP_DESCRIPTION", "File service"")
    APP_BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = ["*"]
    APP_VERSION: str = env("APP_VERSION", "1.0.0")
    APP_AUTH_TOKEN: str = env("APP_AUTH_TOKEN", "token")

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


    TMP_DIR = env("TMP_DIR", "/tmp/")
    ENV = env("ENV", "local")


    COMMON_AUTH_URL = env("COMMON_AUTH_URL", "http://localhost:8001")

    # Max number of upload per user
    MAX_UPLOAD_PER_USER = env("MAX_UPLOAD_PER_USER", 4, cast=int)


settings = BaseConfig()
