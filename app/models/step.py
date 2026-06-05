import uuid
from sqlalchemy import ForeignKey, Integer, Text, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.db import Base
from app.models.base import UUIDMixin, TimestampMixin

class Step(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "steps"

    attempt_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("attempts.id"), nullable=False, index=True)
    step_order: Mapped[int] = mapped_column(Integer, nullable=False)
    raw_text: Mapped[str] = mapped_column(Text, nullable=False)
    normalized_before: Mapped[str | None] = mapped_column(Text, nullable=True)
    normalized_after: Mapped[str | None] = mapped_column(Text, nullable=True)
    operation_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    diagnostics_json: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    attempt = relationship("Attempt", back_populates="steps")
