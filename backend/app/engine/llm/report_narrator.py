"""
Report narrator: structured data → Board paper / RBI submission narrative.
"""
from __future__ import annotations

from app.engine.llm.prompts.report import build_report_prompt
from app.engine.llm.provider import LLMProvider


async def narrate_report(
    report_type: str,
    context: dict,
    provider: LLMProvider,
) -> str:
    """
    Generate a narrative report section using the LLM.

    Args:
        report_type: "portfolio_narrative" | "vendor_narrative"
        context: dict matching the relevant prompt template variables
        provider: LLMProvider instance

    Returns:
        Narrative text as a string.
    """
    system, user = build_report_prompt(report_type, context)
    return await provider.complete(system, user)


def build_portfolio_context(
    vendors: list[dict],
    alerts: list[dict],
    period: str,
) -> dict:
    """Assemble context dict for portfolio-level narrative."""
    scores = [v.get("composite_score", 50) for v in vendors]
    portfolio_score = int(sum(scores) / len(scores)) if scores else 0

    band_counts: dict[str, int] = {"critical": 0, "high": 0, "watch": 0, "stable": 0}
    for v in vendors:
        band = v.get("risk_band", "stable")
        band_counts[band] = band_counts.get(band, 0) + 1

    open_alerts = sum(1 for a in alerts if a.get("status") not in ("resolved",))
    resolved_alerts = sum(1 for a in alerts if a.get("status") == "resolved")

    cert_in_activations = sum(
        1 for v in vendors if v.get("cert_in_clock_active", False)
    )

    top_risks = sorted(vendors, key=lambda v: v.get("composite_score", 100))[:5]
    top_vendor_risks = "\n".join(
        f"- {v.get('name', 'Unknown')}: score {v.get('composite_score', 0)}, "
        f"band {v.get('risk_band', 'unknown')}, tier {v.get('tier', 'standard')}"
        for v in top_risks
    )

    return {
        "period": period,
        "portfolio_score": portfolio_score,
        "score_delta": 0,  # caller can provide if available
        "critical_count": band_counts["critical"],
        "high_count": band_counts["high"],
        "watch_count": band_counts["watch"],
        "stable_count": band_counts["stable"],
        "cert_in_activations": cert_in_activations,
        "top_vendor_risks": top_vendor_risks,
        "rbi_score": 85,   # caller provides real compliance scores
        "certin_score": 90,
        "dpdp_score": 78,
        "open_alerts": open_alerts,
        "resolved_alerts": resolved_alerts,
        "regulatory_actions": 0,
    }


def build_vendor_context(
    vendor: dict,
    signals: list[dict],
    workflows: list[dict],
    alerts: list[dict],
) -> dict:
    """Assemble context dict for per-vendor narrative."""
    dims = [
        "cybersecurity", "regulatory", "operational", "newsLegal",
        "financialHealth", "dataPrivacy", "concentration", "esg", "fourthParty",
    ]
    dimension_lines = "\n".join(
        f"  {d}: {vendor.get(d, 'N/A')}" for d in dims
    )

    recent = signals[-10:] if signals else []
    signal_lines = "\n".join(
        f"  - [{s.get('signal_type', '?')}] {s.get('summary', '')}" for s in recent
    ) or "  None"

    active_alerts = sum(1 for a in alerts if a.get("status") != "resolved")
    open_workflows = sum(1 for w in workflows if w.get("status") != "completed")

    score = vendor.get("composite_score", 50)
    prev = vendor.get("previous_score", score)

    return {
        "vendor_name": vendor.get("name", "Unknown"),
        "tier": vendor.get("tier", "standard"),
        "composite_score": score,
        "previous_score": prev,
        "score_delta": score - prev,
        "risk_band": vendor.get("risk_band", "watch"),
        "dimension_scores": dimension_lines,
        "signal_count": len(signals),
        "recent_signals": signal_lines,
        "active_alerts": active_alerts,
        "open_workflows": open_workflows,
    }
