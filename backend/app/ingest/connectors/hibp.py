"""HaveIBeenPwned connector — checks for credential leaks by vendor domain."""
from __future__ import annotations

import logging
from datetime import datetime, timezone

from app.ingest.connectors.base import BaseConnector, RawSignal

logger = logging.getLogger(__name__)

HIBP_BREACHES_URL = "https://haveibeenpwned.com/api/v3/breaches"


class HIBPConnector(BaseConnector):
    source_name = "hibp"
    _rate_limit_seconds = 86400.0  # 24 hours — HIBP data doesn't change frequently

    async def fetch(self, vendor_names: list[str]) -> list[RawSignal]:
        if not self.api_key:
            logger.info("HIBP connector: no API key configured — skipping")
            return []

        try:
            import httpx  # type: ignore[import]
        except ImportError:
            logger.warning("httpx not installed — skipping HIBP fetch")
            return []

        # Fetch all breaches once and filter locally
        try:
            async with httpx.AsyncClient(timeout=15) as client:
                resp = await client.get(
                    HIBP_BREACHES_URL,
                    headers={
                        "hibp-api-key": self.api_key,
                        "user-agent": "ThirdEye Risk Platform/1.0",
                    },
                )
                resp.raise_for_status()
                all_breaches: list[dict] = resp.json()
        except Exception as exc:
            logger.error("HIBP API error: %s", exc)
            return []

        signals: list[RawSignal] = []
        for vendor_name in vendor_names:
            # Match by domain or breach title containing vendor name
            vendor_lower = vendor_name.lower().replace(" ", "")
            matching = [
                b for b in all_breaches
                if vendor_lower in (b.get("Domain") or "").lower()
                or vendor_lower in (b.get("Name") or "").lower()
            ]

            for breach in matching:
                data_classes = ", ".join(breach.get("DataClasses", []))
                pwn_count = breach.get("PwnCount", 0)
                breach_date = breach.get("BreachDate", "unknown")
                text = (
                    f"HIBP credential leak: {vendor_name} breach '{breach.get('Name')}' "
                    f"on {breach_date}. "
                    f"{pwn_count:,} accounts compromised. "
                    f"Data exposed: {data_classes}."
                )
                signals.append(RawSignal(
                    source=self.source_name,
                    raw_text=text,
                    url=f"https://haveibeenpwned.com/PwnedWebsites#{breach.get('Name', '')}",
                    published_at=datetime.now(timezone.utc),
                    vendor_hint=vendor_name,
                    extra={
                        "breach_name": breach.get("Name"),
                        "pwn_count": pwn_count,
                        "data_classes": breach.get("DataClasses", []),
                    },
                ))

        return signals
