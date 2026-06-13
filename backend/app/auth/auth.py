import os
import secrets

from fastapi import Depends, Header, HTTPException


def verify_api_key(x_api_key: str = Header(...)):
    server_key = os.environ.get("API_KEY")
    if not server_key:
        raise HTTPException(status_code=500, detail="Server API key not configured")
    if not secrets.compare_digest(x_api_key, server_key):
        raise HTTPException(status_code=401, detail="Invalid API key")
    return x_api_key


APIKeyDep = Depends(verify_api_key)
