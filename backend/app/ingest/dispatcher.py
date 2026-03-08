"""
Signal dispatcher — routes normalized signals to Celery processing tasks.
"""
from __future__ import annotations

import logging

from app.ingest.normalizer import NormalizedSignal

logger = logging.getLogger(__name__)


def dispatch(signal: NormalizedSignal) -> None:
    """
    Enqueue a normalized signal for async processing.

    Imports Celery task lazily to avoid circular imports at module load time.
    """
    try:
        from app.workers.alert_tasks import process_signal  # noqa: PLC0415
        process_signal.delay(signal.model_dump(mode="json"))
        logger.debug("Dispatched signal from source=%s vendor=%s", signal.source, signal.vendor_hint)
    except Exception as exc:
        logger.error("Failed to dispatch signal: %s", exc)


def dispatch_batch(signals: list[NormalizedSignal]) -> int:
    """
    Dispatch a batch of signals. Returns count of successfully dispatched.
    """
    dispatched = 0
    for signal in signals:
        try:
            dispatch(signal)
            dispatched += 1
        except Exception as exc:
            logger.error("Dispatch error for signal from %s: %s", signal.source, exc)
    return dispatched
