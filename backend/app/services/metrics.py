import logging

from sqlalchemy.orm import Session

from app.database.models import CallRecord, Load, OutcomeEnum
from app.schemas.call_records import CallRecordCreate

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
