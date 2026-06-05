import uuid
from sqlalchemy import ForeignKey, Float, Boolean
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from app.core.db import Base
from app.models.base import UUIDMixin, TimestampMixin

class AnalysisResult(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "analysis_results"

    step_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("steps.id"), nullable=False, unique=True, index=True)
    is_valid: Mapped[bool] = mapped_column(Boolean, nullable=False)
    soft_score: Mapped[float] = mapped_column(Float, nullable=False)
    math_score: Mapped[float] = mapped_column(Float, nullable=False)
    logic_score: Mapped[float] = mapped_column(Float, nullable=False)
    condition_score: Mapped[float] = mapped_column(Float, nullable=False)
    goal_score: Mapped[float] = mapped_column(Float, nullable=False)
    error_probs_json: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    feedback_json: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
