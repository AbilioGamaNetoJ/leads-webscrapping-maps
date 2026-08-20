from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


class Business(Base):
    __tablename__ = "businesses"

    id = Column(Integer, primary_key=True, index=True)
    place_id = Column(String, unique=True, nullable=False, index=True)
    name = Column(String, nullable=False)
    address = Column(Text)
    phone = Column(String)
    maps_url = Column(Text)
    has_website = Column(Boolean, nullable=False, default=False)
    business_type = Column(String, nullable=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
