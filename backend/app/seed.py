import json
from datetime import datetime
from pathlib import Path

from sqlalchemy.orm import Session

from app.models import Load

_SEED_FILE = Path(__file__).parent.parent / "seed_loads.json"


def seed_loads(db: Session) -> None:
    if db.query(Load).count() > 0:
        return

    records = json.loads(_SEED_FILE.read_text())
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
