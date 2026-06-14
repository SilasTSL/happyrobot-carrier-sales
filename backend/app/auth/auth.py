import os
import secrets

from fastapi import Depends, HTTPException, Request
from fastapi.security import APIKeyHeader

_api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

_OPEN_PATHS = {"/health"}

# All /api/ routes use JWT auth instead of the API key — skip the check for them.
_OPEN_PREFIXES = ("/api/",)


def _matches(key: str | None, env_var: str) -> bool:
    server_key = os.environ.get(env_var)
    return bool(server_key and key and secrets.compare_digest(key, server_key))


async def require_api_key(
    request: Request,
    api_key: str | None = Depends(_api_key_header),
) -> None:
    path = request.url.path
    if path in _OPEN_PATHS:
        return
    if any(path.startswith(p) for p in _OPEN_PREFIXES):
        return
    if _matches(api_key, "API_KEY") or _matches(api_key, "ADMIN_API_KEY"):
        return
    if not os.environ.get("API_KEY"):
        raise HTTPException(status_code=500, detail="Server API key not configured")
    raise HTTPException(status_code=401, detail="Invalid API key")


async def require_admin_key(
    api_key: str | None = Depends(_api_key_header),
) -> None:
    if not _matches(api_key, "ADMIN_API_KEY"):
        raise HTTPException(status_code=403, detail="Admin access required")
