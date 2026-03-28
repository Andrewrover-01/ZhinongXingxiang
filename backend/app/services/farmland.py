from typing import Optional

from sqlalchemy.orm import Session

from app.models.farmland import Farmland
from app.schemas.farmland import FarmlandCreate, FarmlandUpdate


def get_farmland(db: Session, farmland_id: str, owner_id: str) -> Optional[Farmland]:
    return (
        db.query(Farmland)
        .filter(Farmland.id == farmland_id, Farmland.owner_id == owner_id)
        .first()
    )


def list_farmlands(db: Session, owner_id: str, skip: int = 0, limit: int = 100) -> list[Farmland]:
    return (
        db.query(Farmland)
        .filter(Farmland.owner_id == owner_id)
        .order_by(Farmland.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def create_farmland(db: Session, owner_id: str, data: FarmlandCreate) -> Farmland:
    farmland = Farmland(owner_id=owner_id, **data.model_dump())
    db.add(farmland)
    db.commit()
    db.refresh(farmland)
    return farmland


def update_farmland(db: Session, farmland: Farmland, data: FarmlandUpdate) -> Farmland:
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(farmland, field, value)
    db.commit()
    db.refresh(farmland)
    return farmland


def delete_farmland(db: Session, farmland: Farmland) -> None:
    db.delete(farmland)
    db.commit()
