"""CERT-In advisories RSS connector."""
from __future__ import annotations

import logging
import xml.etree.ElementTree as ElementTree
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime

from app.ingest.connectors.base import BaseConnector, RawSignal

logger = logging.getLogger(__name__)

CERT_IN_RSS = "https://www.cert-in.org.in/s2cMainServlet?pageid=PUBVLNOTES01&type=rss"


class CertInConnector(BaseConnector):
    source_name = "cert_in"
    _rate_limit_seconds = 3600.0

    async def fetch(self, vendor_names: list[str]) -> list[RawSignal]:
        try:
            import httpx  # type: ignore[import]
        except ImportError:
            logger.warning("httpx not installed — skipping CERT-In fetch")
            return []

        try:
            async with httpx.AsyncClient(timeout=15) as client:
                resp = await client.get(CERT_IN_RSS)
                resp.raise_for_status()
                root = ElementTree.fromstring(resp.text)
        except Exception as exc:
            logger.error("CERT-In RSS error: %s", exc)
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

            text = f"CERT-In Advisory: {title}. {desc}"
            vendor_hint = next(
                (name for name in vendor_names if name.lower() in text.lower()), None
            )

            signals.append(RawSignal(
                source=self.source_name,
                raw_text=text.strip(),
                url=link,
                published_at=published,
                vendor_hint=vendor_hint,
                extra={"advisory_type": "cert_in"},
            ))

        return signals
