"""
Integration test: critical cyber event → CERT-In clock activation.
Verifies the full rule engine path including citation requirement.
"""
from app.engine.rules.engine import RuleEngine


def test_critical_cyber_incident_activates_cert_in_clock():
    """
    Full rule engine path:
    composite_score <= 24 + cybersecurity signal severity >= 8
    → ACTIVATE_CERT_IN_CLOCK triggered with valid CERT-In citation
    """
    engine = RuleEngine()

    vendor_data = {
        "composite_score": 18,
        "cybersecurity": 15,
        "tier": "material",
    }
    signals = [
        {
            "parsed_dimension": "cybersecurity",
            "parsed_severity": 9,
            "signal_type": "CRITICAL_BREACH",
            "summary": "Ransomware attack detected on vendor infrastructure",
        }
    ]

    results = engine.run_all(vendor_data, signals)
    cert_in_results = [r for r in results if r.action == "ACTIVATE_CERT_IN_CLOCK"]

    assert len(cert_in_results) >= 1, "CERT-In clock should be activated for critical + cyber breach"

    result = cert_in_results[0]
    assert result.triggered
    assert result.citation
    assert "CERT-In" in result.citation
    assert "2022" in result.citation or "Section" in result.citation  # must be specific


def test_non_critical_score_does_not_activate_cert_in():
    engine = RuleEngine()

    vendor_data = {"composite_score": 60, "tier": "material", "cybersecurity": 55}
    signals = [{"parsed_dimension": "cybersecurity", "parsed_severity": 9, "signal_type": "CRITICAL_BREACH"}]

    results = engine.run_all(vendor_data, signals)
    cert_in_results = [r for r in results if r.action == "ACTIVATE_CERT_IN_CLOCK"]
    assert len(cert_in_results) == 0


def test_audit_trail_every_rule_has_citation():
    """
    REGULATORY REQUIREMENT: Every triggered rule result must carry a citation.
    This is non-negotiable for RBI audit defensibility.
    """
    engine = RuleEngine()
    vendor_data = {
        "composite_score": 15,
        "cybersecurity": 10,
        "tier": "material",
        "financialHealth": 20,
    }
    signals = [
        {"parsed_dimension": "cybersecurity", "parsed_severity": 9, "signal_type": "CRITICAL_BREACH"},
        {"parsed_dimension": "dataPrivacy", "parsed_severity": 8, "signal_type": "DATA_LEAK"},
        {"signal_type": "MCA_ANOMALY", "summary": "overdue filing detected"},
    ]

    results = engine.run_all(vendor_data, signals)

    for result in results:
        assert result.citation, (
            f"Rule result '{result.action}' has no citation — "
            "this is a compliance violation and would fail RBI audit"
        )
