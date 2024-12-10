from fastapi import Security, HTTPException
from fastapi.security import APIKeyHeader
from starlette.status import HTTP_401_UNAUTHORIZED

from settings import settings

api_key_header = APIKeyHeader(name="Authorization", auto_error=False)


def check_auth_token(
    api_key_header: str = Security(api_key_header),
):
    """
    Middleware for checking if the user has access to the request resource.

    :param api_key_header:
    :return:
    """
    if api_key_header == settings.APP_AUTH_TOKEN:
        return api_key_header
    else:
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail="Forbidden")
