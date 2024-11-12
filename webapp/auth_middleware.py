import re

import requests
from fastapi import Security, HTTPException
from fastapi.security import APIKeyHeader
from starlette.status import HTTP_401_UNAUTHORIZED

from settings import settings

api_key_header = APIKeyHeader(name="Authorization", auto_error=False)


def check_auth_token(authorization_header: str = Security(api_key_header)):
    """
    A token middleware which helps to check is a Token is given in the query params.

    :param authorization_header:
    :return:
    """
    if authorization_header:
        token = re.sub("Bearer ", "", authorization_header)
        if not token or token == "undefined":
            raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail="Forbidden")

        # Verify the token
        res = requests.post(
            f"{settings.COMMON_AUTH_URL}/auth/verify", data={"token": token}
        )
        if res.status_code != 200:
            raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail="Forbidden")

        verified_token = res.json()["token"]
        return verified_token
    else:
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail="Forbidden")
