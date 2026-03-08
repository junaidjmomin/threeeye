"""RBI enforcement actions connector — parses RBI press releases RSS."""
from __future__ import annotations

import logging
import xml.etree.ElementTree as ElementTree
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime

from app.ingest.connectors.base import BaseConnector, RawSignal

logger = logging.getLogger(__name__)

RBI_PRESS_RSS = "https://rbi.org.in/scripts/rss.aspx?Id=316"  # Enforcement Actions


class RBIEnforcementConnector(BaseConnector):
    source_name = "rbi_enforcement"
    _rate_limit_seconds = 7200.0

    async def fetch(self, vendor_names: list[str]) -> list[RawSignal]:
        try:
            import httpx  # type: ignore[import]
        except ImportError:
            logger.warning("httpx not installed — skipping RBI enforcement fetch")
            return []

        try:
            async with httpx.AsyncClient(timeout=15) as client:
                resp = await client.get(RBI_PRESS_RSS)
                resp.raise_for_status()
                root = ElementTree.fromstring(resp.text)
        except Exception as exc:
            logger.error("RBI RSS error: %s", exc)
            return []

        signals: list[RawSignal] = []
        for item in root.findall(".//item"):
            title = item.findtext("title") or ""
            desc = item.findtext("description") or ""
            link = item.findtext("link") or ""
            pub_str = item.findtext("pubDate") or ""

            published: datetime | None = None
            if pub_str:
                try:
                    published = parsedate_to_datetime(pub_str).replace(tzinfo=timezone.utc)
                except Exception:
                    pass

            text = f"RBI Enforcement: {title}. {desc}"
            vendor_hint = next(
                (name for name in vendor_names if name.lower() in text.lower()), None
            )

            signals.append(RawSignal(
                source=self.source_name,
                raw_text=text.strip(),
                url=link,
                published_at=published,
                vendor_hint=vendor_hint,
                extra={"regulatory_body": "RBI"},
            ))

        return signals
