"""
GET /api/metrics/summary

KPI headline numbers plus period-over-period deltas.

Formulas
--------
booking_rate        = booked / (total - not_eligible) * 100
avg_rate_delta      = mean(final_rate - loadboard_rate)  for booked calls
avg_margin_headroom = mean((final_rate - loadboard_rate) / (max_rate - loadboard_rate) * 100)
calls_at_max_rate   = count(booked calls where final_rate >= max_rate)
"""
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.auth.jwt import get_current_company
from app.database import get_db
from app.database.models import CallRecord, Company, OutcomeEnum
from app.schemas.dashboard import KpiValue, SummaryResponse

router = APIRouter()


def _strip_tz(dt: datetime | None) -> datetime | None:
    """Convert to naive UTC so SQLite string comparisons work."""
    if dt is None:
        return None
    if dt.tzinfo is not None:
        return dt.astimezone(timezone.utc).replace(tzinfo=None)
    return dt


def _compute_kpis(db: Session, company_id: int, start: datetime, end: datetime) -> dict:
    base = db.query(CallRecord).filter(
        CallRecord.company_id == company_id,
        CallRecord.timestamp >= start,
        CallRecord.timestamp < end,
    )

    total_calls = base.count()
    not_eligible_count = base.filter(
        CallRecord.outcome == OutcomeEnum.not_eligible
    ).count()
    booked_records = (
        base.filter(CallRecord.outcome == OutcomeEnum.booked).all()
    )
    loads_booked = len(booked_records)

    eligible = total_calls - not_eligible_count
    booking_rate = round(loads_booked / eligible * 100, 1) if eligible > 0 else 0.0

    rates = [r.final_rate for r in booked_records if r.final_rate is not None]
    avg_final_rate = round(sum(rates) / len(rates), 2) if rates else None
    total_committed = round(sum(rates), 2) if rates else 0.0

    rounds_list = [r.negotiation_rounds for r in booked_records]
    avg_rounds = round(sum(rounds_list) / len(rounds_list), 2) if rounds_list else None

    deltas = [
        r.final_rate - r.loadboard_rate
        for r in booked_records
        if r.final_rate is not None and r.loadboard_rate is not None
    ]
    avg_rate_delta = round(sum(deltas) / len(deltas), 2) if deltas else None

    headrooms = []
    calls_at_max = 0
    for r in booked_records:
        if r.final_rate is not None and r.loadboard_rate is not None and r.max_rate is not None:
            band = r.max_rate - r.loadboard_rate
            if band > 0:
                headrooms.append((r.final_rate - r.loadboard_rate) / band * 100)
            if r.final_rate >= r.max_rate:
                calls_at_max += 1

    avg_headroom = round(sum(headrooms) / len(headrooms), 1) if headrooms else None
    calls_at_max_pct = round(calls_at_max / loads_booked * 100, 1) if loads_booked > 0 else 0.0

    return {
        "total_calls": total_calls,
        "booking_rate": booking_rate,
        "loads_booked": loads_booked,
        "avg_final_rate": avg_final_rate,
        "total_committed_revenue": total_committed,
        "avg_negotiation_rounds": avg_rounds,
        "avg_rate_delta": avg_rate_delta,
        "avg_margin_headroom_used": avg_headroom,
        "calls_at_max_rate": calls_at_max,
        "calls_at_max_rate_pct": calls_at_max_pct,
    }


def _delta(current, prior) -> float | None:
    if prior is None or prior == 0:
        return None
    return round((current - prior) / abs(prior) * 100, 1)


def _kpi(current, prior) -> KpiValue:
    return KpiValue(value=current, delta_pct=_delta(current, prior))


@router.get("/metrics/summary", response_model=SummaryResponse)
def get_summary(
    start: datetime | None = Query(None),
    end: datetime | None = Query(None),
    company: Company = Depends(get_current_company),
    db: Session = Depends(get_db),
):
    now = datetime.now(timezone.utc)
    end_dt = _strip_tz(end) if end else now.replace(tzinfo=None)
    start_dt = _strip_tz(start) if start else (now - timedelta(days=30)).replace(tzinfo=None)

    period_len = end_dt - start_dt
    prior_end = start_dt
    prior_start = start_dt - period_len

    current = _compute_kpis(db, company.company_id, start_dt, end_dt)
    prior = _compute_kpis(db, company.company_id, prior_start, prior_end)

    return SummaryResponse(
        period_start=start_dt.isoformat(),
        period_end=end_dt.isoformat(),
        total_calls=_kpi(current["total_calls"], prior["total_calls"]),
        loads_booked=_kpi(current["loads_booked"], prior["loads_booked"]),
        booking_rate=_kpi(current["booking_rate"], prior["booking_rate"]),
        total_committed_revenue=_kpi(current["total_committed_revenue"], prior["total_committed_revenue"]),
        avg_final_rate=_kpi(current["avg_final_rate"], prior["avg_final_rate"]),
        avg_negotiation_rounds=_kpi(current["avg_negotiation_rounds"], prior["avg_negotiation_rounds"]),
        avg_rate_delta=_kpi(current["avg_rate_delta"], prior["avg_rate_delta"]),
        avg_margin_headroom_used=_kpi(current["avg_margin_headroom_used"], prior["avg_margin_headroom_used"]),
        calls_at_max_rate=_kpi(current["calls_at_max_rate"], prior["calls_at_max_rate"]),
        calls_at_max_rate_pct=_kpi(current["calls_at_max_rate_pct"], prior["calls_at_max_rate_pct"]),
    )
