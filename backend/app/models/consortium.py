import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, Integer, String, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class ConsortiumNode(Base):
    __tablename__ = "consortium_nodes"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    bank_name: Mapped[str] = mapped_column(String, nullable=False)
    node_status: Mapped[str] = mapped_column(String, nullable=False, default="offline")
    last_signal_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    vendors_monitored: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )


class ConsortiumSignal(Base):
    __tablename__ = "consortium_signals"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    signal_type: Mapped[str] = mapped_column(String, nullable=False)
    dimension: Mapped[str | None] = mapped_column(String, nullable=True)
    vendor_hash: Mapped[str] = mapped_column(String, nullable=False)
    severity: Mapped[str] = mapped_column(String, nullable=False)
    cert_in_relevant: Mapped[bool] = mapped_column(Boolean, default=False)
    source_node: Mapped[str] = mapped_column(String, default="REDACTED")
    received_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
