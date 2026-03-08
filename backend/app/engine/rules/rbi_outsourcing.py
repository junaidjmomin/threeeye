"""RBI IT Outsourcing Directions 2023 rules."""
from app.engine.rules.base_rule import BaseRule, RuleResult


class MaterialOutsourcingClassificationRule(BaseRule):
    name = "rbi_material_outsourcing"
    citation = "RBI Master Direction on IT Outsourcing 2023, Section 6.1"
    version = "1.0.0"

    def evaluate(self, vendor_data: dict, signals: list[dict]) -> RuleResult:
        tier = vendor_data.get("tier", "standard")
        composite = vendor_data.get("composite_score", 100)

        if tier == "material" and composite < 50:
            return RuleResult(
                triggered=True,
                action="ESCALATE_TO_BOARD",
                rationale=(
                    f"Material outsourcing vendor score {composite} below threshold. "
                    "Board-level oversight required per RBI Directions."
                ),
                citation=self.citation,
            )
        return RuleResult(triggered=False)


class RightToAuditRule(BaseRule):
    name = "rbi_right_to_audit"
    citation = "RBI Master Direction on IT Outsourcing 2023, Section 8.3"
    version = "1.0.0"

    def evaluate(self, vendor_data: dict, signals: list[dict]) -> RuleResult:
        # Phase 2: Check contract metadata for audit clause
        return RuleResult(triggered=False)
