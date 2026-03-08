"""Celery tasks for data ingestion from all connector sources."""
from __future__ import annotations

import asyncio
import logging

from app.workers.celery_app import celery_app

logger = logging.getLogger(__name__)


def _run_async(coro):
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


async def _get_vendor_names() -> list[str]:
    """Fetch all active vendor names from the database."""
    from sqlalchemy import select

    from app.core.database import AsyncSessionLocal
    from app.models.vendor import Vendor

    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Vendor.name))
        return [row[0] for row in result.fetchall() if row[0]]


async def _ingest_and_dispatch(connector_cls, api_key: str = "", base_url: str = "") -> int:
    """Instantiate a connector, fetch signals, normalize, and dispatch."""
    from app.ingest.dispatcher import dispatch_batch
    from app.ingest.normalizer import normalize_batch

    vendor_names = await _get_vendor_names()
    if not vendor_names:
        logger.info("No vendors in DB — skipping ingestion")
        return 0

    connector = connector_cls(api_key=api_key, base_url=base_url)
    raw_signals = await connector.fetch(vendor_names)
    normalized = normalize_batch(raw_signals)
    dispatched = dispatch_batch(normalized)
    logger.info(
        "%s: fetched=%d normalized=%d dispatched=%d",
        connector.source_name, len(raw_signals), len(normalized), dispatched,
    )
    return dispatched


@celery_app.task(name="tasks.ingest_news")
def ingest_news():
    """Ingest news signals — runs every 15 minutes via beat schedule."""
    from app.core.config import settings
    from app.ingest.connectors.news_feed import NewsFeedConnector

    api_key = getattr(settings, "NEWS_API_KEY", "")
    _run_async(_ingest_and_dispatch(NewsFeedConnector, api_key=api_key))


@celery_app.task(name="tasks.ingest_cve")
def ingest_cve():
    """Ingest CVE/NVD signals — runs every hour."""
    from app.core.config import settings
    from app.ingest.connectors.cve_nvd import CVENVDConnector

    api_key = getattr(settings, "NVD_API_KEY", "")
    _run_async(_ingest_and_dispatch(CVENVDConnector, api_key=api_key))


@celery_app.task(name="tasks.ingest_cert_in")
def ingest_cert_in():
    """Ingest CERT-In advisories — runs every hour."""
    from app.ingest.connectors.cert_in import CertInConnector
    _run_async(_ingest_and_dispatch(CertInConnector))


@celery_app.task(name="tasks.ingest_rbi_enforcement")
def ingest_rbi_enforcement():
    """Ingest RBI enforcement actions — runs every 6 hours."""
    from app.ingest.connectors.rbi_enforcement import RBIEnforcementConnector
    _run_async(_ingest_and_dispatch(RBIEnforcementConnector))


@celery_app.task(name="tasks.ingest_shodan")
def ingest_shodan():
    """Ingest Shodan open port/service data — runs every 6 hours."""
    from app.core.config import settings
    from app.ingest.connectors.shodan import ShodanConnector

    api_key = getattr(settings, "SHODAN_API_KEY", "")
    _run_async(_ingest_and_dispatch(ShodanConnector, api_key=api_key))


@celery_app.task(name="tasks.ingest_hibp")
def ingest_hibp():
    """Ingest HaveIBeenPwned credential leaks — runs every 24 hours."""
    from app.core.config import settings
    from app.ingest.connectors.hibp import HIBPConnector

    api_key = getattr(settings, "HIBP_API_KEY", "")
    _run_async(_ingest_and_dispatch(HIBPConnector, api_key=api_key))
