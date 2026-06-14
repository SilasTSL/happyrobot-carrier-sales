import logging

from sqlalchemy.orm import Session

from app.database.models import CallRecord, Load, OutcomeEnum
from app.schemas.call_records import CallRecordCreate, CallRecordRead
from app.schemas.metrics import MetricsResponse

logger = logging.getLogger(__name__)


def log_call_record(db: Session, data: CallRecordCreate) -> CallRecord:
    loadboard_rate = None
    max_rate = None

    if data.load_id is not None:
        load = db.query(Load).filter(Load.load_id == data.load_id).first()
        if load:
            loadboard_rate = load.loadboard_rate
            max_rate = load.max_rate

    record = CallRecord(
        company_id=data.company_id,
        mc_number=data.mc_number,
        carrier_name=data.carrier_name,
        load_id=data.load_id,
        loadboard_rate=loadboard_rate,
        max_rate=max_rate,
        final_rate=data.final_rate,
        negotiation_rounds=data.negotiation_rounds,
        outcome=data.outcome,
        sentiment=data.sentiment,
    )
    db.add(record)

    if data.outcome == OutcomeEnum.booked and data.load_id is not None:
        db.query(Load).filter(Load.load_id == data.load_id).update({"booked": True})
        logger.info("Load %d marked as booked", data.load_id)

    db.commit()
    db.refresh(record)
    logger.info("Call record %s logged — outcome: %s", record.call_id, record.outcome)
    return record


def get_metrics(db: Session) -> MetricsResponse:
    total_calls = db.query(CallRecord).count()
    not_eligible_count = (
        db.query(CallRecord)
        .filter(CallRecord.outcome == OutcomeEnum.not_eligible)
        .count()
    )
    total_booked = (
        db.query(CallRecord)
        .filter(CallRecord.outcome == OutcomeEnum.booked)
        .count()
    )

    eligible_calls = total_calls - not_eligible_count
    booking_rate = round(total_booked / eligible_calls * 100, 1) if eligible_calls > 0 else 0.0

    booked_records = (
        db.query(CallRecord)
        .filter(
            CallRecord.outcome == OutcomeEnum.booked,
            CallRecord.final_rate.isnot(None),
            CallRecord.loadboard_rate.isnot(None),
            CallRecord.max_rate.isnot(None),
        )
        .all()
    )

    margins = []
    for r in booked_records:
        band = r.max_rate - r.loadboard_rate
        if band > 0:
            retained = (r.max_rate - r.final_rate) / band * 100
            margins.append(retained)

    avg_retained_margin_pct = round(sum(margins) / len(margins), 1) if margins else None

    return MetricsResponse(
        total_calls=total_calls,
        total_booked=total_booked,
        booking_rate=booking_rate,
        avg_retained_margin_pct=avg_retained_margin_pct,
    )
