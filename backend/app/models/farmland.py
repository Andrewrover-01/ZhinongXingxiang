import uuid
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import DATE, Boolean, DateTime, ForeignKey, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Farmland(Base):
    __tablename__ = "farmlands"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    owner_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    area: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    location: Mapped[str | None] = mapped_column(String(200))
    latitude: Mapped[Decimal | None] = mapped_column(Numeric(10, 7))
    longitude: Mapped[Decimal | None] = mapped_column(Numeric(10, 7))
    soil_type: Mapped[str | None] = mapped_column(String(50))
    crop_type: Mapped[str | None] = mapped_column(String(100))
    crop_stage: Mapped[str | None] = mapped_column(String(50))
    sowing_date: Mapped[date | None] = mapped_column(DATE)
    notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )

    owner: Mapped["User"] = relationship(back_populates="farmlands")  # noqa: F821
    recognition_records: Mapped[list["RecognitionRecord"]] = relationship(back_populates="farmland")  # noqa: F821


class FarmlandCropHistory(Base):
    __tablename__ = "farmland_crop_history"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    farmland_id: Mapped[str] = mapped_column(String(36), ForeignKey("farmlands.id", ondelete="CASCADE"), nullable=False, index=True)
    crop_type: Mapped[str] = mapped_column(String(100), nullable=False)
    sowing_date: Mapped[date | None] = mapped_column(DATE)
    harvest_date: Mapped[date | None] = mapped_column(DATE)
    yield_kg: Mapped[Decimal | None] = mapped_column(Numeric(10, 2))
    notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
