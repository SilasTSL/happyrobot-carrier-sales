from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.call_records import CallRecordCreate, CallRecordRead
from app.services.metrics import log_call_record

router = APIRouter(prefix="/metrics", tags=["metrics"])


@router.post("/", response_model=CallRecordRead, status_code=status.HTTP_201_CREATED)
def post_call_record(data: CallRecordCreate, db: Session = Depends(get_db)):
    return log_call_record(db, data)
