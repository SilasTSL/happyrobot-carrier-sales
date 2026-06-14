"""
GET /api/metrics/breakdowns?start=&end=

Outcome distribution, sentiment distribution, negotiation-rounds histogram,
top lanes by volume, and MC eligibility rate.
"""
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, Query
from sqlalchemy import case, func
from sqlalchemy.orm import Session

from app.auth.jwt import get_current_company
from app.database import get_db
from app.database.models import CallRecord, Company, Load, OutcomeEnum, SentimentEnum
from app.schemas.dashboard import (
    BreakdownsResponse,
    LaneBreakdown,
    NegotiationBreakdown,
    OutcomeBreakdown,
    SentimentBreakdown,
)

router = APIRouter()


def _strip_tz(dt: datetime | None) -> datetime | None:
    if dt is None:
        return None
    if dt.tzinfo is not None:
        return dt.astimezone(timezone.utc).replace(tzinfo=None)
    return dt


@router.get("/metrics/breakdowns", response_model=BreakdownsResponse)
def get_breakdowns(
    start: datetime | None = Query(None),
    end: datetime | None = Query(None),
    company: Company = Depends(get_current_company),
    db: Session = Depends(get_db),
):
    now = datetime.now(timezone.utc)
    end_dt = _strip_tz(end) if end else now.replace(tzinfo=None)
    start_dt = _strip_tz(start) if start else (now - timedelta(days=30)).replace(tzinfo=None)

    date_filter = [
        CallRecord.company_id == company.company_id,
        CallRecord.timestamp >= start_dt,
        CallRecord.timestamp < end_dt,
    ]

    # -- Outcome distribution --------------------------------------------------
    outcome_rows = (
        db.query(
            CallRecord.outcome,
            func.count(CallRecord.call_id).label("cnt"),
        )
        .filter(*date_filter)
        .group_by(CallRecord.outcome)
        .all()
    )
    total_calls = sum(r.cnt for r in outcome_rows)
    outcomes = [
        OutcomeBreakdown(
            outcome=r.outcome,
            count=r.cnt,
            pct=round(r.cnt / total_calls * 100, 1) if total_calls else 0.0,
        )
        for r in outcome_rows
    ]

    # -- Sentiment distribution with booking rate per sentiment ----------------
    sentiment_rows = (
        db.query(
            CallRecord.sentiment,
            func.count(CallRecord.call_id).label("cnt"),
            func.sum(
                case((CallRecord.outcome == OutcomeEnum.booked, 1), else_=0)
            ).label("booked_cnt"),
        )
        .filter(*date_filter)
        .group_by(CallRecord.sentiment)
        .all()
    )
    sentiments = [
        SentimentBreakdown(
            sentiment=r.sentiment,
            count=r.cnt,
            booking_rate=round(r.booked_cnt / r.cnt * 100, 1) if r.cnt else 0.0,
        )
        for r in sentiment_rows
    ]

    # -- Negotiation-rounds distribution ---------------------------------------
    rounds_rows = (
        db.query(
            CallRecord.negotiation_rounds,
            func.count(CallRecord.call_id).label("cnt"),
            func.sum(
                case((CallRecord.outcome == OutcomeEnum.booked, 1), else_=0)
            ).label("booked_cnt"),
        )
        .filter(*date_filter)
        .group_by(CallRecord.negotiation_rounds)
        .order_by(CallRecord.negotiation_rounds)
        .all()
    )
    negotiation_rounds = [
        NegotiationBreakdown(
            rounds=r.negotiation_rounds,
            count=r.cnt,
            booking_rate=round(r.booked_cnt / r.cnt * 100, 1) if r.cnt else 0.0,
        )
        for r in rounds_rows
    ]

    # -- Top lanes by call volume (join to Load for origin/dest/equip) ---------
    lane_rows = (
        db.query(
            Load.origin,
            Load.destination,
            Load.equipment_type,
            func.count(CallRecord.call_id).label("calls"),
            func.sum(
                case((CallRecord.outcome == OutcomeEnum.booked, 1), else_=0)
            ).label("bookings"),
        )
        .join(Load, CallRecord.load_id == Load.load_id)
        .filter(*date_filter)
        .group_by(Load.origin, Load.destination, Load.equipment_type)
        .order_by(func.count(CallRecord.call_id).desc())
        .limit(10)
        .all()
    )
    top_lanes = [
        LaneBreakdown(
            origin=r.origin,
            destination=r.destination,
            equipment_type=r.equipment_type,
            calls=r.calls,
            bookings=r.bookings,
            booking_rate=round(r.bookings / r.calls * 100, 1) if r.calls else 0.0,
        )
        for r in lane_rows
    ]

    # -- MC eligibility rate ---------------------------------------------------
    not_elig = next(
        (r.cnt for r in outcome_rows if r.outcome == OutcomeEnum.not_eligible), 0
    )
    mc_eligibility_rate = (
        round((total_calls - not_elig) / total_calls * 100, 1) if total_calls else 0.0
    )

    return BreakdownsResponse(
        outcomes=outcomes,
        sentiments=sentiments,
        negotiation_rounds=negotiation_rounds,
        top_lanes=top_lanes,
        mc_eligibility_rate=mc_eligibility_rate,
    )
