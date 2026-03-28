from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, Field


class FarmlandBase(BaseModel):
    name: str = Field(..., max_length=100)
    area: Decimal = Field(..., gt=0, description="面积（亩）")
    location: str | None = Field(None, max_length=200)
    latitude: Decimal | None = None
    longitude: Decimal | None = None
    soil_type: str | None = Field(None, max_length=50)
    crop_type: str | None = Field(None, max_length=100)
    crop_stage: str | None = Field(None, max_length=50)
    sowing_date: date | None = None
    notes: str | None = None


class FarmlandCreate(FarmlandBase):
    pass


class FarmlandUpdate(BaseModel):
    name: str | None = Field(None, max_length=100)
    area: Decimal | None = Field(None, gt=0)
    location: str | None = Field(None, max_length=200)
    latitude: Decimal | None = None
    longitude: Decimal | None = None
    soil_type: str | None = Field(None, max_length=50)
    crop_type: str | None = Field(None, max_length=100)
    crop_stage: str | None = Field(None, max_length=50)
    sowing_date: date | None = None
    notes: str | None = None


class FarmlandResponse(FarmlandBase):
    id: str
    owner_id: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
