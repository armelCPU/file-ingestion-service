import sys

import uvicorn as uvicorn
import logging
from fastapi import FastAPI, Request
from fastapi.openapi.utils import get_openapi
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse

from webapp.routes import router
from settings import settings

# Get the logger for Daphne
daphne_logger = logging.getLogger("daphne")

# Get the root logger
root_logger = logging.getLogger()

# Set the log level for the root logger
root_logger.setLevel(logging.INFO)

# Add handlers from Daphne's logger to the root logger
for handler in daphne_logger.handlers:
    root_logger.addHandler(handler)

# Optionally, you can configure additional handlers or formatters for the root logger if needed

# Example: Add a StreamHandler to print logs to stdout
stdout_handler = logging.StreamHandler(sys.stdout)
stdout_handler.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
stdout_handler.setFormatter(formatter)
root_logger.addHandler(stdout_handler)
root_logger.addHandler(stdout_handler)

app = FastAPI(
    title=settings.APP_NAME,
    description=settings.APP_DESCRIPTION,
    version=settings.APP_VERSION,
    responses={
        401: {
            "description": "Not authenticated.",
            "content": {
                "application/json": {"example": {"detail": "Not authenticated"}}
            },
        }
    },
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.APP_BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description=settings.APP_DESCRIPTION,
        routes=app.routes,
    )
    openapi_schema["info"]["x-logo"] = {
        "url": "https://fastapi.tiangolo.com/img/logo-margin/logo-teal.png"
    }
    app.openapi_schema = openapi_schema
    return app.openapi_schema


if settings.SWAGGER_UI:
    app.openapi = custom_openapi


@app.route("/")
def default(request: Request):
    return JSONResponse("Welcome to File Service")


if settings.ENV == "local":
    if __name__ == "__main__":
        uvicorn.run("app:app", port=9002, reload=True)
