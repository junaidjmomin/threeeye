import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class ScoreAuditLog(Base):
    """Append-only table. Never update or delete rows."""

    __tablename__ = "score_audit_log"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    vendor_id: Mapped[str] = mapped_column(String, ForeignKey("vendors.id"), nullable=False, index=True)
    old_composite: Mapped[int | None] = mapped_column(Integer, nullable=True)
    new_composite: Mapped[int | None] = mapped_column(Integer, nullable=True)
    old_band: Mapped[str | None] = mapped_column(String, nullable=True)
    new_band: Mapped[str | None] = mapped_column(String, nullable=True)
    dimension_affected: Mapped[str | None] = mapped_column(String, nullable=True)
    old_dimension_score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    new_dimension_score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    trigger_signal: Mapped[str] = mapped_column(String, nullable=False)
    model_version: Mapped[str] = mapped_column(String, nullable=False, default="manual_v1")
    rule_activated: Mapped[str | None] = mapped_column(String, nullable=True)
    regulatory_citation: Mapped[str | None] = mapped_column(String, nullable=True)
    recommended_action: Mapped[str | None] = mapped_column(String, nullable=True)
    actor: Mapped[str] = mapped_column(String, nullable=False, default="system")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
