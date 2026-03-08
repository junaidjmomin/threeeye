"""Tests for RuleEngine orchestrator — auto-discovers and runs all rules."""
from app.engine.rules.base_rule import BaseRule
from app.engine.rules.engine import RuleEngine


def test_rule_engine_discovers_rules():
    engine = RuleEngine()
    assert len(engine.rules) > 0


def test_rule_engine_all_rules_have_citations():
    engine = RuleEngine()
    for rule in engine.rules:
        assert rule.citation, f"Rule '{rule.name}' missing citation — audit risk!"


def test_rule_engine_run_all_returns_triggered_only():
    engine = RuleEngine()
    # Vendor data that should trigger CERT-In clock and RBI cybersecurity
    triggered = engine.run_all(
        vendor_data={"composite_score": 20, "tier": "material", "cybersecurity": 15},
        signals=[{"parsed_dimension": "cybersecurity", "parsed_severity": 9}],
    )
    assert len(triggered) >= 1
    for result in triggered:
        assert result.triggered
        assert result.citation  # every triggered result must have citation


def test_rule_engine_stable_vendor_no_triggers():
    engine = RuleEngine()
    triggered = engine.run_all(
        vendor_data={"composite_score": 90, "tier": "standard", "cybersecurity": 90},
        signals=[],
    )
    # A stable vendor with no signals should produce minimal or zero triggered rules
    critical_actions = [r for r in triggered if "CERT_IN" in r.action or "ESCALATE" in r.action]
    assert len(critical_actions) == 0


def test_rule_engine_run_for_action_filters():
    engine = RuleEngine()
    results = engine.run_for_action(
        vendor_data={"composite_score": 10, "tier": "material"},
        signals=[{"parsed_dimension": "cybersecurity", "parsed_severity": 9}],
        action="ACTIVATE_CERT_IN_CLOCK",
    )
    for r in results:
        assert r.action == "ACTIVATE_CERT_IN_CLOCK"


def test_rule_engine_error_in_rule_does_not_crash():
    """Engine should handle a broken rule gracefully."""
    class BrokenRule(BaseRule):
        name = "broken_rule"
        citation = "Test citation"
        version = "1.0.0"

        def evaluate(self, vendor_data, signals):
            raise ValueError("Simulated rule error")

    engine = RuleEngine(rules=[BrokenRule()])
    # Should not raise
    results = engine.run_all({"composite_score": 50}, [])
    assert results == []
