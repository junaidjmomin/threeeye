"""Abstract base connector for all data ingestion sources."""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class RawSignal:
    """Unified raw signal before LLM parsing and normalisation."""
    source: str                    # connector name e.g. "news_feed", "cve_nvd"
    raw_text: str                  # original text content
    url: Optional[str] = None      # source URL if available
    published_at: Optional[datetime] = None
    vendor_hint: Optional[str] = None   # vendor name if already known
    extra: dict = field(default_factory=dict)  # source-specific metadata


class BaseConnector(ABC):
    """
    Abstract connector. Each source implements fetch() to return RawSignals.

    Rate limiting: subclasses set _rate_limit_seconds to avoid hammering APIs.
    """
    source_name: str = "unknown"
    _rate_limit_seconds: float = 60.0

    def __init__(self, api_key: str = "", base_url: str = "") -> None:
        self.api_key = api_key
        self.base_url = base_url

    @abstractmethod
    async def fetch(self, vendor_names: list[str]) -> list[RawSignal]:
        """
        Fetch raw signals for the given vendor names.
        Returns list of RawSignal objects.
        """
        ...

    async def __aenter__(self) -> "BaseConnector":
        return self

    async def __aexit__(self, *args: object) -> None:
        pass
