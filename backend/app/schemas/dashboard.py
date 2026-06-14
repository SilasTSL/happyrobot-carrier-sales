from pydantic import BaseModel

from app.database.models import OutcomeEnum, SentimentEnum


# ---------------------------------------------------------------------------
# Summary / KPIs
# ---------------------------------------------------------------------------

class KpiValue(BaseModel):
    value: float | int | None
    delta_pct: float | None  # % change vs prior equivalent period; None if prior is 0 or missing


class SummaryResponse(BaseModel):
    period_start: str
    period_end: str
    # Volume
    total_calls: KpiValue
    loads_booked: KpiValue
    booking_rate: KpiValue          # % of eligible calls that booked
    # Revenue
    total_committed_revenue: KpiValue
    avg_final_rate: KpiValue
    # Efficiency
    avg_negotiation_rounds: KpiValue
    # Margin intelligence
    avg_rate_delta: KpiValue        # final_rate - loadboard_rate (concession per booked load)
    avg_margin_headroom_used: KpiValue  # % of (loadboard→max) band consumed
    calls_at_max_rate: KpiValue     # count where final_rate >= max_rate
    calls_at_max_rate_pct: KpiValue # above / loads_booked * 100


# ---------------------------------------------------------------------------
# Timeseries
# ---------------------------------------------------------------------------

class TimeseriesPoint(BaseModel):
    date: str   # "YYYY-MM-DD"
    calls: int
    bookings: int


class TimeseriesResponse(BaseModel):
    interval: str
    data: list[TimeseriesPoint]


# ---------------------------------------------------------------------------
# Breakdowns
# ---------------------------------------------------------------------------

class OutcomeBreakdown(BaseModel):
    outcome: OutcomeEnum
    count: int
    pct: float


class SentimentBreakdown(BaseModel):
    sentiment: SentimentEnum
    count: int
    booking_rate: float   # % of calls with this sentiment that booked


class NegotiationBreakdown(BaseModel):
    rounds: int
    count: int
    booking_rate: float


class LaneBreakdown(BaseModel):
    origin: str
    destination: str
    equipment_type: str
    calls: int
    bookings: int
    booking_rate: float


class BreakdownsResponse(BaseModel):
    outcomes: list[OutcomeBreakdown]
    sentiments: list[SentimentBreakdown]
    negotiation_rounds: list[NegotiationBreakdown]
    top_lanes: list[LaneBreakdown]
    mc_eligibility_rate: float   # % of calls where outcome != not_eligible


# ---------------------------------------------------------------------------
# Calls (paginated call log)
# ---------------------------------------------------------------------------

class CallRecordRow(BaseModel):
    call_id: str
    timestamp: str          # ISO string — avoids TZ serialisation surprises
    carrier_name: str | None
    mc_number: str | None
    origin: str | None
    destination: str | None
    equipment_type: str | None
    outcome: OutcomeEnum
    sentiment: SentimentEnum
    loadboard_rate: float | None
    final_rate: float | None
    max_rate: float | None
    negotiation_rounds: int


class CallsResponse(BaseModel):
    total: int
    page: int
    limit: int
    data: list[CallRecordRow]
