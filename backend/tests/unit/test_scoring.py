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
    # Weighted average should be in a reasonable range
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


def test_composite_score_all_stable():
    score = compute_composite_score(
        cybersecurity=90,
        regulatory=90,
        operational=90,
        news_legal=90,
        financial_health=90,
        data_privacy=90,
        concentration=90,
        esg=90,
        fourth_party=90,
    )
    assert score >= 75
    assert compute_risk_band(score) == "stable"


def test_composite_score_all_critical():
    score = compute_composite_score(
        cybersecurity=10,
        regulatory=10,
        operational=10,
        news_legal=10,
        financial_health=10,
        data_privacy=10,
        concentration=10,
        esg=10,
        fourth_party=10,
    )
    assert score <= 24
    assert compute_risk_band(score) == "critical"
