"""Celery tasks for alert creation, signal processing, and CERT-In clock management."""
from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timezone

from app.workers.celery_app import celery_app

logger = logging.getLogger(__name__)


def _run_async(coro):
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


@celery_app.task(name="tasks.process_score_change")
def process_score_change(vendor_id: str, old_score: int, new_score: int):
    """
    Called when a vendor's composite score changes band.
    - Creates an Alert record
    - Creates a WorkflowItem if critical/high
    - Broadcasts vendor_score_update via WebSocket
    """
    _run_async(_process_score_change_async(vendor_id, old_score, new_score))


async def _process_score_change_async(
    vendor_id: str,
    old_score: int,
    new_score: int,
) -> None:
    from app.core.database import AsyncSessionLocal
    from app.models.alert import Alert
    from app.models.vendor import Vendor
    from app.models.workflow import WorkflowItem
    from app.services.scoring_service import compute_risk_band

    old_band = compute_risk_band(old_score)
    new_band = compute_risk_band(new_score)

    if old_band == new_band:
        return  # no band change, nothing to do

    severity_map = {"critical": "critical", "high": "high", "watch": "medium", "stable": "low"}
    severity = severity_map.get(new_band, "medium")

    async with AsyncSessionLocal() as session:
        vendor = await session.get(Vendor, vendor_id)
        vendor_name = vendor.name if vendor else vendor_id

        # Create alert
        alert = Alert(
            vendor_id=vendor_id,
            title=f"Risk band change: {old_band.upper()} → {new_band.upper()} for {vendor_name}",
            description=(
                f"Composite score moved from {old_score} ({old_band}) to "
                f"{new_score} ({new_band}). "
                f"{'Immediate action required.' if new_band in ('critical', 'high') else 'Monitor closely.'}"
            ),
            severity=severity,
            status="new",
            created_at=datetime.now(timezone.utc),
        )
        session.add(alert)

        # Create workflow item for critical/high escalations
        if new_band in ("critical", "high"):
            workflow = WorkflowItem(
                vendor_id=vendor_id,
                title=f"Investigate {new_band.upper()} risk: {vendor_name}",
                description=(
                    f"Vendor score dropped to {new_score} ({new_band} band). "
                    "Conduct risk review and initiate remediation steps."
                ),
                priority="critical" if new_band == "critical" else "high",
                status="open",
                created_at=datetime.now(timezone.utc),
            )
            session.add(workflow)

        await session.commit()

    logger.info(
        "Score change alert created for vendor %s: %s→%s (%d→%d)",
        vendor_id, old_band, new_band, old_score, new_score,
    )


@celery_app.task(name="tasks.process_signal")
def process_signal(signal_data: dict):
    """
    Process a normalized signal:
    1. LLM parse raw_text → ParsedSignal
    2. Match to a vendor
    3. Persist signal to DB
    4. Trigger rescore for matched vendor
    5. Check rule engine for immediate actions
    """
    _run_async(_process_signal_async(signal_data))


async def _process_signal_async(signal_data: dict) -> None:
    from sqlalchemy import select

    from app.core.config import settings
    from app.core.database import AsyncSessionLocal
    from app.engine.llm.provider import get_provider_from_settings
    from app.engine.llm.signal_parser import parse_signal
    from app.models.signal import Signal
    from app.models.vendor import Vendor

    if not settings.ANTHROPIC_API_KEY and not settings.OPENAI_API_KEY:
        logger.debug("No LLM API key configured — skipping signal LLM parse")
        return

    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Vendor.id, Vendor.name))
        vendors = result.fetchall()
        vendor_names = [v.name for v in vendors]
        vendor_by_name = {v.name: str(v.id) for v in vendors}

    try:
        provider = get_provider_from_settings()
    except Exception as exc:
        logger.error("LLM provider init failed: %s", exc)
        return

    raw_text = signal_data.get("raw_text", "")
    parsed = await parse_signal(raw_text, vendor_names, provider)

    # Low-confidence or no vendor match → skip
    if parsed.confidence < 0.3 or not parsed.vendor_name:
        logger.debug("Signal discarded: confidence=%.2f vendor=%s", parsed.confidence, parsed.vendor_name)
        return

    vendor_id = vendor_by_name.get(parsed.vendor_name)
    if not vendor_id:
        logger.debug("No vendor ID found for name: %s", parsed.vendor_name)
        return

    async with AsyncSessionLocal() as session:
        signal = Signal(
            vendor_id=vendor_id,
            source=signal_data.get("source", "unknown"),
            raw_text=raw_text[:4000],
            parsed_dimension=parsed.dimension,
            parsed_severity=parsed.severity,
            signal_type=parsed.signal_type,
            regulatory_implication=parsed.regulatory_implication,
            confidence=parsed.confidence,
            summary=parsed.summary,
            url=signal_data.get("url"),
            published_at=signal_data.get("published_at"),
            created_at=datetime.now(timezone.utc),
        )
        session.add(signal)
        await session.commit()

    logger.info(
        "Signal persisted: vendor=%s dim=%s severity=%d type=%s",
        parsed.vendor_name, parsed.dimension, parsed.severity, parsed.signal_type,
    )

    # Trigger rescore for the affected vendor
    from app.workers.score_tasks import rescore_vendor
    rescore_vendor.delay(vendor_id)


