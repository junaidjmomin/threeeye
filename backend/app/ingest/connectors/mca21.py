"""
MCA21 connector — Ministry of Corporate Affairs company filings.

Checks for filing anomalies: overdue annual returns, missing financial statements.
Note: MCA21 does not have a public API; this uses their public search endpoint.
"""
from __future__ import annotations

import logging
from datetime import datetime, timezone

from app.ingest.connectors.base import BaseConnector, RawSignal

logger = logging.getLogger(__name__)

MCA21_SEARCH_URL = "https://www.mca.gov.in/mcafoportal/showCheckCompanyName.do"


class MCA21Connector(BaseConnector):
    source_name = "mca21"
    _rate_limit_seconds = 7200.0  # 2 hours — be conservative with scraping

    async def fetch(self, vendor_names: list[str]) -> list[RawSignal]:
        """
        Fetch MCA21 filing status for each vendor.

        Currently a stub — MCA21 requires captcha/session for full data.
        Returns synthetic anomaly signals for vendors with known filing issues.
        TODO: Integrate with MCA21 data feed API when available.
        """
        # TODO: Replace with real MCA21 API integration when available
        # For now, return empty list — real implementation requires credentials
        logger.info("MCA21 connector: stub — no real API integration yet")
        return []

    async def _check_company(self, company_name: str) -> RawSignal | None:
        """Check a single company's filing status on MCA21."""
        try:
            import httpx  # type: ignore[import]
            async with httpx.AsyncClient(timeout=15) as client:
                resp = await client.get(
                    MCA21_SEARCH_URL,
                    params={"companyName": company_name},
                    headers={"User-Agent": "ThirdEye Risk Platform/1.0"},
                )
                # Parse response for filing anomalies
                if "overdue" in resp.text.lower() or "defaulter" in resp.text.lower():
                    return RawSignal(
                        source=self.source_name,
                        raw_text=f"MCA21 filing anomaly detected for {company_name}: overdue filing",
                        published_at=datetime.now(timezone.utc),
                        vendor_hint=company_name,
                        extra={"signal_type": "MCA_ANOMALY"},
                    )
        except Exception as exc:
            logger.debug("MCA21 check failed for %s: %s", company_name, exc)
        return None
