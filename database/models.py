from datetime import datetime, timezone

from sqlalchemy import Boolean, CheckConstraint, Column, DateTime, Float, Integer, String, Text
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
    rating = Column(Float, nullable=True)
    user_ratings_total = Column(Integer, nullable=True)
    business_type = Column(String, nullable=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class AppUser(Base):
    __tablename__ = "app_users"
    __table_args__ = (
        CheckConstraint("role IN ('admin', 'member')", name="app_users_role_check"),
    )

    clerk_user_id = Column(String(128), primary_key=True)
    email = Column(String(320), nullable=True, index=True)
    first_name = Column(String(255), nullable=True)
    last_name = Column(String(255), nullable=True)
    image_url = Column(Text, nullable=True)
    role = Column(String(20), nullable=False, default="member", index=True)
    is_active = Column(Boolean, nullable=False, default=True, index=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
    deleted_at = Column(DateTime(timezone=True), nullable=True)

    @property
    def full_name(self) -> str:
        return " ".join(part for part in [self.first_name, self.last_name] if part)
