"""Tests for compound risk correlation engine."""
from app.engine.ml.correlation_engine import detect_compound_risks


def test_breach_probability_detection():
    risks = detect_compound_risks(["negative_news", "open_ports", "sla_degradation"])
    assert len(risks) == 1
    assert risks[0].pattern_name == "breach_probability"
    assert risks[0].multiplier == 0.6


def test_partial_match_breach():
    risks = detect_compound_risks(["negative_news", "open_ports"])
    assert len(risks) == 1
    assert risks[0].pattern_name == "breach_probability"


def test_no_match():
    risks = detect_compound_risks(["open_ports"])
    assert len(risks) == 0


def test_multiple_patterns():
    risks = detect_compound_risks([
        "negative_news",
        "open_ports",
        "rbi_enforcement",
        "dpdp_violation",
    ])
    assert len(risks) == 2
    names = {r.pattern_name for r in risks}
    assert "breach_probability" in names
    assert "regulatory_cascade" in names


def test_financial_collapse_pattern():
    risks = detect_compound_risks(["mca_filing_anomaly", "credit_downgrade"])
    assert any(r.pattern_name == "financial_collapse" for r in risks)


def test_empty_signals():
    risks = detect_compound_risks([])
    assert risks == []
