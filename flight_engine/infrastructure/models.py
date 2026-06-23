from sqlalchemy import Column, String, DateTime, Numeric, Integer, Index, JSON, Float, Boolean
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

class AccommodationModel(Base):
    __tablename__ = "accommodations"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    type = Column(String, nullable=False, index=True)  # 'hotel', 'pousada', 'hostel', 'resort'
    rating = Column(Float, nullable=False)
    stars = Column(Integer, nullable=False)
    reviews_count = Column(Integer, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    price_per_night = Column(Numeric(10, 2), nullable=False)
    photo_url = Column(String, nullable=False)
    amenities = Column(JSON, nullable=False)  # List of amenities strings
    city = Column(String, nullable=False, index=True)  # city / airport code, e.g., 'SAO'
    distance_center = Column(Float, nullable=False)
    distance_airport = Column(Float, nullable=False)
    distance_beach = Column(Float, nullable=True)
    distance_sightseeing = Column(Float, nullable=True)

    __table_args__ = (
        Index("ix_accommodations_city_type", "city", "type"),
        Index("ix_accommodations_price", "price_per_night"),
    )

class SearchHistoryModel(Base):
    __tablename__ = "search_history"

    id = Column(Integer, primary_key=True, autoincrement=True)
    origin = Column(String, nullable=False)
    destination = Column(String, nullable=False)
    departure_date = Column(DateTime(timezone=True), nullable=False)
    return_date = Column(DateTime(timezone=True), nullable=True)
    adults = Column(Integer, nullable=False)
    searched_at = Column(DateTime(timezone=True), default=func.now(), nullable=False)

class FavoriteModel(Base):
    __tablename__ = "favorites"

    id = Column(Integer, primary_key=True, autoincrement=True)
    item_type = Column(String, nullable=False, index=True)  # 'flight' or 'accommodation'
    item_id = Column(String, nullable=False, index=True)
    details = Column(JSON, nullable=False)  # Full details dict of item
    created_at = Column(DateTime(timezone=True), default=func.now(), nullable=False)

class UserModel(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String, nullable=False, index=True, unique=True)
    name = Column(String, nullable=False)
    google_id = Column(String, nullable=True, index=True)
    facebook_id = Column(String, nullable=True, index=True)
    avatar_url = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), default=func.now(), nullable=False)

class AnonymousSearchTrackingModel(Base):
    __tablename__ = "anonymous_tracking"

    id = Column(Integer, primary_key=True, autoincrement=True)
    ip_address = Column(String, nullable=False, index=True, unique=True)
    search_count = Column(Integer, default=0, nullable=False)
    last_search_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now(), nullable=False)
