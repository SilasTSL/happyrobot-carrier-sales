from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.auth.auth import require_admin_key
from app.database import get_db
from app.database.models import CallRecord
from app.schemas.call_records import CallRecordCreate, CallRecordRead
from app.services.metrics import log_call_record

router = APIRouter(prefix="/call-records", tags=["call-records"])


@router.post("/", response_model=CallRecordRead, status_code=status.HTTP_201_CREATED)
def post_call_record(data: CallRecordCreate, db: Session = Depends(get_db)):
    return log_call_record(db, data)


@router.get("/", response_model=list[CallRecordRead], dependencies=[Depends(require_admin_key)])
def get_call_records(db: Session = Depends(get_db)):
    return db.query(CallRecord).order_by(CallRecord.timestamp.desc()).all()
