import bcrypt
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.auth.jwt import create_access_token
from app.database import get_db
from app.database.models import Company

router = APIRouter(prefix="/api/auth", tags=["auth"])


class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    company_name: str
    company_id: int


@router.post("/login", response_model=LoginResponse)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    company = db.query(Company).filter(Company.username == data.username).first()
    if not company or not bcrypt.checkpw(data.password.encode(), company.password_hash.encode()):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token(company.company_id, company.name)
    return LoginResponse(
        access_token=token,
        company_name=company.name,
        company_id=company.company_id,
    )
