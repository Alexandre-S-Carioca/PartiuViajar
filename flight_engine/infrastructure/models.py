from sqlalchemy import Column, String, DateTime, Numeric, Integer, Index
from sqlalchemy.sql import func
from infrastructure.db import Base

class FlightModel(Base):
    __tablename__ = "flights"

    id = Column(String, primary_key=True, index=True)
    airline = Column(String, nullable=False)
    origin = Column(String, nullable=False)
    destination = Column(String, nullable=False)
    departure_date = Column(DateTime(timezone=True), nullable=False)
    arrival_date = Column(DateTime(timezone=True), nullable=False)
    price = Column(Numeric(10, 2), nullable=False)
    currency = Column(String, nullable=False)
    base_price_brl = Column(Numeric(10, 2), nullable=False)
    duration = Column(Integer, nullable=False)
    stops = Column(Integer, nullable=False)
    cabin_class = Column(String, nullable=False)
    booking_url = Column(String, nullable=False)
    collected_at = Column(DateTime(timezone=True), default=func.now(), nullable=False)

    __table_args__ = (
        Index("ix_flights_origin_destination", "origin", "destination"),
        Index("ix_flights_price", "price"),
        Index("ix_flights_collected_at", "collected_at"),
    )

class FlightPriceHistoryModel(Base):
    __tablename__ = "flight_price_history"

    id = Column(Integer, primary_key=True, autoincrement=True)
    flight_id = Column(String, index=True, nullable=False)
    price = Column(Numeric(10, 2), nullable=False)
    currency = Column(String, nullable=False)
    recorded_at = Column(DateTime(timezone=True), default=func.now(), nullable=False)

class PriceAlertModel(Base):
    __tablename__ = "price_alerts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String, nullable=False, index=True)
    telegram_chat_id = Column(String, nullable=True)
    origin = Column(String, nullable=False)
    destination = Column(String, nullable=False)
    departure_date = Column(DateTime(timezone=True), nullable=False)
    target_price = Column(Numeric(10, 2), nullable=False)
    created_at = Column(DateTime(timezone=True), default=func.now(), nullable=False)

