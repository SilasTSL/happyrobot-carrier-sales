"""
GET /api/metrics/timeseries?interval=day&start=&end=

Daily (or weekly) call and booking counts for the area/line chart.
"""
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, Query
from sqlalchemy import case, func
from sqlalchemy.orm import Session

from app.auth.jwt import get_current_company
from app.database import get_db
from app.database.models import CallRecord, Company, OutcomeEnum
from app.schemas.dashboard import TimeseriesPoint, TimeseriesResponse

router = APIRouter()


def _strip_tz(dt: datetime | None) -> datetime | None:
    if dt is None:
        return None
    if dt.tzinfo is not None:
        return dt.astimezone(timezone.utc).replace(tzinfo=None)
    return dt


@router.get("/metrics/timeseries", response_model=TimeseriesResponse)
def get_timeseries(
    interval: str = Query("day", pattern="^(day|week)$"),
    start: datetime | None = Query(None),
    end: datetime | None = Query(None),
    company: Company = Depends(get_current_company),
    db: Session = Depends(get_db),
):
    now = datetime.now(timezone.utc)
    end_dt = _strip_tz(end) if end else now.replace(tzinfo=None)
    start_dt = _strip_tz(start) if start else (now - timedelta(days=30)).replace(tzinfo=None)

    fmt = "%Y-%m-%d" if interval == "day" else "%Y-W%W"
    date_bucket = func.strftime(fmt, CallRecord.timestamp)

    rows = (
        db.query(
            date_bucket.label("date"),
            func.count(CallRecord.call_id).label("calls"),
            func.sum(
                case((CallRecord.outcome == OutcomeEnum.booked, 1), else_=0)
            ).label("bookings"),
        )
        .filter(
            CallRecord.company_id == company.company_id,
            CallRecord.timestamp >= start_dt,
            CallRecord.timestamp < end_dt,
        )
        .group_by(date_bucket)
        .order_by(date_bucket)
        .all()
    )

    return TimeseriesResponse(
        interval=interval,
        data=[TimeseriesPoint(date=r.date, calls=r.calls, bookings=r.bookings) for r in rows],
    )
