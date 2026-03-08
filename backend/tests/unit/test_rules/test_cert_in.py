"""Tests for CERT-In clock activation rules."""
from app.engine.rules.cert_in import CertInClockRule, CertInReportingRule


def test_cert_in_clock_triggers_on_critical_cyber():
    rule = CertInClockRule()
    result = rule.evaluate(
        vendor_data={"composite_score": 20},
        signals=[{"parsed_dimension": "cybersecurity", "parsed_severity": 9}],
    )
    assert result.triggered
    assert result.action == "ACTIVATE_CERT_IN_CLOCK"
    assert "CERT-In" in result.citation


def test_cert_in_clock_does_not_trigger_above_threshold():
    rule = CertInClockRule()
    result = rule.evaluate(
        vendor_data={"composite_score": 50},
        signals=[{"parsed_dimension": "cybersecurity", "parsed_severity": 9}],
    )
    assert not result.triggered


def test_cert_in_clock_requires_cyber_incident():
    """Score alone (without cyber incident) should NOT trigger clock."""
    rule = CertInClockRule()
    result = rule.evaluate(
        vendor_data={"composite_score": 10},
        signals=[{"parsed_dimension": "regulatory", "parsed_severity": 9}],
    )
    assert not result.triggered


def test_cert_in_reporting_triggers_on_breach():
    rule = CertInReportingRule()
    result = rule.evaluate(
        vendor_data={},
        signals=[{"signal_type": "CRITICAL_BREACH"}],
    )
    assert result.triggered
    assert result.action == "PREPARE_CERT_IN_REPORT"
    assert "CERT-In" in result.citation


def test_cert_in_rule_has_citation():
    rule = CertInClockRule()
    assert rule.citation
    assert rule.version
