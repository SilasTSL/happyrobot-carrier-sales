"""
GET /api/calls

Paginated, filterable, sortable call-record list.

Filters : start, end, outcome, sentiment
Sort    : timestamp (default desc), final_rate
"""
from datetime import datetime, timedelta, timezone
from typing import Literal

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session, joinedload

from app.auth.jwt import get_current_company
from app.database import get_db
from app.database.models import CallRecord, Company, OutcomeEnum, SentimentEnum
from app.schemas.dashboard import CallRecordRow, CallsResponse

router = APIRouter()


def _strip_tz(dt: datetime | None) -> datetime | None:
    if dt is None:
        return None
    if dt.tzinfo is not None:
        return dt.astimezone(timezone.utc).replace(tzinfo=None)
    return dt


@router.get("/calls", response_model=CallsResponse)
def get_calls(
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=200),
    start: datetime | None = Query(None),
    end: datetime | None = Query(None),
    outcome: OutcomeEnum | None = Query(None),
    sentiment: SentimentEnum | None = Query(None),
    sort: Literal["timestamp_desc", "timestamp_asc", "final_rate_desc", "final_rate_asc"] = Query(
        "timestamp_desc"
    ),
    company: Company = Depends(get_current_company),
    db: Session = Depends(get_db),
):
    now = datetime.now(timezone.utc)
    end_dt = _strip_tz(end) if end else now.replace(tzinfo=None)
    start_dt = _strip_tz(start) if start else (now - timedelta(days=30)).replace(tzinfo=None)

    query = (
        db.query(CallRecord)
        .options(joinedload(CallRecord.load))
        .filter(
            CallRecord.company_id == company.company_id,
            CallRecord.timestamp >= start_dt,
            CallRecord.timestamp < end_dt,
        )
    )

    if outcome is not None:
        query = query.filter(CallRecord.outcome == outcome)
    if sentiment is not None:
        query = query.filter(CallRecord.sentiment == sentiment)

    sort_map = {
        "timestamp_desc": CallRecord.timestamp.desc(),
        "timestamp_asc": CallRecord.timestamp.asc(),
        "final_rate_desc": CallRecord.final_rate.desc(),
        "final_rate_asc": CallRecord.final_rate.asc(),
    }
    query = query.order_by(sort_map[sort])

    total = query.count()
    records = query.offset((page - 1) * limit).limit(limit).all()

    return CallsResponse(
        total=total,
        page=page,
        limit=limit,
        data=[
            CallRecordRow(
                call_id=r.call_id,
                timestamp=r.timestamp.isoformat(),
                carrier_name=r.carrier_name,
                mc_number=r.mc_number,
                origin=r.load.origin if r.load else None,
                destination=r.load.destination if r.load else None,
                equipment_type=r.load.equipment_type if r.load else None,
                outcome=r.outcome,
                sentiment=r.sentiment,
                loadboard_rate=r.loadboard_rate,
                final_rate=r.final_rate,
                max_rate=r.max_rate,
                negotiation_rounds=r.negotiation_rounds,
            )
            for r in records
        ],
    )
