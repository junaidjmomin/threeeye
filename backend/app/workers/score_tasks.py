"""Celery tasks for vendor scoring and risk trend snapshots."""
from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timedelta, timezone

from app.workers.celery_app import celery_app

logger = logging.getLogger(__name__)


def _run_async(coro):
    """Run an async coroutine from a sync Celery task."""
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


@celery_app.task(name="tasks.rescore_vendor", bind=True, max_retries=3)
def rescore_vendor(self, vendor_id: str):
    """
    Full AI scoring pipeline for a single vendor:
    1. Load vendor record and recent signals from DB
    2. Build feature vectors per dimension
    3. ML score each dimension
    4. Run correlation engine for compound risks
    5. Compute composite score
    6. Run Policy-as-Code rule engine
    7. Update vendor record in DB
    8. Append score_audit_log entry
    9. Trigger process_score_change if band changed
    """
    try:
        _run_async(_rescore_vendor_async(vendor_id))
    except Exception as exc:
        logger.error("rescore_vendor failed for %s: %s", vendor_id, exc)
        raise self.retry(exc=exc, countdown=60)


async def _rescore_vendor_async(vendor_id: str) -> None:
    from app.core.database import AsyncSessionLocal
    from app.models.vendor import Vendor
    from app.models.signal import Signal
    from app.models.score_audit_log import ScoreAuditLog
    from app.engine.ml.feature_builder import build_all_features
    from app.engine.ml.scorer import score_all_dimensions
    from app.engine.ml.correlation_engine import detect_compound_risks
    from app.engine.rules.engine import RuleEngine
    from app.services.scoring_service import compute_composite_score, compute_risk_band
    from sqlalchemy import select

    async with AsyncSessionLocal() as session:
        # 1. Load vendor
        vendor = await session.get(Vendor, vendor_id)
        if vendor is None:
            logger.warning("rescore_vendor: vendor %s not found", vendor_id)
            return

        # 2. Load recent signals (last 7 days)
        since = datetime.now(timezone.utc) - timedelta(days=7)
        result = await session.execute(
            select(Signal)
            .where(Signal.vendor_id == vendor_id)
            .where(Signal.created_at >= since)
            .order_by(Signal.created_at.desc())
            .limit(50)
        )
        signals = result.scalars().all()
        signal_dicts = [
            {
                "parsed_dimension": s.parsed_dimension,
                "parsed_severity": s.parsed_severity,
                "signal_type": s.signal_type,
                "summary": s.summary,
                "days_ago": (datetime.now(timezone.utc) - s.created_at).days
                if s.created_at else 0,
            }
            for s in signals
        ]

        vendor_data = {
            "id": str(vendor.id),
            "tier": vendor.tier,
            "composite_score": vendor.composite_score,
            "cert_in_clock_active": vendor.cert_in_clock_active,
            **{
                dim: getattr(vendor, dim, 50)
                for dim in [
                    "cybersecurity", "regulatory", "operational", "newsLegal",
                    "financialHealth", "dataPrivacy", "concentration", "esg", "fourthParty",
                ]
            },
        }

        # 3. Build features and ML-score each dimension
        all_features = build_all_features(vendor_data, signal_dicts, history=[])
        dim_scores = score_all_dimensions(all_features)

        # 4. Detect compound risks and apply multipliers
        active_signal_types = [s.get("signal_type", "") for s in signal_dicts]
        compound_risks = detect_compound_risks(active_signal_types)
        for risk in compound_risks:
            for dim in dim_scores:
                dim_scores[dim] = max(0, int(dim_scores[dim] * risk.multiplier))

        # 5. Compute composite score
        new_composite = compute_composite_score(**dim_scores)
        new_band = compute_risk_band(new_composite)
        old_composite = vendor.composite_score or 50
        old_band = vendor.risk_band or "stable"

        # 6. Run rule engine
        rule_engine = RuleEngine()
        rule_results = rule_engine.run_all(
            vendor_data={**vendor_data, "composite_score": new_composite, **dim_scores},
            signals=signal_dicts,
        )

        cert_in_active = any(r.action == "ACTIVATE_CERT_IN_CLOCK" for r in rule_results)

        # 7. Update vendor
        for dim, score in dim_scores.items():
            if hasattr(vendor, dim):
                setattr(vendor, dim, score)
        vendor.previous_score = old_composite
        vendor.composite_score = new_composite
        vendor.risk_band = new_band
        if cert_in_active and not vendor.cert_in_clock_active:
            vendor.cert_in_clock_active = True
            vendor.cert_in_clock_started = datetime.now(timezone.utc)
        vendor.updated_at = datetime.now(timezone.utc)

        # 8. Write audit log
        audit = ScoreAuditLog(
            vendor_id=vendor_id,
            composite_score=new_composite,
            risk_band=new_band,
            dimension_scores=dim_scores,
            rule_results=[
                {"action": r.action, "citation": r.citation, "rationale": r.rationale}
                for r in rule_results
            ],
            scored_at=datetime.now(timezone.utc),
        )
        session.add(audit)
        await session.commit()

    # 9. Trigger alert if band changed
    if old_band != new_band:
        from app.workers.alert_tasks import process_score_change
        process_score_change.delay(vendor_id, old_composite, new_composite)

    logger.info(
        "Rescored vendor %s: %d→%d (%s→%s)",
        vendor_id, old_composite, new_composite, old_band, new_band,
    )


@celery_app.task(name="tasks.rescore_all_vendors")
def rescore_all_vendors():
    """Scheduled every 6 hours. Rescores all active vendors."""
    _run_async(_rescore_all_async())


async def _rescore_all_async() -> None:
    from app.core.database import AsyncSessionLocal
    from app.models.vendor import Vendor
    from sqlalchemy import select

    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Vendor.id))
        vendor_ids = [str(row[0]) for row in result.fetchall()]

    logger.info("Scheduling rescore for %d vendors", len(vendor_ids))
    for vid in vendor_ids:
        rescore_vendor.delay(vid)


@celery_app.task(name="tasks.take_risk_trend_snapshot")
def take_risk_trend_snapshot():
    """Scheduled daily at midnight IST. Captures aggregate risk posture."""
    _run_async(_snapshot_async())


async def _snapshot_async() -> None:
    from app.core.database import AsyncSessionLocal
    from app.models.vendor import Vendor
    from app.models.risk_trend import RiskTrendSnapshot
    from sqlalchemy import select

    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Vendor))
        vendors = result.scalars().all()

        if not vendors:
            return

        scores = [v.composite_score or 50 for v in vendors]
        avg_score = sum(scores) / len(scores)

        band_counts: dict[str, int] = {"critical": 0, "high": 0, "watch": 0, "stable": 0}
        for v in vendors:
            band = v.risk_band or "stable"
            band_counts[band] = band_counts.get(band, 0) + 1

        snapshot = RiskTrendSnapshot(
            average_composite_score=round(avg_score, 1),
            critical_count=band_counts["critical"],
            high_count=band_counts["high"],
            watch_count=band_counts["watch"],
            stable_count=band_counts["stable"],
            total_vendors=len(vendors),
            snapshot_date=datetime.now(timezone.utc).date(),
        )
        session.add(snapshot)
        await session.commit()

    logger.info("Risk trend snapshot: avg=%.1f vendors=%d", avg_score, len(vendors))
