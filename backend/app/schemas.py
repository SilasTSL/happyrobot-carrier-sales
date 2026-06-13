from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models import OutcomeEnum, SentimentEnum


class LoadRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    load_id: int
    origin: str
    destination: str
    pickup_datetime: datetime
    delivery_datetime: datetime
    equipment_type: str
    loadboard_rate: float
    max_rate: float
    notes: str | None
    weight: float
    commodity_type: str
    num_of_pieces: int
    miles: float
    dimensions: str | None
    booked: bool


class CallRecordRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    call_id: str
    timestamp: datetime
    mc_number: str | None
    carrier_name: str | None
    verification_passed: bool
    load_id: int | None
    loadboard_rate: float | None
    max_rate: float | None
    final_rate: float | None
    negotiation_rounds: int
    outcome: OutcomeEnum
    sentiment: SentimentEnum
    call_duration_seconds: int | None
    transcript: str | None