@celery_app.task(name="tasks.run_compliance_rules")
def run_compliance_rules():
    """Scheduled hourly. Evaluates all regulatory rules against all vendors."""
    _run_async(_run_compliance_rules_async())


async def _run_compliance_rules_async() -> None:
    from datetime import timedelta

    from sqlalchemy import select

    from app.core.database import AsyncSessionLocal
    from app.engine.rules.engine import RuleEngine
    from app.models.alert import Alert
    from app.models.signal import Signal
    from app.models.vendor import Vendor

    rule_engine = RuleEngine()
    since = datetime.now(timezone.utc) - timedelta(days=1)

    async with AsyncSessionLocal() as session:
        vendor_result = await session.execute(select(Vendor))
        vendors = vendor_result.scalars().all()

        triggered_count = 0
        for vendor in vendors:
            sig_result = await session.execute(
                select(Signal)
                .where(Signal.vendor_id == vendor.id)
                .where(Signal.created_at >= since)
            )
            signals = sig_result.scalars().all()
            signal_dicts = [
                {
                    "parsed_dimension": s.parsed_dimension,
                    "parsed_severity": s.parsed_severity,
                    "signal_type": s.signal_type,
                    "summary": s.summary,
                }
                for s in signals
            ]

            vendor_data = {
                "tier": vendor.tier,
                "composite_score": vendor.composite_score or 50,
                "cybersecurity": vendor.cybersecurity,
                "financialHealth": vendor.financial_health,
            }

            results = rule_engine.run_all(vendor_data, signal_dicts)

            for result in results:
                # Create a regulatory compliance alert if not already open
                alert = Alert(
                    vendor_id=str(vendor.id),
                    title=f"[Compliance] {result.action} — {vendor.name}",
                    description=f"{result.rationale}\nCitation: {result.citation}",
                    severity="high" if "CERT_IN" in result.action or "BREACH" in result.action else "medium",
                    status="new",
                    created_at=datetime.now(timezone.utc),
                )
                session.add(alert)
                triggered_count += 1

        await session.commit()

    logger.info("Compliance rules run: %d rules triggered across %d vendors", triggered_count, len(vendors))


@celery_app.task(name="tasks.generate_playbook")
def generate_playbook(vendor_id: str, playbook_type: str, incident_summary: str):
    """LLM-generate a Letter of Concern, Remediation Ticket, or RBI Summary."""
    _run_async(_generate_playbook_async(vendor_id, playbook_type, incident_summary))


async def _generate_playbook_async(
    vendor_id: str,
    playbook_type: str,
    incident_summary: str,
) -> None:
    from app.core.config import settings
    from app.core.database import AsyncSessionLocal
    from app.engine.llm.playbook_generator import generate_playbook as gen
    from app.engine.llm.provider import get_provider_from_settings
    from app.models.report import Report
    from app.models.vendor import Vendor

    if not settings.ANTHROPIC_API_KEY and not settings.OPENAI_API_KEY:
        logger.debug("No LLM API key — skipping playbook generation")
        return

    async with AsyncSessionLocal() as session:
        vendor = await session.get(Vendor, vendor_id)
        if not vendor:
            return

        provider = get_provider_from_settings()
        vendor_data = {
            "vendor_name": vendor.name,
            "tier": vendor.tier,
            "composite_score": vendor.composite_score,
            "previous_score": vendor.previous_score,
            "risk_band": vendor.risk_band,
            "incident_summary": incident_summary,
        }
        content = await gen(playbook_type, vendor_data, provider)

        report = Report(
            vendor_id=vendor_id,
            report_type=playbook_type,
            content=content,
            generated_at=datetime.now(timezone.utc),
        )
        session.add(report)
        await session.commit()

    logger.info("Playbook generated: type=%s vendor=%s", playbook_type, vendor_id)
