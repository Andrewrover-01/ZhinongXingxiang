import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import Boolean, DateTime, ForeignKey, JSON, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class RecognitionRecord(Base):
    __tablename__ = "recognition_records"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    farmland_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("farmlands.id", ondelete="SET NULL"), index=True)
    image_url: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    crop_type: Mapped[str | None] = mapped_column(String(100))
    diagnosis: Mapped[str | None] = mapped_column(String(200))
    # mild | moderate | severe
    severity: Mapped[str | None] = mapped_column(String(20))
    confidence: Mapped[Decimal | None] = mapped_column(Numeric(5, 4))
    treatment_plan: Mapped[str | None] = mapped_column(Text)
    medicine_suggest: Mapped[str | None] = mapped_column(Text)
    rag_sources: Mapped[dict | None] = mapped_column(JSON)
    llm_model: Mapped[str | None] = mapped_column(String(100))
    is_confirmed: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    expert_review: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)

    user: Mapped["User"] = relationship(back_populates="recognition_records")  # noqa: F821
    farmland: Mapped["Farmland | None"] = relationship(back_populates="recognition_records")  # noqa: F821


class PolicyChatHistory(Base):
    __tablename__ = "policy_chat_history"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    session_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    # user | assistant
    role: Mapped[str] = mapped_column(String(10), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    rag_sources: Mapped[dict | None] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
