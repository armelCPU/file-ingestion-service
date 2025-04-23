import os
from dotenv import load_dotenv
from typing import List

from pydantic import AnyHttpUrl
from envparse import env

load_dotenv()

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

    # OPENAI
    OPENAI_API_KEY: str = env("OPENAI_API_KEY", default=None)

    # PostgreSQL
    POSTGRES_USER: str = env("POSTGRES_USER", "rag_user")
    POSTGRES_PASSWORD: str = env("POSTGRES_PASSWORD", "rag_pass")
    POSTGRES_DB: str = env("POSTGRES_DB", "rag_db")
    POSTGRES_HOST: str = env("POSTGRES_HOST", "postgres")
    POSTGRES_PORT: int = env("POSTGRES_PORT", 5432, cast=int)

    # Mode mock
    MOCK_MODE: bool = os.getenv("MOCK_MODE", "false").lower() == "true"

settings = BaseConfig()
