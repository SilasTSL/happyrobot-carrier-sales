import json
import logging
from datetime import datetime, timedelta, timezone
from pathlib import Path

from sqlalchemy.orm import Session

from app.database.models import CallRecord, Load, OutcomeEnum, SentimentEnum

logger = logging.getLogger(__name__)

_SEED_FILE = Path(__file__).parent.parent.parent / "seed_loads.json"

_CALL_RECORD_SPECS = [
    # --- booked (10) ---
    {
        "load_index": 0, "mc_number": "MC-287364", "carrier_name": "Swift Transportation",
        "verification_passed": True, "final_rate": 2600.00, "negotiation_rounds": 3,
        "outcome": "booked", "sentiment": "positive", "call_duration_seconds": 287, "hours_ago": 720,
        "transcript": "Agent offered Chicago–Dallas dry van at $2,450. Carrier countered $2,750. Three rounds; closed at $2,600. BOL and pickup window confirmed.",
    },
    {
        "load_index": 2, "mc_number": "MC-394821", "carrier_name": "Werner Enterprises",
        "verification_passed": True, "final_rate": 2600.00, "negotiation_rounds": 2,
        "outcome": "booked", "sentiment": "positive", "call_duration_seconds": 215, "hours_ago": 648,
        "transcript": "Atlanta–New York dry van, high-value electronics. Carrier confirmed no drop trailer policy. Two rounds from board rate; settled at $2,600.",
    },
    {
        "load_index": 4, "mc_number": "MC-512847", "carrier_name": "Heartland Express",
        "verification_passed": True, "final_rate": 2750.00, "negotiation_rounds": 1,
        "outcome": "booked", "sentiment": "neutral", "call_duration_seconds": 145, "hours_ago": 576,
    },
    {
        "load_index": 7, "mc_number": "MC-628394", "carrier_name": "Schneider National",
        "verification_passed": True, "final_rate": 2700.00, "negotiation_rounds": 2,
        "outcome": "booked", "sentiment": "positive", "call_duration_seconds": 198, "hours_ago": 504,
        "transcript": "Boston–Chicago dry van, 980 miles. Opened at $2,550, carrier asked $2,800, closed at $2,700 after two rounds.",
    },
    {
        "load_index": 9, "mc_number": "MC-741285", "carrier_name": "JB Hunt Transport",
        "verification_passed": True, "final_rate": 2050.00, "negotiation_rounds": 3,
        "outcome": "booked", "sentiment": "neutral", "call_duration_seconds": 312, "hours_ago": 432,
        "transcript": "Reefer Portland–Sacramento, USDA food-grade required. Carrier confirmed compliant trailer. Three rounds; closed at $2,050.",
    },
    {
        "load_index": 11, "mc_number": "MC-853921", "carrier_name": "Knight Transportation",
        "verification_passed": True, "final_rate": 1300.00, "negotiation_rounds": 1,
        "outcome": "booked", "sentiment": "positive", "call_duration_seconds": 118, "hours_ago": 360,
    },
    {
        "load_index": 5, "mc_number": "MC-967432", "carrier_name": "USA Truck",
        "verification_passed": True, "final_rate": 1850.00, "negotiation_rounds": 2,
        "outcome": "booked", "sentiment": "positive", "call_duration_seconds": 234, "hours_ago": 312,
    },
    {
        "load_index": 12, "mc_number": "MC-104857", "carrier_name": "Covenant Transport",
        "verification_passed": True, "final_rate": 975.00, "negotiation_rounds": 1,
        "outcome": "booked", "sentiment": "positive", "call_duration_seconds": 97, "hours_ago": 264,
    },
    {
        "load_index": 13, "mc_number": "MC-215964", "carrier_name": "Prime Inc",
        "verification_passed": True, "final_rate": 1550.00, "negotiation_rounds": 2,
        "outcome": "booked", "sentiment": "neutral", "call_duration_seconds": 221, "hours_ago": 216,
    },
    {
        "load_index": 3, "mc_number": "MC-328471", "carrier_name": "Roehl Transport",
        "verification_passed": True, "final_rate": 1900.00, "negotiation_rounds": 3,
        "outcome": "booked", "sentiment": "positive", "call_duration_seconds": 298, "hours_ago": 168,
        "transcript": "Houston–Memphis flatbed, steel coils. Carrier confirmed coil racks. Three rounds from $1,750; closed at $1,900. Insurance cert number provided.",
    },
    # --- not_eligible (7) ---
    {
        "load_index": None, "mc_number": None, "carrier_name": None,
        "verification_passed": False, "final_rate": None, "negotiation_rounds": 0,
        "outcome": "not_eligible", "sentiment": "negative", "call_duration_seconds": 45, "hours_ago": 696,
    },
    {
        "load_index": None, "mc_number": "MC-000192", "carrier_name": "Unknown Carrier LLC",
        "verification_passed": False, "final_rate": None, "negotiation_rounds": 0,
        "outcome": "not_eligible", "sentiment": "negative", "call_duration_seconds": 63, "hours_ago": 624,
    },
    {
        "load_index": None, "mc_number": "MC-111204", "carrier_name": "Fast Freight Co",
        "verification_passed": False, "final_rate": None, "negotiation_rounds": 0,
        "outcome": "not_eligible", "sentiment": "negative", "call_duration_seconds": 78, "hours_ago": 552,
    },
    {
        "load_index": None, "mc_number": "MC-222415", "carrier_name": "QuickHaul Inc",
        "verification_passed": False, "final_rate": None, "negotiation_rounds": 0,
        "outcome": "not_eligible", "sentiment": "neutral", "call_duration_seconds": 55, "hours_ago": 480,
    },
    {
        "load_index": None, "mc_number": None, "carrier_name": None,
        "verification_passed": False, "final_rate": None, "negotiation_rounds": 0,
        "outcome": "not_eligible", "sentiment": "negative", "call_duration_seconds": 38, "hours_ago": 408,
    },
    {
        "load_index": None, "mc_number": "MC-333526", "carrier_name": "Blue Ridge Transport",
        "verification_passed": False, "final_rate": None, "negotiation_rounds": 0,
        "outcome": "not_eligible", "sentiment": "negative", "call_duration_seconds": 82, "hours_ago": 336,
    },
    {
        "load_index": None, "mc_number": "MC-444637", "carrier_name": "Desert Wind Carriers",
        "verification_passed": False, "final_rate": None, "negotiation_rounds": 0,
        "outcome": "not_eligible", "sentiment": "negative", "call_duration_seconds": 71, "hours_ago": 288,
    },
    # --- no_match (4) ---
    {
        "load_index": None, "mc_number": "MC-555748", "carrier_name": "Mountainview Logistics",
        "verification_passed": True, "final_rate": None, "negotiation_rounds": 0,
        "outcome": "no_match", "sentiment": "neutral", "call_duration_seconds": 134, "hours_ago": 528,
    },
    {
        "load_index": None, "mc_number": "MC-666859", "carrier_name": "Coastal Carriers Inc",
        "verification_passed": True, "final_rate": None, "negotiation_rounds": 0,
        "outcome": "no_match", "sentiment": "neutral", "call_duration_seconds": 118, "hours_ago": 456,
    },
    {
        "load_index": None, "mc_number": "MC-777960", "carrier_name": "Prairie Wind Transport",
        "verification_passed": True, "final_rate": None, "negotiation_rounds": 0,
        "outcome": "no_match", "sentiment": "neutral", "call_duration_seconds": 156, "hours_ago": 384,
    },
    {
        "load_index": None, "mc_number": "MC-888071", "carrier_name": "Apex Freight Solutions",
        "verification_passed": True, "final_rate": None, "negotiation_rounds": 0,
        "outcome": "no_match", "sentiment": "neutral", "call_duration_seconds": 142, "hours_ago": 240,
    },
    # --- rate_not_agreed (6) ---
    {
        "load_index": 1, "mc_number": "MC-885921", "carrier_name": "Sunrise Trucking",
        "verification_passed": True, "final_rate": None, "negotiation_rounds": 3,
        "outcome": "rate_not_agreed", "sentiment": "negative", "call_duration_seconds": 285, "hours_ago": 600,
    },
    {
        "load_index": 6, "mc_number": "MC-996438", "carrier_name": "Canyon Haul LLC",
        "verification_passed": True, "final_rate": None, "negotiation_rounds": 3,
        "outcome": "rate_not_agreed", "sentiment": "negative", "call_duration_seconds": 312, "hours_ago": 480,
    },
    {
        "load_index": 8, "mc_number": "MC-107542", "carrier_name": "Southern Star Freight",
        "verification_passed": True, "final_rate": None, "negotiation_rounds": 2,
        "outcome": "rate_not_agreed", "sentiment": "neutral", "call_duration_seconds": 198, "hours_ago": 360,
    },
    {
        "load_index": 10, "mc_number": "MC-218643", "carrier_name": "Great Lakes Carriers",
        "verification_passed": True, "final_rate": None, "negotiation_rounds": 3,
        "outcome": "rate_not_agreed", "sentiment": "negative", "call_duration_seconds": 267, "hours_ago": 192,
    },
    {
        "load_index": 1, "mc_number": "MC-329754", "carrier_name": "Ridgeline Transport",
        "verification_passed": True, "final_rate": None, "negotiation_rounds": 2,
        "outcome": "rate_not_agreed", "sentiment": "negative", "call_duration_seconds": 223, "hours_ago": 120,
    },
    {
        "load_index": 6, "mc_number": "MC-440861", "carrier_name": "Sierra Nevada Freight",
        "verification_passed": True, "final_rate": None, "negotiation_rounds": 3,
        "outcome": "rate_not_agreed", "sentiment": "negative", "call_duration_seconds": 298, "hours_ago": 48,
    },
    # --- hung_up (3) ---
    {
        "load_index": None, "mc_number": None, "carrier_name": None,
        "verification_passed": False, "final_rate": None, "negotiation_rounds": 0,
        "outcome": "hung_up", "sentiment": "negative", "call_duration_seconds": 18, "hours_ago": 672,
    },
    {
        "load_index": None, "mc_number": "MC-551972", "carrier_name": "Eagle Eye Freight",
        "verification_passed": True, "final_rate": None, "negotiation_rounds": 0,
        "outcome": "hung_up", "sentiment": "negative", "call_duration_seconds": 32, "hours_ago": 144,
    },
    {
        "load_index": None, "mc_number": None, "carrier_name": None,
        "verification_passed": False, "final_rate": None, "negotiation_rounds": 0,
        "outcome": "hung_up", "sentiment": "negative", "call_duration_seconds": 15, "hours_ago": 72,
    },
]


