"""Tests for DPDP Act breach notification rules."""
from app.engine.rules.dpdp import DPDPBreachNotificationRule


def test_dpdp_breach_triggers_on_high_severity_data_privacy():
    rule = DPDPBreachNotificationRule()
    result = rule.evaluate(
        vendor_data={},
        signals=[{"parsed_dimension": "dataPrivacy", "parsed_severity": 8}],
    )
    assert result.triggered
    assert result.action == "INITIATE_DPDP_NOTIFICATION"
    assert "DPDP" in result.citation


def test_dpdp_no_trigger_on_low_severity():
    rule = DPDPBreachNotificationRule()
    result = rule.evaluate(
        vendor_data={},
        signals=[{"parsed_dimension": "dataPrivacy", "parsed_severity": 5}],
    )
    assert not result.triggered


def test_dpdp_no_trigger_wrong_dimension():
    rule = DPDPBreachNotificationRule()
    result = rule.evaluate(
        vendor_data={},
        signals=[{"parsed_dimension": "cybersecurity", "parsed_severity": 9}],
    )
    assert not result.triggered


def test_dpdp_rule_has_citation():
    rule = DPDPBreachNotificationRule()
    assert rule.citation
    assert "DPDP" in rule.citation
    assert rule.version
