from datetime import datetime

from pydantic import BaseModel, Field


class UserBase(BaseModel):
    username: str
    phone: str
    real_name: str | None = None
    province: str | None = None
    city: str | None = None
    role: str = "farmer"
    avatar_url: str | None = None


class UserCreate(UserBase):
    password: str = Field(..., min_length=6)


class UserUpdate(BaseModel):
    real_name: str | None = None
    province: str | None = None
    city: str | None = None
    avatar_url: str | None = None


class UserResponse(UserBase):
    id: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
