"""DPDP Act 2023 compliance rules."""
from app.engine.rules.base_rule import BaseRule, RuleResult


class DPDPBreachNotificationRule(BaseRule):
    name = "dpdp_breach_notification"
    citation = "DPDP (Digital Personal Data Protection) Act 2023, Section 8(6)"
    version = "1.0.0"

    def evaluate(self, vendor_data: dict, signals: list[dict]) -> RuleResult:
        has_data_breach = any(
            s.get("parsed_dimension") == "dataPrivacy" and (s.get("parsed_severity") or 0) >= 7
            for s in signals
        )

        if has_data_breach:
            return RuleResult(
                triggered=True,
                action="INITIATE_DPDP_NOTIFICATION",
                rationale=(
                    "Data privacy breach signal detected. "
                    "DPDP Act requires breach notification to Data Protection Board "
                    "and affected data principals."
                ),
                citation=self.citation,
            )
        return RuleResult(triggered=False)


class DPDPPenaltySurfaceRule(BaseRule):
    name = "dpdp_penalty_surface"
    citation = "DPDP (Digital Personal Data Protection) Act 2023, Section 33"
    version = "1.0.0"

    def evaluate(self, vendor_data: dict, signals: list[dict]) -> RuleResult:
        privacy_score = vendor_data.get("score_data_privacy", 100)
        if privacy_score < 40:
            return RuleResult(
                triggered=True,
                action="FLAG_DPDP_PENALTY_EXPOSURE",
                rationale=(
                    f"Data privacy score {privacy_score} indicates elevated penalty surface. "
                    "Potential exposure up to INR 200 crore per violation."
                ),
                citation=self.citation,
            )
        return RuleResult(triggered=False)
