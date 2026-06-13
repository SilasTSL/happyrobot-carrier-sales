import json
import logging
from datetime import datetime
from pathlib import Path

from sqlalchemy.orm import Session

from app.models import Load

logger = logging.getLogger(__name__)

_SEED_FILE = Path(__file__).parent.parent / "seed_loads.json"


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
