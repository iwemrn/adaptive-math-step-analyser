from datetime import datetime

from sqlalchemy import DateTime, Float, Integer, String, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base
from app.models.base import TimestampMixin, UUIDMixin


class StudentProfile(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "student_profiles"

    profile_key: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)

    overall_mastery: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)

    total_steps: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    correct_steps: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    incorrect_steps: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    topic_mastery_json: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    misconception_stats_json: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )
