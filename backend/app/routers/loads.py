from fastapi import APIRouter, Depends, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.auth.auth import require_admin_key
from app.database import get_db
from app.database.models import Load
from app.schemas.loads import LoadRead

router = APIRouter(prefix="/loads", tags=["loads"])


@router.get("/", response_model=list[LoadRead], dependencies=[Depends(require_admin_key)])
def get_loads(db: Session = Depends(get_db)):
    return db.query(Load).all()


@router.get("/search", response_model=list[LoadRead])
def search_loads(
    company_id: int = Query(...),
    origin: str = Query(...),
    equipment_type: str = Query(...),
    db: Session = Depends(get_db),
):
    origin_q = origin.strip().lower()
    equipment_q = equipment_type.strip().lower()

    return (
        db.query(Load)
        .filter(
            Load.company_id == company_id,
            Load.booked == False,
            func.lower(Load.origin).like(f"%{origin_q}%"),
            func.lower(Load.equipment_type).like(f"%{equipment_q}%"),
        )
        .order_by(Load.loadboard_rate.asc())
        .all()
    )
