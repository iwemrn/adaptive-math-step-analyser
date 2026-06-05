import uuid
from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.db import Base
from app.models.base import UUIDMixin, TimestampMixin

class Attempt(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "attempts"

    user_id: Mapped[uuid.UUID | None] = mapped_column(nullable=True)
    problem_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("problems.id"), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(50), default="active", nullable=False)

    steps = relationship("Step", back_populates="attempt", cascade="all, delete-orphan")
