"""
CLI training script for per-dimension XGBoost/GradientBoosting models.

Usage:
    python -m app.engine.ml.training.train_dimension --dimension cybersecurity
    python -m app.engine.ml.training.train_dimension --all
"""
from __future__ import annotations

import argparse
import logging
import sys

import numpy as np  # type: ignore[import]

logger = logging.getLogger(__name__)

DIMENSIONS = [
    "cybersecurity", "regulatory", "operational", "newsLegal",
    "financialHealth", "dataPrivacy", "concentration", "esg", "fourthParty",
]

FEATURE_NAMES = [
    "max_severity", "avg_severity", "signal_count", "recency",
    "signal_diversity", "cert_in_active", "tier_weight",
]


def generate_synthetic_data(
    n_samples: int = 500,
    seed: int = 42,
) -> tuple[np.ndarray, np.ndarray]:
    """
    Generate synthetic training data until real historical data is available.

    Features are in [0, 1]. Labels are 0-100 scores (higher = safer).
    The label is an inverse-weighted sum of features with noise.
    """
    rng = np.random.default_rng(seed)
    X = rng.uniform(0, 1, size=(n_samples, len(FEATURE_NAMES)))

    # Higher severity/recency/cert_in → lower (worse) score
    weights = np.array([0.35, 0.20, 0.15, 0.10, 0.05, 0.10, 0.05])
    risk = X @ weights  # 0 to 1
    noise = rng.normal(0, 0.05, n_samples)
    y = np.clip((1 - risk) * 100 + noise * 10, 0, 100)
    return X, y


def train(dimension: str) -> None:
    from sklearn.ensemble import GradientBoostingRegressor  # type: ignore[import]
    from sklearn.model_selection import train_test_split  # type: ignore[import]
    from sklearn.metrics import mean_absolute_error  # type: ignore[import]
    from app.engine.ml.model_registry import save_model

    logger.info("Training model for dimension: %s", dimension)
    X, y = generate_synthetic_data()
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = GradientBoostingRegressor(
        n_estimators=100,
        max_depth=4,
        learning_rate=0.1,
        random_state=42,
    )
    model.fit(X_train, y_train)
    preds = model.predict(X_test)
    mae = mean_absolute_error(y_test, preds)
    logger.info("  MAE on test set: %.2f", mae)

    save_model(
        dimension,
        model,
        metadata={
            "trained_features": FEATURE_NAMES,
            "n_samples": len(X),
            "test_mae": round(mae, 2),
            "note": "synthetic-data — replace with real historical signals",
        },
    )
    print(f"[OK] {dimension}: MAE={mae:.2f}")


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    parser = argparse.ArgumentParser(description="Train risk scoring models")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--dimension", choices=DIMENSIONS, help="Dimension to train")
    group.add_argument("--all", action="store_true", help="Train all dimensions")
    args = parser.parse_args()

    targets = DIMENSIONS if args.all else [args.dimension]
    for dim in targets:
        try:
            train(dim)
        except ImportError:
            print("ERROR: Install scikit-learn: pip install scikit-learn", file=sys.stderr)
            sys.exit(1)


if __name__ == "__main__":
    main()
