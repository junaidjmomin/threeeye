"""
NVD/CVE connector — polls NIST NVD REST API v2.0 for recent CVEs.

Maps CWE categories to ThirdEye risk dimensions.
"""
from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone

from app.ingest.connectors.base import BaseConnector, RawSignal

logger = logging.getLogger(__name__)

NVD_API_URL = "https://services.nvd.nist.gov/rest/json/cves/2.0"

# Map CWE IDs / categories to risk dimensions
CWE_DIMENSION_MAP = {
    "CWE-89": "cybersecurity",   # SQL injection
    "CWE-79": "cybersecurity",   # XSS
    "CWE-78": "cybersecurity",   # OS Command injection
    "CWE-22": "cybersecurity",   # Path traversal
    "CWE-200": "dataPrivacy",    # Exposure of sensitive info
    "CWE-306": "cybersecurity",  # Missing auth
    "CWE-502": "cybersecurity",  # Deserialization
}


class CVENVDConnector(BaseConnector):
    source_name = "cve_nvd"
    _rate_limit_seconds = 3600.0  # 1 hour

    async def fetch(self, vendor_names: list[str]) -> list[RawSignal]:
        try:
            import httpx  # type: ignore[import]
        except ImportError:
            logger.warning("httpx not installed — skipping NVD fetch")
            return []

        signals: list[RawSignal] = []
        now = datetime.now(timezone.utc)
        since = now - timedelta(hours=24)

        pub_start = since.strftime("%Y-%m-%dT%H:%M:%S.000")
        pub_end = now.strftime("%Y-%m-%dT%H:%M:%S.000")

        headers = {}
        if self.api_key:
            headers["apiKey"] = self.api_key

        try:
            async with httpx.AsyncClient(timeout=30, headers=headers) as client:
                resp = await client.get(
                    NVD_API_URL,
                    params={
                        "pubStartDate": pub_start,
                        "pubEndDate": pub_end,
                        "resultsPerPage": 50,
                    },
                )
                resp.raise_for_status()
                data = resp.json()
        except Exception as exc:
            logger.error("NVD API error: %s", exc)
            return []

        for vuln in data.get("vulnerabilities", []):
            cve = vuln.get("cve", {})
            cve_id = cve.get("id", "")
            descriptions = cve.get("descriptions", [])
            desc_text = next(
                (d["value"] for d in descriptions if d.get("lang") == "en"),
                ""
            )

            # Check if any vendor name appears in CVE description
            vendor_hint = next(
                (name for name in vendor_names if name.lower() in desc_text.lower()),
                None,
            )

            # Determine severity from CVSS
            metrics = cve.get("metrics", {})
            cvss_score = 5.0
            for key in ("cvssMetricV31", "cvssMetricV30", "cvssMetricV2"):
                entries = metrics.get(key, [])
                if entries:
                    cvss_score = entries[0].get("cvssData", {}).get("baseScore", 5.0)
                    break

            text = f"CVE: {cve_id}. {desc_text} CVSS: {cvss_score}"
            signals.append(RawSignal(
                source=self.source_name,
                raw_text=text,
                url=f"https://nvd.nist.gov/vuln/detail/{cve_id}",
                published_at=now,
                vendor_hint=vendor_hint,
                extra={"cve_id": cve_id, "cvss_score": cvss_score},
            ))

        return signals
