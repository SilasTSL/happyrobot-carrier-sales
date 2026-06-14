import logging
import random
from datetime import datetime, timedelta, timezone

import bcrypt
from sqlalchemy.orm import Session

from app.database.models import CallRecord, Company, Load, OutcomeEnum, SentimentEnum

logger = logging.getLogger(__name__)


def _hash(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

# ---------------------------------------------------------------------------
# Company definitions
# ---------------------------------------------------------------------------

_COMPANIES = [
    {"name": "Acme Logistics", "username": "acme", "password": "acme1234"},
    {"name": "Blue Ridge Freight", "username": "blueridge", "password": "ridge5678"},
    {"name": "Coastal Carriers", "username": "coastal", "password": "coast9012"},
]

# ---------------------------------------------------------------------------
# Load lane templates
# ---------------------------------------------------------------------------

_ACME_LANES = [
    {"origin": "Chicago, IL", "destination": "Dallas, TX", "equipment_type": "Dry Van",
     "miles": 920, "loadboard_rate": 2450.0, "max_rate": 2750.0, "weight": 42000,
     "commodity_type": "Packaged Goods", "num_of_pieces": 24, "dimensions": "53ft", "notes": None},
    {"origin": "Los Angeles, CA", "destination": "Phoenix, AZ", "equipment_type": "Reefer",
     "miles": 370, "loadboard_rate": 1200.0, "max_rate": 1350.0, "weight": 38000,
     "commodity_type": "Frozen Food", "num_of_pieces": 18, "dimensions": "53ft",
     "notes": "Temperature must be maintained at -10°F"},
    {"origin": "Atlanta, GA", "destination": "New York, NY", "equipment_type": "Dry Van",
     "miles": 870, "loadboard_rate": 2450.0, "max_rate": 2750.0, "weight": 35000,
     "commodity_type": "Electronics", "num_of_pieces": 200, "dimensions": "53ft",
     "notes": "High-value freight — no drop trailer"},
    {"origin": "Houston, TX", "destination": "Memphis, TN", "equipment_type": "Flatbed",
     "miles": 560, "loadboard_rate": 1750.0, "max_rate": 1950.0, "weight": 44000,
     "commodity_type": "Steel Coils", "num_of_pieces": 8, "dimensions": "48x102",
     "notes": "Coil racks required"},
    {"origin": "Seattle, WA", "destination": "Salt Lake City, UT", "equipment_type": "Reefer",
     "miles": 840, "loadboard_rate": 2650.0, "max_rate": 2950.0, "weight": 40000,
     "commodity_type": "Dairy Products", "num_of_pieces": 32, "dimensions": "53ft",
     "notes": "34°F required throughout transit"},
    {"origin": "Miami, FL", "destination": "Charlotte, NC", "equipment_type": "Dry Van",
     "miles": 650, "loadboard_rate": 1750.0, "max_rate": 1950.0, "weight": 28000,
     "commodity_type": "Retail Apparel", "num_of_pieces": 450, "dimensions": "53ft",
     "notes": None},
    {"origin": "Denver, CO", "destination": "Kansas City, MO", "equipment_type": "Flatbed",
     "miles": 600, "loadboard_rate": 1800.0, "max_rate": 2050.0, "weight": 46000,
     "commodity_type": "Construction Equipment", "num_of_pieces": 3, "dimensions": "48x102",
     "notes": "Over-dimensional — permit in hand"},
    {"origin": "Boston, MA", "destination": "Chicago, IL", "equipment_type": "Dry Van",
     "miles": 980, "loadboard_rate": 2550.0, "max_rate": 2850.0, "weight": 36000,
     "commodity_type": "Auto Parts", "num_of_pieces": 85, "dimensions": "53ft", "notes": None},
    {"origin": "Nashville, TN", "destination": "Dallas, TX", "equipment_type": "Dry Van",
     "miles": 670, "loadboard_rate": 1850.0, "max_rate": 2100.0, "weight": 31000,
     "commodity_type": "Clothing", "num_of_pieces": 300, "dimensions": "53ft", "notes": None},
    {"origin": "Portland, OR", "destination": "Sacramento, CA", "equipment_type": "Reefer",
     "miles": 580, "loadboard_rate": 1900.0, "max_rate": 2150.0, "weight": 43000,
     "commodity_type": "Fresh Produce", "num_of_pieces": 60, "dimensions": "53ft",
     "notes": "USDA inspected — food-grade trailer required"},
    {"origin": "Minneapolis, MN", "destination": "Detroit, MI", "equipment_type": "Dry Van",
     "miles": 700, "loadboard_rate": 1850.0, "max_rate": 2100.0, "weight": 33000,
     "commodity_type": "Packaged Goods", "num_of_pieces": 120, "dimensions": "53ft",
     "notes": None},
    {"origin": "Phoenix, AZ", "destination": "El Paso, TX", "equipment_type": "Flatbed",
     "miles": 430, "loadboard_rate": 1250.0, "max_rate": 1400.0, "weight": 47000,
     "commodity_type": "Industrial Materials", "num_of_pieces": 12, "dimensions": "48x102",
     "notes": "Tarping required"},
    {"origin": "St. Louis, MO", "destination": "Louisville, KY", "equipment_type": "Dry Van",
     "miles": 265, "loadboard_rate": 900.0, "max_rate": 1050.0, "weight": 26000,
     "commodity_type": "Consumer Goods", "num_of_pieces": 90, "dimensions": "53ft",
     "notes": None},
    {"origin": "Charlotte, NC", "destination": "Columbus, OH", "equipment_type": "Reefer",
     "miles": 490, "loadboard_rate": 1450.0, "max_rate": 1650.0, "weight": 39000,
     "commodity_type": "Meat Products", "num_of_pieces": 48, "dimensions": "53ft",
     "notes": "28°F required — meat hooks in trailer"},
    {"origin": "Dallas, TX", "destination": "Chicago, IL", "equipment_type": "Dry Van",
     "miles": 920, "loadboard_rate": 2400.0, "max_rate": 2700.0, "weight": 41000,
     "commodity_type": "Consumer Electronics", "num_of_pieces": 180, "dimensions": "53ft",
     "notes": None},
    {"origin": "Memphis, TN", "destination": "Atlanta, GA", "equipment_type": "Dry Van",
     "miles": 420, "loadboard_rate": 1100.0, "max_rate": 1300.0, "weight": 29000,
     "commodity_type": "Retail Goods", "num_of_pieces": 200, "dimensions": "53ft",
     "notes": None},
    {"origin": "Kansas City, MO", "destination": "Denver, CO", "equipment_type": "Flatbed",
     "miles": 600, "loadboard_rate": 1750.0, "max_rate": 2000.0, "weight": 45000,
     "commodity_type": "Steel Products", "num_of_pieces": 6, "dimensions": "48x102",
     "notes": "Tarping required"},
    {"origin": "Sacramento, CA", "destination": "Portland, OR", "equipment_type": "Reefer",
     "miles": 580, "loadboard_rate": 1850.0, "max_rate": 2100.0, "weight": 42000,
     "commodity_type": "Fresh Produce", "num_of_pieces": 55, "dimensions": "53ft",
     "notes": "USDA inspected — food-grade trailer required"},
    {"origin": "Detroit, MI", "destination": "Minneapolis, MN", "equipment_type": "Dry Van",
     "miles": 700, "loadboard_rate": 1900.0, "max_rate": 2150.0, "weight": 34000,
     "commodity_type": "Auto Parts", "num_of_pieces": 95, "dimensions": "53ft",
     "notes": None},
    {"origin": "Columbus, OH", "destination": "Charlotte, NC", "equipment_type": "Dry Van",
     "miles": 490, "loadboard_rate": 1400.0, "max_rate": 1600.0, "weight": 30000,
     "commodity_type": "Packaged Goods", "num_of_pieces": 110, "dimensions": "53ft",
     "notes": None},
    {"origin": "Chicago, IL", "destination": "Nashville, TN", "equipment_type": "Dry Van",
     "miles": 470, "loadboard_rate": 1300.0, "max_rate": 1500.0, "weight": 33000,
     "commodity_type": "Consumer Goods", "num_of_pieces": 140, "dimensions": "53ft",
     "notes": None},
    {"origin": "Dallas, TX", "destination": "Houston, TX", "equipment_type": "Flatbed",
     "miles": 240, "loadboard_rate": 850.0, "max_rate": 1000.0, "weight": 45000,
     "commodity_type": "Pipe & Tubing", "num_of_pieces": 15, "dimensions": "48x102",
     "notes": "Tarping required"},
    {"origin": "Houston, TX", "destination": "San Antonio, TX", "equipment_type": "Dry Van",
     "miles": 200, "loadboard_rate": 700.0, "max_rate": 850.0, "weight": 28000,
     "commodity_type": "Retail Goods", "num_of_pieces": 180, "dimensions": "53ft",
     "notes": None},
    {"origin": "Atlanta, GA", "destination": "Miami, FL", "equipment_type": "Reefer",
     "miles": 660, "loadboard_rate": 2000.0, "max_rate": 2300.0, "weight": 40000,
     "commodity_type": "Fresh Produce", "num_of_pieces": 50, "dimensions": "53ft",
     "notes": "34°F required throughout transit"},
    {"origin": "New York, NY", "destination": "Boston, MA", "equipment_type": "Dry Van",
     "miles": 215, "loadboard_rate": 850.0, "max_rate": 1000.0, "weight": 22000,
     "commodity_type": "Apparel", "num_of_pieces": 300, "dimensions": "53ft",
     "notes": None},
    {"origin": "Philadelphia, PA", "destination": "Atlanta, GA", "equipment_type": "Dry Van",
     "miles": 780, "loadboard_rate": 2100.0, "max_rate": 2400.0, "weight": 37000,
     "commodity_type": "Industrial Supplies", "num_of_pieces": 60, "dimensions": "53ft",
     "notes": None},
    {"origin": "Indianapolis, IN", "destination": "Chicago, IL", "equipment_type": "Dry Van",
     "miles": 180, "loadboard_rate": 650.0, "max_rate": 800.0, "weight": 25000,
     "commodity_type": "Auto Parts", "num_of_pieces": 90, "dimensions": "53ft",
     "notes": None},
    {"origin": "Louisville, KY", "destination": "Memphis, TN", "equipment_type": "Dry Van",
     "miles": 390, "loadboard_rate": 1050.0, "max_rate": 1250.0, "weight": 31000,
     "commodity_type": "Consumer Electronics", "num_of_pieces": 120, "dimensions": "53ft",
     "notes": None},
    {"origin": "Cincinnati, OH", "destination": "Nashville, TN", "equipment_type": "Flatbed",
     "miles": 280, "loadboard_rate": 950.0, "max_rate": 1100.0, "weight": 43000,
     "commodity_type": "Building Materials", "num_of_pieces": 8, "dimensions": "48x102",
     "notes": "Tarping required"},
    {"origin": "Chicago, IL", "destination": "Detroit, MI", "equipment_type": "Dry Van",
     "miles": 280, "loadboard_rate": 900.0, "max_rate": 1050.0, "weight": 29000,
     "commodity_type": "Auto Parts", "num_of_pieces": 110, "dimensions": "53ft",
     "notes": None},
]

_BLUE_RIDGE_LANES = [
    {"origin": "Denver, CO", "destination": "Albuquerque, NM", "equipment_type": "Dry Van",
     "miles": 450, "loadboard_rate": 1400.0, "max_rate": 1600.0, "weight": 38000,
     "commodity_type": "Auto Parts", "num_of_pieces": 75, "dimensions": "53ft", "notes": None},
    {"origin": "Raleigh, NC", "destination": "Washington, DC", "equipment_type": "Reefer",
     "miles": 320, "loadboard_rate": 1100.0, "max_rate": 1300.0, "weight": 35000,
     "commodity_type": "Produce", "num_of_pieces": 40, "dimensions": "53ft",
     "notes": "34°F required"},
    {"origin": "Indianapolis, IN", "destination": "St. Louis, MO", "equipment_type": "Dry Van",
     "miles": 240, "loadboard_rate": 850.0, "max_rate": 1000.0, "weight": 27000,
     "commodity_type": "Consumer Goods", "num_of_pieces": 120, "dimensions": "53ft",
     "notes": None},
    {"origin": "Tampa, FL", "destination": "Nashville, TN", "equipment_type": "Dry Van",
     "miles": 650, "loadboard_rate": 1700.0, "max_rate": 1950.0, "weight": 32000,
     "commodity_type": "Retail Goods", "num_of_pieces": 250, "dimensions": "53ft",
     "notes": None},
    {"origin": "Salt Lake City, UT", "destination": "Las Vegas, NV", "equipment_type": "Flatbed",
     "miles": 420, "loadboard_rate": 1300.0, "max_rate": 1500.0, "weight": 44000,
     "commodity_type": "Construction Materials", "num_of_pieces": 10, "dimensions": "48x102",
     "notes": "Tarping required"},
    {"origin": "Cincinnati, OH", "destination": "Pittsburgh, PA", "equipment_type": "Dry Van",
     "miles": 300, "loadboard_rate": 950.0, "max_rate": 1100.0, "weight": 29000,
     "commodity_type": "Packaged Goods", "num_of_pieces": 85, "dimensions": "53ft",
     "notes": None},
    {"origin": "Oklahoma City, OK", "destination": "Houston, TX", "equipment_type": "Flatbed",
     "miles": 440, "loadboard_rate": 1350.0, "max_rate": 1550.0, "weight": 46000,
     "commodity_type": "Industrial Equipment", "num_of_pieces": 4, "dimensions": "48x102",
     "notes": "Overweight — permit required"},
    {"origin": "Cleveland, OH", "destination": "Buffalo, NY", "equipment_type": "Dry Van",
     "miles": 185, "loadboard_rate": 750.0, "max_rate": 900.0, "weight": 24000,
     "commodity_type": "Consumer Goods", "num_of_pieces": 60, "dimensions": "53ft",
     "notes": None},
]

_COASTAL_LANES = [
    {"origin": "San Diego, CA", "destination": "Tucson, AZ", "equipment_type": "Dry Van",
     "miles": 360, "loadboard_rate": 1150.0, "max_rate": 1350.0, "weight": 30000,
     "commodity_type": "Consumer Goods", "num_of_pieces": 95, "dimensions": "53ft",
     "notes": None},
    {"origin": "Jacksonville, FL", "destination": "Baltimore, MD", "equipment_type": "Reefer",
     "miles": 890, "loadboard_rate": 2200.0, "max_rate": 2500.0, "weight": 38000,
     "commodity_type": "Seafood", "num_of_pieces": 30, "dimensions": "53ft",
     "notes": "32°F required"},
    {"origin": "New Orleans, LA", "destination": "Birmingham, AL", "equipment_type": "Dry Van",
     "miles": 350, "loadboard_rate": 1050.0, "max_rate": 1250.0, "weight": 28000,
     "commodity_type": "Retail Goods", "num_of_pieces": 150, "dimensions": "53ft",
     "notes": None},
    {"origin": "Savannah, GA", "destination": "Charlotte, NC", "equipment_type": "Flatbed",
     "miles": 380, "loadboard_rate": 1200.0, "max_rate": 1400.0, "weight": 43000,
     "commodity_type": "Lumber", "num_of_pieces": 20, "dimensions": "48x102",
     "notes": "Tarping required"},
    {"origin": "Norfolk, VA", "destination": "Philadelphia, PA", "equipment_type": "Dry Van",
     "miles": 360, "loadboard_rate": 1100.0, "max_rate": 1300.0, "weight": 32000,
     "commodity_type": "Auto Parts", "num_of_pieces": 70, "dimensions": "53ft",
     "notes": None},
    {"origin": "Charleston, SC", "destination": "Atlanta, GA", "equipment_type": "Reefer",
     "miles": 350, "loadboard_rate": 1150.0, "max_rate": 1350.0, "weight": 36000,
     "commodity_type": "Fresh Seafood", "num_of_pieces": 25, "dimensions": "53ft",
     "notes": "30°F required — fresh catch"},
]

# ---------------------------------------------------------------------------
# Carrier pools
# ---------------------------------------------------------------------------

_ELIGIBLE_CARRIERS = [
    ("MC-287364", "Swift Transportation"),
    ("MC-394821", "Werner Enterprises"),
    ("MC-512847", "Heartland Express"),
    ("MC-628394", "Schneider National"),
    ("MC-741285", "JB Hunt Transport"),
    ("MC-853921", "Knight Transportation"),
    ("MC-967432", "USA Truck"),
    ("MC-104857", "Covenant Transport"),
    ("MC-215964", "Prime Inc"),
    ("MC-328471", "Roehl Transport"),
    ("MC-441582", "Marten Transport"),
    ("MC-554693", "Old Dominion"),
    ("MC-667804", "Saia Freight"),
    ("MC-780915", "XPO Logistics"),
    ("MC-894026", "Coyote Logistics"),
    ("MC-907137", "Landstar System"),
    ("MC-120248", "Echo Global Logistics"),
    ("MC-233359", "Total Quality Logistics"),
    ("MC-346470", "C.H. Robinson"),
    ("MC-459581", "RXO Transport Solutions"),
    ("MC-572692", "Convoy Inc"),
    ("MC-685803", "Transplace"),
    ("MC-798914", "NFI Industries"),
    ("MC-812025", "Hub Group"),
    ("MC-925136", "Universal Transport"),
]

_INELIGIBLE_CARRIERS = [
    ("MC-000192", "Unknown Carrier LLC"),
    ("MC-111204", "Fast Freight Co"),
    ("MC-222416", "QuickHaul Inc"),
    ("MC-333528", "Badger Freight Inc"),
    ("MC-444640", "Desert Wind Transport"),
    ("MC-555752", "Sunset Haul LLC"),
    ("MC-666864", "Frontier Trucking LLC"),
    ("MC-777976", "Liberty Logistics"),
    ("MC-889088", "Keystone Carriers"),
    ("MC-990200", "Eagle Eye Freight"),
]


# ---------------------------------------------------------------------------
# Seed helpers
# ---------------------------------------------------------------------------

def _make_loads(company_id: int, lanes: list[dict], base_dt: datetime) -> list[Load]:
    loads = []
    for i, lane in enumerate(lanes):
        pickup = base_dt + timedelta(days=7 + i % 14)
        delivery = pickup + timedelta(days=2)
        loads.append(
            Load(
                company_id=company_id,
                origin=lane["origin"],
                destination=lane["destination"],
                pickup_datetime=pickup.replace(tzinfo=None),
                delivery_datetime=delivery.replace(tzinfo=None),
                equipment_type=lane["equipment_type"],
                loadboard_rate=lane["loadboard_rate"],
                max_rate=round(lane["loadboard_rate"] * 0.88, 0),
                notes=lane.get("notes"),
                weight=lane["weight"],
                commodity_type=lane["commodity_type"],
                num_of_pieces=lane["num_of_pieces"],
                miles=lane["miles"],
                dimensions=lane.get("dimensions"),
                booked=False,
            )
        )
    return loads


def _generate_calls(
    rng: random.Random,
    company_id: int,
    loads: list[Load],
    num_calls: int,
    days_back: int = 60,
    days_forward: int = 7,
) -> list[CallRecord]:
    """
    Generate num_calls synthetic call records spread over the last days_back days
    and up to days_forward days into the future. Future-dated records are stored
    but excluded by dashboard queries (which cap end_dt at now), so the dashboard
    always has recent data even if viewed days after the initial seed.

    Outcome distribution: booked 35%, not_eligible 20%, no_match 10%,
    rate_not_agreed 25%, hung_up 10%.

    final_rate for booked calls follows a Beta(1.5, 4) distribution over
    [loadboard_rate, max_rate], biasing toward the lower end (agent resists
    conceding margin).
    """
    now = datetime.now(timezone.utc)
    outcomes = rng.choices(
        population=[
            OutcomeEnum.booked,
            OutcomeEnum.not_eligible,
            OutcomeEnum.no_match,
            OutcomeEnum.rate_not_agreed,
            OutcomeEnum.hung_up,
        ],
        weights=[35, 20, 10, 25, 10],
        k=num_calls,
    )

    records = []
    for outcome in outcomes:
        days_ago = rng.uniform(-days_forward, days_back)
        timestamp = now - timedelta(days=days_ago)

        mc_number = None
        carrier_name = None
        load_id = None
        loadboard_rate = None
        max_rate = None
        final_rate = None
        negotiation_rounds = 0
        sentiment = SentimentEnum.neutral

        if outcome == OutcomeEnum.booked:
            load = rng.choice(loads)
            mc_number, carrier_name = rng.choice(_ELIGIBLE_CARRIERS)
            load_id = load.load_id
            loadboard_rate = load.loadboard_rate
            max_rate = load.max_rate
            band = loadboard_rate - max_rate
            position = rng.betavariate(1.5, 4.0)
            final_rate = round(max_rate + position * band, 0)
            final_rate = min(final_rate, loadboard_rate)
            negotiation_rounds = rng.choices([1, 2, 3], weights=[30, 50, 20])[0]
            sentiment = rng.choices(
                [SentimentEnum.positive, SentimentEnum.neutral, SentimentEnum.negative],
                weights=[60, 35, 5],
            )[0]

        elif outcome == OutcomeEnum.not_eligible:
            if rng.random() < 0.7:
                mc_number, carrier_name = rng.choice(_INELIGIBLE_CARRIERS)
            sentiment = rng.choices(
                [SentimentEnum.positive, SentimentEnum.neutral, SentimentEnum.negative],
                weights=[5, 15, 80],
            )[0]

        elif outcome == OutcomeEnum.no_match:
            mc_number, carrier_name = rng.choice(_ELIGIBLE_CARRIERS)
            sentiment = rng.choices(
                [SentimentEnum.positive, SentimentEnum.neutral, SentimentEnum.negative],
                weights=[10, 75, 15],
            )[0]

        elif outcome == OutcomeEnum.rate_not_agreed:
            load = rng.choice(loads)
            mc_number, carrier_name = rng.choice(_ELIGIBLE_CARRIERS)
            load_id = load.load_id
            loadboard_rate = load.loadboard_rate
            max_rate = load.max_rate
            negotiation_rounds = rng.choices([2, 3], weights=[40, 60])[0]
            sentiment = rng.choices(
                [SentimentEnum.positive, SentimentEnum.neutral, SentimentEnum.negative],
                weights=[5, 30, 65],
            )[0]

        else:  # hung_up
            if rng.random() < 0.4:
                mc_number, carrier_name = rng.choice(_ELIGIBLE_CARRIERS)
            sentiment = SentimentEnum.negative

        records.append(
            CallRecord(
                timestamp=timestamp.replace(tzinfo=None),
                company_id=company_id,
                mc_number=mc_number,
                carrier_name=carrier_name,
                load_id=load_id,
                loadboard_rate=loadboard_rate,
                max_rate=max_rate,
                final_rate=final_rate,
                negotiation_rounds=negotiation_rounds,
                outcome=outcome,
                sentiment=sentiment,
            )
        )

    return records


# ---------------------------------------------------------------------------
# Public seed entry point
# ---------------------------------------------------------------------------

def seed_all(db: Session) -> None:
    if db.query(Company).count() > 0:
        logger.info("Database already seeded — skipping")
        return

    logger.info("Seeding companies...")
    companies = [
        Company(
            name=c["name"],
            username=c["username"],
            password_hash=_hash(c["password"]),
        )
        for c in _COMPANIES
    ]
    db.add_all(companies)
    db.flush()  # assign company_ids before creating loads

    acme, blue_ridge, coastal = companies

    logger.info("Seeding loads...")
    base_dt = datetime.now(timezone.utc)
    acme_loads = _make_loads(acme.company_id, _ACME_LANES, base_dt)
    br_loads = _make_loads(blue_ridge.company_id, _BLUE_RIDGE_LANES, base_dt)
    coastal_loads = _make_loads(coastal.company_id, _COASTAL_LANES, base_dt)

    db.add_all(acme_loads + br_loads + coastal_loads)
    db.flush()  # assign load_ids before creating call records

    logger.info("Seeding call records (fixed seed rng=42)...")
    rng = random.Random(42)

    acme_calls = _generate_calls(rng, acme.company_id, acme_loads, num_calls=200)
    br_calls = _generate_calls(rng, blue_ridge.company_id, br_loads, num_calls=30)
    coastal_calls = _generate_calls(rng, coastal.company_id, coastal_loads, num_calls=25)

    db.add_all(acme_calls + br_calls + coastal_calls)
    db.flush()

    # Mark loads as booked where a booked call references them
    booked_ids = {
        r.load_id
        for r in (acme_calls + br_calls + coastal_calls)
        if r.outcome == OutcomeEnum.booked and r.load_id is not None
    }
    if booked_ids:
        db.query(Load).filter(Load.load_id.in_(booked_ids)).update(
            {"booked": True}, synchronize_session=False
        )

    db.commit()
    total = len(acme_calls) + len(br_calls) + len(coastal_calls)
    logger.info(
        "Seed complete — %d companies, %d loads, %d call records",
        len(companies),
        len(acme_loads) + len(br_loads) + len(coastal_loads),
        total,
    )
