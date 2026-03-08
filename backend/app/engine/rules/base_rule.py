"""Base class for all Policy-as-Code rules."""
from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class RuleResult:
    triggered: bool
    action: str = ""
    rationale: str = ""
    citation: str = ""


class BaseRule(ABC):
    name: str = ""
    citation: str = ""
    version: str = "1.0.0"

    @abstractmethod
    def evaluate(self, vendor_data: dict, signals: list[dict]) -> RuleResult:
        """Evaluate this rule against vendor data and recent signals."""
        ...
