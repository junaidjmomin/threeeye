import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, Integer, String, DateTime, Date, JSON
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Vendor(Base):
    __tablename__ = "vendors"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String, nullable=False)
    category: Mapped[str] = mapped_column(String, nullable=False)
    tier: Mapped[str] = mapped_column(String, nullable=False, default="standard")

    # Scores
    composite_score: Mapped[int] = mapped_column(Integer, nullable=False, default=100)
    previous_score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    risk_band: Mapped[str] = mapped_column(String, nullable=False, default="stable", index=True)

    # 9 dimension scores
    score_cybersecurity: Mapped[int] = mapped_column(Integer, nullable=False, default=100)
    score_regulatory: Mapped[int] = mapped_column(Integer, nullable=False, default=100)
    score_operational: Mapped[int] = mapped_column(Integer, nullable=False, default=100)
    score_news_legal: Mapped[int] = mapped_column(Integer, nullable=False, default=100)
    score_financial_health: Mapped[int] = mapped_column(Integer, nullable=False, default=100)
    score_data_privacy: Mapped[int] = mapped_column(Integer, nullable=False, default=100)
    score_concentration: Mapped[int] = mapped_column(Integer, nullable=False, default=100)
    score_esg: Mapped[int] = mapped_column(Integer, nullable=False, default=100)
    score_fourth_party: Mapped[int] = mapped_column(Integer, nullable=False, default=100)

    # Metadata
    contract_expiry: Mapped[datetime | None] = mapped_column(Date, nullable=True)
    last_assessed: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    triggers: Mapped[list[str]] = mapped_column(JSON, default=list)

    # CERT-In 6-hour clock
    cert_in_clock_active: Mapped[bool] = mapped_column(Boolean, default=False)
    cert_in_clock_started: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    def to_dimensions_dict(self) -> dict[str, int]:
        return {
            "cybersecurity": self.score_cybersecurity,
            "regulatory": self.score_regulatory,
            "operational": self.score_operational,
            "newsLegal": self.score_news_legal,
            "financialHealth": self.score_financial_health,
            "dataPrivacy": self.score_data_privacy,
            "concentration": self.score_concentration,
            "esg": self.score_esg,
            "fourthParty": self.score_fourth_party,
        }

    def cert_in_clock_dict(self) -> dict | None:
        if not self.cert_in_clock_active or not self.cert_in_clock_started:
            return None
        now = datetime.now(timezone.utc)
        elapsed = now - self.cert_in_clock_started
        remaining_seconds = max(0, 6 * 3600 - elapsed.total_seconds())
        hours = int(remaining_seconds // 3600)
        minutes = int((remaining_seconds % 3600) // 60)
        seconds = int(remaining_seconds % 60)
        return {
            "active": True,
            "remaining": f"{hours:02d}:{minutes:02d}:{seconds:02d}",
            "startedAt": self.cert_in_clock_started.isoformat(),
        }
