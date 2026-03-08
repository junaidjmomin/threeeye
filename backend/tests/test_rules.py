"""Tests for Policy-as-Code rule engine."""
from app.engine.rules.cert_in import CertInClockRule
from app.engine.rules.rbi_outsourcing import MaterialOutsourcingClassificationRule
from app.engine.rules.dpdp import DPDPBreachNotificationRule


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


def test_rbi_material_outsourcing_triggers():
    rule = MaterialOutsourcingClassificationRule()
    result = rule.evaluate(
        vendor_data={"tier": "material", "composite_score": 30},
        signals=[],
    )
    assert result.triggered
    assert result.action == "ESCALATE_TO_BOARD"
    assert "RBI" in result.citation


def test_rbi_material_outsourcing_safe():
    rule = MaterialOutsourcingClassificationRule()
    result = rule.evaluate(
        vendor_data={"tier": "material", "composite_score": 75},
        signals=[],
    )
    assert not result.triggered


def test_dpdp_breach_notification_triggers():
    rule = DPDPBreachNotificationRule()
    result = rule.evaluate(
        vendor_data={},
        signals=[{"parsed_dimension": "dataPrivacy", "parsed_severity": 8}],
    )
    assert result.triggered
    assert result.action == "INITIATE_DPDP_NOTIFICATION"
    assert "DPDP" in result.citation


def test_all_rules_have_citations():
    """Every rule must carry a regulatory citation for audit defensibility."""
    rules = [CertInClockRule(), MaterialOutsourcingClassificationRule(), DPDPBreachNotificationRule()]
    for rule in rules:
        assert rule.citation, f"Rule {rule.name} is missing a regulatory citation"
        assert rule.version, f"Rule {rule.name} is missing a version"
