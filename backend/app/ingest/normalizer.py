"""
Signal normalizer — converts raw connector output into a unified RawSignal schema
with pre-validation and enrichment before dispatching to Celery.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, Field

from app.ingest.connectors.base import RawSignal

# Map connector source names to likely signal types (hint for LLM)
SOURCE_SIGNAL_TYPE_HINT = {
    "cert_in": "CERT_IN_ADVISORY",
    "cve_nvd": "CRITICAL_BREACH",
    "rbi_enforcement": "REGULATORY_ACTION",
    "mca21": "MCA_ANOMALY",
    "hibp": "DATA_LEAK",
    "shodan": "CRITICAL_BREACH",
    "news_feed": "NEGATIVE_NEWS",
    "dark_web": "CRITICAL_BREACH",
}

# Minimum text length to be worth processing
MIN_TEXT_LENGTH = 30


class NormalizedSignal(BaseModel):
    source: str
    raw_text: str
    url: str | None = None
    published_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    vendor_hint: str | None = None
    signal_type_hint: str = "UNKNOWN"
    extra: dict[str, Any] = Field(default_factory=dict)


def normalize(raw: RawSignal) -> NormalizedSignal | None:
    """
    Validate and enrich a RawSignal.

    Returns None if the signal should be dropped (too short, duplicate hint, etc.).
    """
    text = (raw.raw_text or "").strip()
    if len(text) < MIN_TEXT_LENGTH:
        return None

    published = raw.published_at or datetime.now(timezone.utc)

    return NormalizedSignal(
        source=raw.source,
        raw_text=text[:8000],  # cap at 8k chars
        url=raw.url,
        published_at=published,
        vendor_hint=raw.vendor_hint,
        signal_type_hint=SOURCE_SIGNAL_TYPE_HINT.get(raw.source, "UNKNOWN"),
        extra=raw.extra or {},
    )


def normalize_batch(raw_signals: list[RawSignal]) -> list[NormalizedSignal]:
    """Normalize a list of raw signals, dropping invalid ones."""
    result: list[NormalizedSignal] = []
    seen_texts: set[str] = set()

    for raw in raw_signals:
        normalized = normalize(raw)
        if normalized is None:
            continue
        # Deduplicate by first 100 chars of text
        key = normalized.raw_text[:100]
        if key in seen_texts:
            continue
        seen_texts.add(key)
        result.append(normalized)

    return result