def seed_loads(db: Session) -> None:
    existing = db.query(Load).count()
    if existing > 0:
        logger.info("Loads table already populated (%d rows) — skipping seed", existing)
        return

    records = json.loads(_SEED_FILE.read_text())
    logger.info("Seeding %d loads from %s", len(records), _SEED_FILE)

    loads = [
        Load(
            **{
                **r,
                "pickup_datetime": datetime.fromisoformat(r["pickup_datetime"]),
                "delivery_datetime": datetime.fromisoformat(r["delivery_datetime"]),
            }
        )
        for r in records
    ]
    db.add_all(loads)
    db.commit()
    logger.info("Seeding complete — %d loads inserted", len(loads))


def seed_call_records(db: Session) -> None:
    existing = db.query(CallRecord).count()
    if existing > 0:
        logger.info("CallRecord table already populated (%d rows) — skipping seed", existing)
        return

    loads = db.query(Load).order_by(Load.load_id).all()
    now = datetime.now(timezone.utc)

    logger.info("Seeding %d call records", len(_CALL_RECORD_SPECS))

    records = [
        CallRecord(
            timestamp=now - timedelta(hours=spec["hours_ago"]),
            mc_number=spec["mc_number"],
            carrier_name=spec["carrier_name"],
            verification_passed=spec["verification_passed"],
            load_id=loads[spec["load_index"]].load_id if spec["load_index"] is not None else None,
            loadboard_rate=loads[spec["load_index"]].loadboard_rate if spec["load_index"] is not None else None,
            max_rate=loads[spec["load_index"]].max_rate if spec["load_index"] is not None else None,
            final_rate=spec["final_rate"],
            negotiation_rounds=spec["negotiation_rounds"],
            outcome=OutcomeEnum(spec["outcome"]),
            sentiment=SentimentEnum(spec["sentiment"]),
            call_duration_seconds=spec["call_duration_seconds"],
            transcript=spec.get("transcript"),
        )
        for spec in _CALL_RECORD_SPECS
    ]

    db.add_all(records)
    db.commit()
    logger.info("Seeding complete — %d call records inserted", len(records))
