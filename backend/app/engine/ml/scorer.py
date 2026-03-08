"""
Dimension scorer: feature vector → 0-100 risk score per dimension.

Uses a trained sklearn GradientBoostingRegressor if available.
Falls back to a deterministic weighted heuristic when no model is loaded.
"""
from __future__ import annotations

import logging
from typing import Any

from app.engine.ml.model_registry import load_model

logger = logging.getLogger(__name__)

# Heuristic weights when no ML model is available.
# Higher weight = more impact on the final heuristic score.
_HEURISTIC_WEIGHTS = {
    "max_severity": 0.35,
    "avg_severity": 0.20,
    "signal_count": 0.15,
    "recency": 0.10,
    "signal_diversity": 0.05,
    "cert_in_active": 0.10,
    "tier_weight": 0.05,
}


def _heuristic_score(features: dict[str, float], current_score: float) -> int:
    """
    Weighted heuristic: higher weighted sum → lower (worse) score.
    current_score provides an anchor — signals push it up or down.
    Returns 0-100.
    """
    risk_weight = sum(
        _HEURISTIC_WEIGHTS.get(k, 0) * features.get(k, 0.0)
        for k in _HEURISTIC_WEIGHTS
    )
    # risk_weight 0 → 1 means no risk → max risk
    # We invert: score = current anchored, pulled down by risk
    raw = current_score * (1.0 - 0.6 * risk_weight)
    return max(0, min(100, int(raw)))


def score_dimension(
    features: dict[str, float],
    dimension: str,
) -> int:
    """
    Score a single risk dimension from its feature vector.

    Returns an integer in [0, 100] where 0 = maximum risk, 100 = no risk.
    """
    current_score = features.get("current_score", 0.5) * 100.0

    model = load_model(dimension)
    if model is not None:
        try:
            import numpy as np  # type: ignore[import]
            feature_order = list(_HEURISTIC_WEIGHTS.keys())
            X = np.array([[features.get(k, 0.0) for k in feature_order]])
            raw = float(model.predict(X)[0])
            return max(0, min(100, int(raw)))
        except Exception as exc:
            logger.warning("ML scoring failed for '%s', using heuristic: %s", dimension, exc)

    return _heuristic_score(features, current_score)


def score_all_dimensions(
    all_features: dict[str, dict[str, float]],
) -> dict[str, int]:
    """Score all 9 dimensions. Returns {dimension: score}."""
    return {dim: score_dimension(features, dim) for dim, features in all_features.items()}


def train_model_for_dimension(
    dimension: str,
    X_train: Any,
    y_train: Any,
) -> Any:
    """
    Train a GradientBoostingRegressor for the given dimension.
    Saves to model registry. Returns the trained model.
    """
    from sklearn.ensemble import GradientBoostingRegressor  # type: ignore[import]
    from app.engine.ml.model_registry import save_model

    model = GradientBoostingRegressor(
        n_estimators=100,
        max_depth=4,
        learning_rate=0.1,
        random_state=42,
    )
    model.fit(X_train, y_train)
    save_model(dimension, model, metadata={"trained_features": list(_HEURISTIC_WEIGHTS.keys())})
    return model
