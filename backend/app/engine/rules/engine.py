"""
Policy-as-Code Rule Engine.

Discovers all BaseRule subclasses and evaluates them against vendor data + signals.
Every triggered result carries a regulatory citation for audit defensibility.
"""
from __future__ import annotations

import importlib
import logging
import pkgutil
from pathlib import Path
from typing import Iterator

from app.engine.rules.base_rule import BaseRule, RuleResult

logger = logging.getLogger(__name__)

# Modules to auto-discover rules from
_RULES_PACKAGE = "app.engine.rules"
_RULES_DIR = Path(__file__).parent


def _iter_rule_modules() -> Iterator[str]:
    """Yield module names in the rules package (excluding engine and base)."""
    excluded = {"engine", "base_rule", "__init__"}
    for finder, name, _ in pkgutil.iter_modules([str(_RULES_DIR)]):
        if name not in excluded:
            yield f"{_RULES_PACKAGE}.{name}"


def _discover_rules() -> list[type[BaseRule]]:
    """Import all rule modules and collect concrete BaseRule subclasses."""
    rule_classes: list[type[BaseRule]] = []
    seen: set[str] = set()

    for module_name in _iter_rule_modules():
        try:
            mod = importlib.import_module(module_name)
        except Exception as exc:
            logger.warning("Failed to import rule module %s: %s", module_name, exc)
            continue

        for attr_name in dir(mod):
            attr = getattr(mod, attr_name)
            if (
                isinstance(attr, type)
                and issubclass(attr, BaseRule)
                and attr is not BaseRule
                and attr.__name__ not in seen
            ):
                rule_classes.append(attr)
                seen.add(attr.__name__)

    return rule_classes


class RuleEngine:
    """Evaluate all registered Policy-as-Code rules against vendor data."""

    def __init__(self, rules: list[BaseRule] | None = None) -> None:
        if rules is not None:
            self._rules = rules
        else:
            self._rules = [cls() for cls in _discover_rules()]
        logger.debug("RuleEngine initialised with %d rules", len(self._rules))

    @property
    def rules(self) -> list[BaseRule]:
        return list(self._rules)

    def run_all(
        self,
        vendor_data: dict,
        signals: list[dict],
    ) -> list[RuleResult]:
        """
        Evaluate every rule.

        Returns only the results that were triggered.
        Each result has a non-empty citation field.
        """
        triggered: list[RuleResult] = []

        for rule in self._rules:
            try:
                result = rule.evaluate(vendor_data, signals)
            except Exception as exc:
                logger.error("Rule %s raised an error: %s", rule.name, exc)
                continue

            if result.triggered:
                if not result.citation:
                    logger.warning(
                        "Rule '%s' triggered without a citation — audit gap!", rule.name
                    )
                triggered.append(result)

        return triggered

    def run_for_action(
        self,
        vendor_data: dict,
        signals: list[dict],
        action: str,
    ) -> list[RuleResult]:
        """Return only triggered results matching a specific action type."""
        return [
            r for r in self.run_all(vendor_data, signals)
            if r.action == action
        ]
