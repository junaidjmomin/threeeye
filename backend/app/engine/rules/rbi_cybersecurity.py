"""RBI Cybersecurity Framework 2016 rules."""
from app.engine.rules.base_rule import BaseRule, RuleResult


class RBICybersecurityFrameworkRule(BaseRule):
    name = "rbi_cybersecurity_framework"
    citation = "RBI Cybersecurity Framework 2016, Section 4 (Baseline Cyber Security)"
    version = "1.0.0"

    def evaluate(self, vendor_data: dict, signals: list[dict]) -> RuleResult:
        cyber_score = vendor_data.get("cybersecurity", vendor_data.get("composite_score", 100))

        if cyber_score < 40:
            return RuleResult(
                triggered=True,
                action="ESCALATE_CYBERSECURITY",
                rationale=(
                    f"Vendor cybersecurity score {cyber_score} is below the 40-point threshold "
                    "mandated by RBI Cybersecurity Framework baseline controls. "
                    "Immediate CISO notification required."
                ),
                citation=self.citation,
            )
        return RuleResult(triggered=False)


class RBICriticalSystemsRule(BaseRule):
    name = "rbi_critical_systems_protection"
    citation = "RBI Cybersecurity Framework 2016, Section 6 (Critical Systems)"
    version = "1.0.0"

    def evaluate(self, vendor_data: dict, signals: list[dict]) -> RuleResult:
        tier = vendor_data.get("tier", "standard")
        cyber_score = vendor_data.get("cybersecurity", 100)
        has_critical_signal = any(
            s.get("signal_type") in ("CRITICAL_BREACH", "CERT_IN_ADVISORY")
            for s in signals
        )

        if tier in ("material", "significant") and cyber_score < 50 and has_critical_signal:
            return RuleResult(
                triggered=True,
                action="INITIATE_INCIDENT_RESPONSE",
                rationale=(
                    f"Critical/significant tier vendor with cyber score {cyber_score} "
                    "has active breach or CERT-In advisory. "
                    "Incident response protocol mandated."
                ),
                citation=self.citation,
            )
        return RuleResult(triggered=False)
