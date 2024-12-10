import os
from typing import List

from pydantic import AnyHttpUrl
from envparse import env


class BaseConfig:
    APP_NAME: str = env("APP_NAME", "File service")
    APP_DESCRIPTION: str = env("APP_DESCRIPTION", "File service")
    APP_BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = ["*"]
    APP_VERSION: str = env("APP_VERSION", "1.0.0")
    APP_AUTH_TOKEN: str = env("APP_AUTH_TOKEN", "token")

    SWAGGER_UI: bool = env("SWAGGER_UI", True)

    # REDIS
    REDIS_HOST = env("REDIS_HOST", "localhost")
    REDIS_PORT = env("REDIS_PORT", 6379, cast=int)

    CELERY_BROKER_URL: str = env(
        "CELERY_BROKER_URL",
        "redis://localhost",
    )
    CELERY_RESULT_BACKEND: str = env(
        "CELERY_RESULT_BACKEND", f"redis://{REDIS_HOST}:{REDIS_PORT}/1"
    )

    TMP_DIR = env("TMP_DIR", "/tmp/")
    ENV = env("ENV", "local")

    # Max number of upload per user
    MAX_UPLOAD_PER_USER = env("MAX_UPLOAD_PER_USER", 4, cast=int)


settings = BaseConfig()
