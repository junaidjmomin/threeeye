import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class WorkflowItem(Base):
    __tablename__ = "workflow_items"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    vendor_id: Mapped[str] = mapped_column(String, ForeignKey("vendors.id"), nullable=False, index=True)
    vendor_name: Mapped[str] = mapped_column(String, nullable=False)
    title: Mapped[str] = mapped_column(String, nullable=False)
    priority: Mapped[str] = mapped_column(String, nullable=False, default="medium")
    status: Mapped[str] = mapped_column(String, nullable=False, default="open", index=True)
    assigned_to: Mapped[str] = mapped_column(String, nullable=False, default="")
    assigned_role: Mapped[str] = mapped_column(String, nullable=False, default="")
    due_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    resolution: Mapped[str | None] = mapped_column(String, nullable=True)
    audit_trail_id: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
