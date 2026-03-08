"""Tests for RBI outsourcing and cybersecurity framework rules."""
from app.engine.rules.rbi_outsourcing import MaterialOutsourcingClassificationRule, RightToAuditRule
from app.engine.rules.rbi_cybersecurity import RBICybersecurityFrameworkRule, RBICriticalSystemsRule


def test_material_outsourcing_triggers_at_risk():
    rule = MaterialOutsourcingClassificationRule()
    result = rule.evaluate(
        vendor_data={"tier": "material", "composite_score": 30},
        signals=[],
    )
    assert result.triggered
    assert result.action == "ESCALATE_TO_BOARD"
    assert "RBI" in result.citation


def test_material_outsourcing_no_trigger_above_threshold():
    rule = MaterialOutsourcingClassificationRule()
    result = rule.evaluate(
        vendor_data={"tier": "material", "composite_score": 75},
        signals=[],
    )
    assert not result.triggered


def test_standard_tier_does_not_trigger_material_rule():
    rule = MaterialOutsourcingClassificationRule()
    result = rule.evaluate(
        vendor_data={"tier": "standard", "composite_score": 20},
        signals=[],
    )
    assert not result.triggered


def test_rbi_cybersecurity_triggers_below_40():
    rule = RBICybersecurityFrameworkRule()
    result = rule.evaluate(
        vendor_data={"cybersecurity": 35},
        signals=[],
    )
    assert result.triggered
    assert result.action == "ESCALATE_CYBERSECURITY"
    assert "RBI Cybersecurity Framework" in result.citation


def test_rbi_cybersecurity_no_trigger_above_40():
    rule = RBICybersecurityFrameworkRule()
    result = rule.evaluate(
        vendor_data={"cybersecurity": 55},
        signals=[],
    )
    assert not result.triggered


def test_rbi_critical_systems_triggers_with_breach():
    rule = RBICriticalSystemsRule()
    result = rule.evaluate(
        vendor_data={"tier": "material", "cybersecurity": 40},
        signals=[{"signal_type": "CRITICAL_BREACH"}],
    )
    assert result.triggered
    assert result.action == "INITIATE_INCIDENT_RESPONSE"


def test_all_rbi_rules_have_citations():
    rules = [
        MaterialOutsourcingClassificationRule(),
        RightToAuditRule(),
        RBICybersecurityFrameworkRule(),
        RBICriticalSystemsRule(),
    ]
    for rule in rules:
        assert rule.citation, f"Rule '{rule.name}' is missing a regulatory citation"
        assert rule.version, f"Rule '{rule.name}' is missing a version"
