import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Signal(Base):
    __tablename__ = "signals"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    vendor_id: Mapped[str | None] = mapped_column(
        String, ForeignKey("vendors.id"), nullable=True, index=True
    )
    source: Mapped[str] = mapped_column(String, nullable=False)
    source_url: Mapped[str | None] = mapped_column(String, nullable=True)
    raw_text: Mapped[str | None] = mapped_column(String, nullable=True)
    parsed_dimension: Mapped[str | None] = mapped_column(String, nullable=True)
    parsed_severity: Mapped[int | None] = mapped_column(Integer, nullable=True)
    parsed_summary: Mapped[str | None] = mapped_column(String, nullable=True)
    regulatory_flag: Mapped[str | None] = mapped_column(String, nullable=True)
    is_processed: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    llm_model_used: Mapped[str | None] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
