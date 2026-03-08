"""CERT-In 6-hour clock activation rule."""
from app.engine.rules.base_rule import BaseRule, RuleResult


class CertInClockRule(BaseRule):
    name = "cert_in_6hr_clock"
    citation = "CERT-In Directions 2022, Section 4(ii)"
    version = "1.0.0"

    def evaluate(self, vendor_data: dict, signals: list[dict]) -> RuleResult:
        composite = vendor_data.get("composite_score", 100)
        has_cyber_incident = any(
            s.get("parsed_dimension") == "cybersecurity" and (s.get("parsed_severity") or 0) >= 8
            for s in signals
        )

        if composite <= 24 and has_cyber_incident:
            return RuleResult(
                triggered=True,
                action="ACTIVATE_CERT_IN_CLOCK",
                rationale=(
                    f"Composite score {composite} below critical threshold (24) "
                    "with confirmed cyber incident detected"
                ),
                citation=self.citation,
            )
        return RuleResult(triggered=False)


class CertInReportingRule(BaseRule):
    name = "cert_in_reporting_obligation"
    citation = "CERT-In Directions 2022, Section 4(i)"
    version = "1.0.0"

    def evaluate(self, vendor_data: dict, signals: list[dict]) -> RuleResult:
        # Check if any signal is a confirmed breach
        has_breach = any(
            s.get("signal_type") in ("CRITICAL_BREACH", "DATA_LEAK")
            for s in signals
        )
        if has_breach:
            return RuleResult(
                triggered=True,
                action="PREPARE_CERT_IN_REPORT",
                rationale="Confirmed breach signal requires CERT-In incident report within 6 hours",
                citation=self.citation,
            )
        return RuleResult(triggered=False)
