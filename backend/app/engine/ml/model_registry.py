"""
Model registry: load/save trained ML models per dimension.

Local models are stored in backend/models/<dimension>.pkl.
If AWS is configured, falls back to S3 bucket thirdeye-models.
"""
from __future__ import annotations

import logging
import os
import pickle
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger(__name__)

# Local model storage relative to this file's package root
_MODELS_DIR = Path(__file__).parent.parent.parent.parent / "models"

# In-memory cache to avoid repeated disk reads
_model_cache: dict[str, Any] = {}


def _model_path(dimension: str) -> Path:
    return _MODELS_DIR / f"{dimension}.pkl"


def save_model(dimension: str, model: Any, metadata: dict | None = None) -> None:
    """Persist a trained model to disk."""
    _MODELS_DIR.mkdir(parents=True, exist_ok=True)
    payload = {"model": model, "metadata": metadata or {}}
    with open(_model_path(dimension), "wb") as f:
        pickle.dump(payload, f)
    _model_cache[dimension] = model
    logger.info("Saved model for dimension '%s'", dimension)


def load_model(dimension: str) -> Optional[Any]:
    """
    Load model for a dimension.

    Order: memory cache → local disk → S3 (if AWS configured).
    Returns None if no model is available (caller falls back to heuristic).
    """
    if dimension in _model_cache:
        return _model_cache[dimension]

    local = _model_path(dimension)
    if local.exists():
        try:
            with open(local, "rb") as f:
                payload = pickle.load(f)
            model = payload.get("model") if isinstance(payload, dict) else payload
            _model_cache[dimension] = model
            logger.info("Loaded local model for dimension '%s'", dimension)
            return model
        except Exception as exc:
            logger.warning("Failed to load local model for '%s': %s", dimension, exc)

    # Try S3 if configured
    return _try_load_from_s3(dimension)


def _try_load_from_s3(dimension: str) -> Optional[Any]:
    bucket = os.getenv("S3_BUCKET_MODELS", "")
    if not bucket:
        return None
    try:
        import boto3  # type: ignore[import]
        s3 = boto3.client("s3", region_name=os.getenv("AWS_REGION", "ap-south-1"))
        key = f"models/{dimension}.pkl"
        obj = s3.get_object(Bucket=bucket, Key=key)
        payload = pickle.loads(obj["Body"].read())
        model = payload.get("model") if isinstance(payload, dict) else payload
        _model_cache[dimension] = model
        # Also save locally for next time
        save_model(dimension, model)
        logger.info("Loaded model for '%s' from S3", dimension)
        return model
    except Exception as exc:
        logger.debug("S3 model load failed for '%s': %s", dimension, exc)
        return None


def clear_cache() -> None:
    """Clear in-memory model cache (useful in tests)."""
    _model_cache.clear()
