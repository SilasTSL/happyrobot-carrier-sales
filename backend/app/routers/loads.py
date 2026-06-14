from fastapi import APIRouter, Depends, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.auth.auth import require_admin_key
from app.database import get_db
from app.database.models import Load
from app.schemas.loads import LoadRead

router = APIRouter(prefix="/loads", tags=["loads"])

# Maps agent-supplied equipment terms to the canonical keyword stored in the DB.
_EQUIPMENT_ALIASES: dict[str, str] = {
    "reefer": "reefer",
    "refrigerated": "reefer",
    "refrigerator": "reefer",
    "dry van": "dry van",
    "dry": "dry van",
    "van": "dry van",
    "flatbed": "flatbed",
    "flat bed": "flatbed",
    "flat": "flatbed",
    "step deck": "step deck",
    "stepdeck": "step deck",
}


def _city(origin: str) -> str:
    """Extract city name from 'City, State' or 'City, Full State Name' inputs."""
    return origin.split(",")[0].strip().lower()


def _equipment(raw: str) -> str:
    key = raw.strip().lower()
    return _EQUIPMENT_ALIASES.get(key, key)


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
    city_q = _city(origin)
    equipment_q = _equipment(equipment_type)

    return (
        db.query(Load)
        .filter(
            Load.company_id == company_id,
            Load.booked == False,
            func.lower(Load.origin).like(f"%{city_q}%"),
            func.lower(Load.equipment_type).like(f"%{equipment_q}%"),
        )
        .order_by(Load.loadboard_rate.asc())
        .all()
    )
