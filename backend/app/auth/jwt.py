import os
from datetime import datetime, timedelta, timezone

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.database import get_db
from app.database.models import Company

_SECRET = os.environ.get("JWT_SECRET", "dev-only-secret-change-in-production")
_ALGORITHM = "HS256"
_EXPIRY_HOURS = 8

_bearer = HTTPBearer(auto_error=False)


def create_access_token(company_id: int, name: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(hours=_EXPIRY_HOURS)
    return jwt.encode(
        {"sub": str(company_id), "name": name, "exp": expire},
        _SECRET,
        algorithm=_ALGORITHM,
    )


async def get_current_company(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer),
    db: Session = Depends(get_db),
) -> Company:
    if not credentials:
        raise HTTPException(
            status_code=401,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    try:
        payload = jwt.decode(credentials.credentials, _SECRET, algorithms=[_ALGORITHM])
        company_id = int(payload["sub"])
    except (JWTError, KeyError, ValueError):
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    company = db.query(Company).filter(Company.company_id == company_id).first()
    if not company:
        raise HTTPException(status_code=401, detail="Company not found")
    return company
