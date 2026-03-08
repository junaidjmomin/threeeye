"""
Compound Risk Correlation Engine.
Detects multi-signal risks that no single dimension catches alone.

Example: negative_news + open_shodan_ports + sla_degradation
         = HIGH breach probability (score multiplier: 0.6x)

Phase 2: Full implementation with signal database queries.
"""
from dataclasses import dataclass


@dataclass
class CompoundPattern:
    name: str
    signals: list[str]
    min_signals: int
    score_multiplier: float
    description: str


@dataclass
class CompoundRisk:
    pattern_name: str
    matched_signals: list[str]
    multiplier: float
    description: str


PATTERNS = [
    CompoundPattern(
        name="breach_probability",
        signals=["negative_news", "open_ports", "sla_degradation"],
        min_signals=2,
        score_multiplier=0.6,
        description="High breach probability: multiple correlated risk signals",
    ),
    CompoundPattern(
        name="financial_collapse",
        signals=["mca_filing_anomaly", "credit_downgrade", "leadership_change"],
        min_signals=2,
        score_multiplier=0.5,
        description="Financial collapse risk: compounding instability signals",
    ),
    CompoundPattern(
        name="regulatory_cascade",
        signals=["rbi_enforcement", "dpdp_violation", "cert_in_advisory"],
        min_signals=2,
        score_multiplier=0.4,
        description="Regulatory cascade: multiple regulatory bodies flagging simultaneously",
    ),
]


def detect_compound_risks(active_signal_types: list[str]) -> list[CompoundRisk]:
    """Check active signals against all compound patterns."""
    results = []
    signal_set = set(active_signal_types)

    for pattern in PATTERNS:
        matched = [s for s in pattern.signals if s in signal_set]
        if len(matched) >= pattern.min_signals:
            results.append(CompoundRisk(
                pattern_name=pattern.name,
                matched_signals=matched,
                multiplier=pattern.score_multiplier,
                description=pattern.description,
            ))

    return results
