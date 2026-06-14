from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.auth.auth import require_admin_key
from app.database import get_db
from app.database.models import Company
from app.schemas.companies import CompanyRead

router = APIRouter(prefix="/companies", tags=["companies"])


@router.get("/", response_model=list[CompanyRead], dependencies=[Depends(require_admin_key)])
def get_companies(db: Session = Depends(get_db)):
    return db.query(Company).order_by(Company.company_id).all()
