"""SEBI LODR / MCA21 filing anomaly rules."""
from app.engine.rules.base_rule import BaseRule, RuleResult


class SEBIMCAFilingAnomalyRule(BaseRule):
    name = "sebi_mca_filing_anomaly"
    citation = "SEBI LODR Regulations 2015, Regulation 33 (Financial Results)"
    version = "1.0.0"

    def evaluate(self, vendor_data: dict, signals: list[dict]) -> RuleResult:
        has_mca_anomaly = any(
            s.get("signal_type") == "MCA_ANOMALY"
            or (s.get("parsed_dimension") == "financialHealth" and s.get("parsed_severity", 0) >= 7)
            for s in signals
        )
        financial_score = vendor_data.get("financialHealth", 100)

        if has_mca_anomaly and financial_score < 50:
            return RuleResult(
                triggered=True,
                action="FLAG_FINANCIAL_ANOMALY",
                rationale=(
                    f"MCA21 filing anomaly detected with financial health score {financial_score}. "
                    "Regulatory filing non-compliance may indicate financial distress. "
                    "Enhanced due diligence required under SEBI LODR."
                ),
                citation=self.citation,
            )
        return RuleResult(triggered=False)


class MCA21OverdueFilingRule(BaseRule):
    name = "mca21_overdue_filing"
    citation = "Companies Act 2013, Section 129 (Financial Statements)"
    version = "1.0.0"

    def evaluate(self, vendor_data: dict, signals: list[dict]) -> RuleResult:
        has_overdue = any(
            s.get("signal_type") == "MCA_ANOMALY"
            and "overdue" in (s.get("summary") or "").lower()
            for s in signals
        )
        if has_overdue:
            return RuleResult(
                triggered=True,
                action="REQUEST_FINANCIAL_STATEMENTS",
                rationale=(
                    "Vendor has overdue MCA21 financial filings. "
                    "Bank must obtain audited statements for continued outsourcing approval."
                ),
                citation=self.citation,
            )
        return RuleResult(triggered=False)
