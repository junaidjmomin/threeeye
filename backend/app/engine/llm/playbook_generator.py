"""
Playbook generator: risk event → Letter of Concern / Remediation Ticket / RBI Summary.
"""
from __future__ import annotations

from datetime import date, timedelta

from app.engine.llm.prompts.playbook import build_playbook_prompt
from app.engine.llm.provider import LLMProvider

PLAYBOOK_TYPES = ("letter_of_concern", "remediation_ticket", "rbi_summary", "board_paper")

PRIORITY_BY_BAND = {
    "critical": "P1 - Critical",
    "high": "P2 - High",
    "watch": "P3 - Medium",
    "stable": "P4 - Low",
}

DUE_DAYS_BY_BAND = {
    "critical": 1,
    "high": 3,
    "watch": 7,
    "stable": 14,
}


async def generate_playbook(
    playbook_type: str,
    vendor_data: dict,
    provider: LLMProvider,
    extra_context: dict | None = None,
) -> str:
    """
    Generate a playbook document for a vendor risk event.

    Args:
        playbook_type: one of PLAYBOOK_TYPES
        vendor_data: dict with keys like vendor_name, tier, composite_score,
                     risk_band, dimension, incident_summary, citation, etc.
        provider: LLMProvider instance
        extra_context: optional extra fields to merge into the prompt context

    Returns:
        Formatted document as a string.
    """
    today = date.today()
    risk_band = vendor_data.get("risk_band", "watch")
    due_delta = DUE_DAYS_BY_BAND.get(risk_band, 7)

    context = {
        "vendor_name": vendor_data.get("vendor_name", "Unknown Vendor"),
        "vendor_code": (vendor_data.get("vendor_name", "UNK") or "UNK")[:3].upper(),
        "tier": vendor_data.get("tier", "standard"),
        "composite_score": vendor_data.get("composite_score", 50),
        "previous_score": vendor_data.get("previous_score", 50),
        "score_delta": vendor_data.get("composite_score", 50) - vendor_data.get("previous_score", 50),
        "risk_band": risk_band,
        "dimension": vendor_data.get("dimension", ""),
        "incident_summary": vendor_data.get("incident_summary", "Risk event detected"),
        "regulatory_context": vendor_data.get("regulatory_context", ""),
        "triggered_rule": vendor_data.get("triggered_rule", ""),
        "citation": vendor_data.get("citation", ""),
        "severity": vendor_data.get("severity", 5),
        "priority": PRIORITY_BY_BAND.get(risk_band, "P3 - Medium"),
        "date": today.strftime("%d %B %Y"),
        "date_short": today.strftime("%Y%m%d"),
        "due_date": (today + timedelta(days=due_delta)).strftime("%d %B %Y"),
        **(extra_context or {}),
    }

    system, user = build_playbook_prompt(playbook_type, context)
    return await provider.complete(system, user)
