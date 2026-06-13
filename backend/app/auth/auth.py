import os
import secrets

from fastapi import Depends, HTTPException, Request
from fastapi.security import APIKeyHeader

_api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

_OPEN_PATHS = {"/health"}


def _check_api_key(api_key: str | None) -> None:
    server_key = os.environ.get("API_KEY")
    if not server_key:
        raise HTTPException(status_code=500, detail="Server API key not configured")
    if not api_key or not secrets.compare_digest(api_key, server_key):
        raise HTTPException(status_code=401, detail="Invalid API key")


async def require_api_key(
    request: Request,
    api_key: str | None = Depends(_api_key_header),
) -> None:
    if request.url.path in _OPEN_PATHS:
        return
    _check_api_key(api_key)
