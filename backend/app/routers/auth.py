from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.core.limiter import limiter
from app.core.security import create_access_token
from app.schemas.auth import LoginRequest, RegisterRequest, Token
from app.schemas.user import UserResponse
from app.services.user import authenticate_user, create_user, get_user_by_phone, get_user_by_username
from app.routers.deps import get_current_user
from app.models.user import User

router = APIRouter(prefix="/auth", tags=["认证"])

_AUTH_COOKIE = "access_token"


def _set_auth_cookie(response: Response, token: str) -> None:
    """Attach the JWT as an httpOnly cookie to the given response."""
    response.set_cookie(
        key=_AUTH_COOKIE,
        value=token,
        httponly=True,
        secure=settings.APP_ENV == "production",  # HTTPS-only in production
        samesite="lax",
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        path="/",
    )


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("5/minute")
def register(
    request: Request,
    data: RegisterRequest,
    db: Annotated[Session, Depends(get_db)],
):
    """用户注册"""
    if get_user_by_username(db, data.username):
        raise HTTPException(status_code=400, detail="用户名已存在")
    if get_user_by_phone(db, data.phone):
        raise HTTPException(status_code=400, detail="手机号已注册")
    user = create_user(db, data)
    return user


@router.post("/login", response_model=Token)
@limiter.limit("5/minute")
def login(
    request: Request,
    data: LoginRequest,
    response: Response,
    db: Annotated[Session, Depends(get_db)],
):
    """用户登录（支持用户名或手机号）"""
    user = authenticate_user(db, data.username, data.password)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(
        subject=user.id,
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    _set_auth_cookie(response, access_token)
    return Token(access_token=access_token)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(response: Response):
    """退出登录（清除认证 Cookie）"""
    response.delete_cookie(key=_AUTH_COOKIE, path="/")


@router.get("/me", response_model=UserResponse)
def get_me(current_user: Annotated[User, Depends(get_current_user)]):
    """获取当前登录用户信息"""
    return current_user
