from pydantic import BaseModel, Field


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    user_id: str | None = None


class LoginRequest(BaseModel):
    username: str = Field(..., description="用户名或手机号")
    password: str = Field(..., min_length=6)


class RegisterRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    phone: str = Field(..., pattern=r"^1[3-9]\d{9}$", description="手机号")
    password: str = Field(..., min_length=6, max_length=100)
    real_name: str | None = Field(None, max_length=50)
    province: str | None = Field(None, max_length=50)
    city: str | None = Field(None, max_length=50)
