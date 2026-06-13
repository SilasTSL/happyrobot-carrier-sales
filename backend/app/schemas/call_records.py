from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.database.models import OutcomeEnum, SentimentEnum


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
