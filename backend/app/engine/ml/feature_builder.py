"""
Feature builder: vendor data + recent signals + history → feature vector per dimension.
"""
from __future__ import annotations

from collections import Counter
from typing import Any

DIMENSIONS = [
    "cybersecurity", "regulatory", "operational", "newsLegal",
    "financialHealth", "dataPrivacy", "concentration", "esg", "fourthParty",
]

# Map signal_type → most relevant dimension
SIGNAL_TYPE_DIMENSION_MAP = {
    "CRITICAL_BREACH": "cybersecurity",
    "DATA_LEAK": "dataPrivacy",
    "REGULATORY_ACTION": "regulatory",
    "OPERATIONAL_FAILURE": "operational",
    "FINANCIAL_DISTRESS": "financialHealth",
    "NEGATIVE_NEWS": "newsLegal",
    "CERT_IN_ADVISORY": "cybersecurity",
    "MCA_ANOMALY": "financialHealth",
    "FOURTH_PARTY_RISK": "fourthParty",
}


def build_features(
    vendor_data: dict[str, Any],
    recent_signals: list[dict[str, Any]],
    history: list[dict[str, Any]],
    dimension: str,
) -> dict[str, float]:
    """
    Build a feature vector for a single dimension.

    Features are numeric values in [0, 1] or small integers.
    Returns a flat dict — keys must be stable across all vendors.
    """
    # --- Signal-derived features ---
    dim_signals = [
        s for s in recent_signals
        if s.get("parsed_dimension") == dimension
        or SIGNAL_TYPE_DIMENSION_MAP.get(s.get("signal_type", "")) == dimension
    ]
    all_severities = [s.get("parsed_severity", 5) for s in dim_signals]
    max_severity = max(all_severities) / 10.0 if all_severities else 0.0
    avg_severity = (sum(all_severities) / len(all_severities) / 10.0) if all_severities else 0.0
    signal_count = min(len(dim_signals), 20) / 20.0  # normalised 0-1

    # --- Vendor baseline score (normalised) ---
    current_dim_score = vendor_data.get(dimension, vendor_data.get("composite_score", 50))
    normalized_score = float(current_dim_score) / 100.0

    # --- Trend: score direction from history ---
    trend = 0.0
    if len(history) >= 2:
        recent_h = history[-1].get(dimension, history[-1].get("composite_score", 50))
        older_h = history[-2].get(dimension, history[-2].get("composite_score", 50))
        trend = (recent_h - older_h) / 100.0  # -1 to +1

    # --- Vendor tier risk weight ---
    tier_map = {"material": 1.0, "significant": 0.6, "standard": 0.3}
    tier_weight = tier_map.get(vendor_data.get("tier", "standard"), 0.3)

    # --- CERT-In active flag ---
    cert_in_active = 1.0 if vendor_data.get("cert_in_clock_active", False) else 0.0

    # --- Days since last incident in this dimension ---
    days_since_incident = 365  # default: no incident
    for s in dim_signals:
        days = s.get("days_ago", 365)
        days_since_incident = min(days_since_incident, days)
    recency = max(0.0, 1.0 - days_since_incident / 365.0)

    # --- Signal type diversity ---
    sig_types = Counter(s.get("signal_type", "UNKNOWN") for s in dim_signals)
    diversity = min(len(sig_types), 5) / 5.0

    return {
        "current_score": normalized_score,
        "max_severity": max_severity,
        "avg_severity": avg_severity,
        "signal_count": signal_count,
        "signal_diversity": diversity,
        "trend": trend,
        "tier_weight": tier_weight,
        "cert_in_active": cert_in_active,
        "recency": recency,
    }


def build_all_features(
    vendor_data: dict[str, Any],
    recent_signals: list[dict[str, Any]],
    history: list[dict[str, Any]],
) -> dict[str, dict[str, float]]:
    """Build features for all 9 dimensions at once."""
    return {
        dim: build_features(vendor_data, recent_signals, history, dim)
        for dim in DIMENSIONS
    }
