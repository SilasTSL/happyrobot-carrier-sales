from datetime import datetime

from pydantic import AliasChoices, BaseModel, ConfigDict, Field

from app.database.models import OutcomeEnum, SentimentEnum


class CallRecordCreate(BaseModel):
    company_id: int
    mc_number: str | None = None
    carrier_name: str | None = None
    load_id: int | None = None
    final_rate: float | None = None
    negotiation_rounds: int | None = None
    outcome: OutcomeEnum
    sentiment: SentimentEnum


class CallRecordRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    call_id: str
    company_id: int
    timestamp: datetime
    mc_number: str | None
    carrier_name: str | None
    load_id: int | None
    loadboard_rate: float | None
    max_rate: float | None
    final_rate: float | None
    negotiation_rounds: int
    outcome: OutcomeEnum
    sentiment: SentimentEnum
