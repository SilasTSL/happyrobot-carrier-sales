from datetime import datetime

from pydantic import BaseModel, ConfigDict


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
