from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.database.models import Load
from app.schemas.loads import LoadRead

router = APIRouter(prefix="/loads", tags=["loads"])


@router.get("/", response_model=list[LoadRead])
def get_loads(db: Session = Depends(get_db)):
    return db.query(Load).all()
