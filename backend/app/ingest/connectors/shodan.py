"""Shodan connector — open ports/services per vendor domain."""
from __future__ import annotations

import logging
from datetime import datetime, timezone

from app.ingest.connectors.base import BaseConnector, RawSignal

logger = logging.getLogger(__name__)

SHODAN_SEARCH_URL = "https://api.shodan.io/shodan/host/search"

# High-risk open ports that indicate poor cyber hygiene
HIGH_RISK_PORTS = {
    21: "FTP", 23: "Telnet", 445: "SMB", 3389: "RDP",
    5900: "VNC", 1433: "MSSQL", 3306: "MySQL", 6379: "Redis",
    27017: "MongoDB", 9200: "Elasticsearch",
}


class ShodanConnector(BaseConnector):
    source_name = "shodan"
    _rate_limit_seconds = 21600.0  # 6 hours

    async def fetch(self, vendor_names: list[str]) -> list[RawSignal]:
        if not self.api_key:
            logger.info("Shodan connector: no API key configured — skipping")
            return []

        try:
            import httpx  # type: ignore[import]
        except ImportError:
            logger.warning("httpx not installed — skipping Shodan fetch")
            return []

        signals: list[RawSignal] = []

        for vendor_name in vendor_names[:20]:
            try:
                async with httpx.AsyncClient(timeout=15) as client:
                    resp = await client.get(
                        SHODAN_SEARCH_URL,
                        params={
                            "key": self.api_key,
                            "query": f"org:{vendor_name}",
                            "minify": "true",
                        },
                    )
                    resp.raise_for_status()
                    data = resp.json()
            except Exception as exc:
                logger.debug("Shodan error for %s: %s", vendor_name, exc)
                continue

            matches = data.get("matches", [])
            open_risk_ports: list[str] = []
            for match in matches:
                port = match.get("port", 0)
                if port in HIGH_RISK_PORTS:
                    open_risk_ports.append(f"{port}/{HIGH_RISK_PORTS[port]}")

            if open_risk_ports:
                unique_ports = list(set(open_risk_ports))
                text = (
                    f"Shodan scan: {vendor_name} has {len(matches)} exposed services. "
                    f"High-risk open ports: {', '.join(unique_ports)}. "
                    "These ports indicate potential attack surface."
                )
                signals.append(RawSignal(
                    source=self.source_name,
                    raw_text=text,
                    published_at=datetime.now(timezone.utc),
                    vendor_hint=vendor_name,
                    extra={
                        "open_ports": unique_ports,
                        "total_exposed": len(matches),
                    },
                ))

        return signals
