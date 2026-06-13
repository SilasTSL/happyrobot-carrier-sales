from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.database.models import CallRecord
from app.schemas.call_records import CallRecordRead

router = APIRouter(prefix="/call-records", tags=["call-records"])


@router.get("/", response_model=list[CallRecordRead])
def get_call_records(db: Session = Depends(get_db)):
    return db.query(CallRecord).order_by(CallRecord.timestamp.desc()).all()
