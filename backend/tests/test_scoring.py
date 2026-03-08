"""Tests for scoring service and risk band calculation."""
from app.services.scoring_service import compute_composite_score, compute_risk_band


def test_composite_score_calculation():
    score = compute_composite_score(
        cybersecurity=28,
        regulatory=61,
        operational=70,
        news_legal=55,
        financial_health=80,
        data_privacy=72,
        concentration=65,
        esg=58,
        fourth_party=45,
    )
    # Weighted average should be around 54
    assert 40 <= score <= 70


def test_risk_band_critical():
    assert compute_risk_band(0) == "critical"
    assert compute_risk_band(24) == "critical"


def test_risk_band_high():
    assert compute_risk_band(25) == "high"
    assert compute_risk_band(49) == "high"


def test_risk_band_watch():
    assert compute_risk_band(50) == "watch"
    assert compute_risk_band(74) == "watch"


def test_risk_band_stable():
    assert compute_risk_band(75) == "stable"
    assert compute_risk_band(100) == "stable"
