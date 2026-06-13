from pydantic import BaseModel


class MetricsResponse(BaseModel):
    total_calls: int
    total_booked: int
    booking_rate: float
    avg_retained_margin_pct: float | None
