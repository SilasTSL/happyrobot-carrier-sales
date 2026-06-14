import enum
import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Enum, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.engine import Base


class OutcomeEnum(str, enum.Enum):
    booked = "booked"
    not_eligible = "not_eligible"
    no_match = "no_match"
    rate_not_agreed = "rate_not_agreed"
    hung_up = "hung_up"


class SentimentEnum(str, enum.Enum):
    positive = "positive"
    neutral = "neutral"
    negative = "negative"


class Company(Base):
    __tablename__ = "companies"

    company_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    username: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String, nullable=False)

    loads: Mapped[list["Load"]] = relationship("Load", back_populates="company")
    call_records: Mapped[list["CallRecord"]] = relationship("CallRecord", back_populates="company")


class Load(Base):
    __tablename__ = "loads"

    load_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    company_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("companies.company_id"), nullable=False
    )
    origin: Mapped[str] = mapped_column(String, nullable=False)
    destination: Mapped[str] = mapped_column(String, nullable=False)
    pickup_datetime: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    delivery_datetime: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    equipment_type: Mapped[str] = mapped_column(String, nullable=False)
    loadboard_rate: Mapped[float] = mapped_column(Float, nullable=False)
    max_rate: Mapped[float] = mapped_column(Float, nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    weight: Mapped[float] = mapped_column(Float, nullable=False)
    commodity_type: Mapped[str] = mapped_column(String, nullable=False)
    num_of_pieces: Mapped[int] = mapped_column(Integer, nullable=False)
    miles: Mapped[float] = mapped_column(Float, nullable=False)
    dimensions: Mapped[str | None] = mapped_column(String, nullable=True)
    booked: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    company: Mapped["Company"] = relationship("Company", back_populates="loads")
    call_records: Mapped[list["CallRecord"]] = relationship("CallRecord", back_populates="load")


class CallRecord(Base):
    __tablename__ = "call_records"

    call_id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    timestamp: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )
    company_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("companies.company_id"), nullable=False
    )

    mc_number: Mapped[str | None] = mapped_column(String, nullable=True)
    carrier_name: Mapped[str | None] = mapped_column(String, nullable=True)

    load_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("loads.load_id"), nullable=True
    )
    load: Mapped["Load | None"] = relationship("Load", back_populates="call_records")

    # Intentionally denormalized: loads get re-seeded and rates change,
    # so joining back to Load would silently corrupt historical margin calculations.
    loadboard_rate: Mapped[float | None] = mapped_column(Float, nullable=True)
    max_rate: Mapped[float | None] = mapped_column(Float, nullable=True)
    final_rate: Mapped[float | None] = mapped_column(Float, nullable=True)

    negotiation_rounds: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    outcome: Mapped[OutcomeEnum] = mapped_column(Enum(OutcomeEnum), nullable=False)
    sentiment: Mapped[SentimentEnum] = mapped_column(Enum(SentimentEnum), nullable=False)

    company: Mapped["Company"] = relationship("Company", back_populates="call_records")
