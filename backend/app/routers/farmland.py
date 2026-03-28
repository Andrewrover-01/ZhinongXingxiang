from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.user import User
from app.routers.deps import get_current_user
from app.schemas.farmland import FarmlandCreate, FarmlandResponse, FarmlandUpdate
from app.services import farmland as farmland_svc

router = APIRouter(prefix="/farmlands", tags=["农田管理"])


@router.get("/", response_model=list[FarmlandResponse])
def list_farmlands(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    skip: int = 0,
    limit: int = 100,
):
    """获取当前用户的所有农田"""
    return farmland_svc.list_farmlands(db, current_user.id, skip=skip, limit=limit)


@router.post("/", response_model=FarmlandResponse, status_code=status.HTTP_201_CREATED)
def create_farmland(
    data: FarmlandCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    """创建新农田"""
    return farmland_svc.create_farmland(db, current_user.id, data)


@router.get("/{farmland_id}", response_model=FarmlandResponse)
def get_farmland(
    farmland_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    """获取指定农田详情"""
    farmland = farmland_svc.get_farmland(db, farmland_id, current_user.id)
    if farmland is None:
        raise HTTPException(status_code=404, detail="农田不存在")
    return farmland


@router.put("/{farmland_id}", response_model=FarmlandResponse)
def update_farmland(
    farmland_id: str,
    data: FarmlandUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    """更新农田信息"""
    farmland = farmland_svc.get_farmland(db, farmland_id, current_user.id)
    if farmland is None:
        raise HTTPException(status_code=404, detail="农田不存在")
    return farmland_svc.update_farmland(db, farmland, data)


@router.delete("/{farmland_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_farmland(
    farmland_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    """删除农田"""
    farmland = farmland_svc.get_farmland(db, farmland_id, current_user.id)
    if farmland is None:
        raise HTTPException(status_code=404, detail="农田不存在")
    farmland_svc.delete_farmland(db, farmland)
