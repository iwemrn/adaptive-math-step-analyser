from sqlalchemy import String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from app.core.db import Base
from app.models.base import UUIDMixin, TimestampMixin

class Problem(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "problems"

    topic: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    statement: Mapped[str] = mapped_column(Text, nullable=False)
    expected_answer: Mapped[str | None] = mapped_column(String(255), nullable=True)
    metadata_json: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
