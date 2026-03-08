"""
Dark web connector — stub.

TODO: Integrate with a threat intelligence feed (e.g., Recorded Future, Intel 471,
or a MISP instance) for dark web monitoring of vendor credential leaks and chatter.
"""
from __future__ import annotations

import logging

from app.ingest.connectors.base import BaseConnector, RawSignal

logger = logging.getLogger(__name__)


class DarkWebConnector(BaseConnector):
    source_name = "dark_web"
    _rate_limit_seconds = 3600.0

    async def fetch(self, vendor_names: list[str]) -> list[RawSignal]:
        """
        TODO: Implement dark web threat intelligence integration.

        Potential integrations:
        - Recorded Future API: /v2/alert/search for vendor names on dark forums
        - Intel 471 Cybercrime Intelligence API
        - MISP threat sharing platform
        - Flare Systems API

        For now, returns empty list — no real data available.
        """
        logger.debug("Dark web connector: stub — no integration configured")
        return []
