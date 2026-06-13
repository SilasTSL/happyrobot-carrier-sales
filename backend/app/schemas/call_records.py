from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.database.models import OutcomeEnum, SentimentEnum


class CallRecordCreate(BaseModel):
    mc_number: str | None = None
    carrier_name: str | None = None
    verification_passed: bool
    load_id: int | None = None
    final_rate: float | None = None
    negotiation_rounds: int = 0
    outcome: OutcomeEnum
    sentiment: SentimentEnum


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
