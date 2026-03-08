"""
LLM-based signal parser: raw text → ParsedSignal.

Extracts structured risk intelligence from unstructured text
(news articles, advisories, filings, alerts).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from app.engine.llm.provider import LLMProvider
from app.engine.llm.prompts.signal_parse import build_signal_parse_prompt

VALID_DIMENSIONS = {
    "cybersecurity", "regulatory", "operational", "newsLegal",
    "financialHealth", "dataPrivacy", "concentration", "esg", "fourthParty",
}

VALID_SIGNAL_TYPES = {
    "CRITICAL_BREACH", "DATA_LEAK", "REGULATORY_ACTION", "OPERATIONAL_FAILURE",
    "FINANCIAL_DISTRESS", "NEGATIVE_NEWS", "CERT_IN_ADVISORY", "MCA_ANOMALY",
    "FOURTH_PARTY_RISK", "UNKNOWN",
}


@dataclass
class ParsedSignal:
    vendor_name: Optional[str]
    dimension: Optional[str]
    severity: int                          # 1–10
    signal_type: str                       # one of VALID_SIGNAL_TYPES
    regulatory_implication: Optional[str]
    confidence: float                      # 0.0–1.0
    summary: str
    raw_text: str = field(default="", repr=False)


async def parse_signal(
    text: str,
    vendor_names: list[str],
    provider: LLMProvider,
) -> ParsedSignal:
    """
    Parse raw text into a structured ParsedSignal using the LLM.

    Returns a ParsedSignal. If LLM fails or returns invalid JSON,
    returns a low-confidence UNKNOWN signal so the pipeline keeps moving.
    """
    system, user = build_signal_parse_prompt(text, vendor_names)

    try:
        data = await provider.complete_json(system, user)
    except Exception:
        return ParsedSignal(
            vendor_name=None,
            dimension=None,
            severity=1,
            signal_type="UNKNOWN",
            regulatory_implication=None,
            confidence=0.0,
            summary="LLM parsing failed — manual review required",
            raw_text=text,
        )

    vendor = data.get("vendor_name")
    # Validate vendor match
    if vendor and vendor_names and vendor not in vendor_names:
        # fuzzy fallback: check if any vendor name is a substring
        matched = next(
            (v for v in vendor_names if v.lower() in vendor.lower() or vendor.lower() in v.lower()),
            None,
        )
        vendor = matched

    dimension = data.get("dimension")
    if dimension not in VALID_DIMENSIONS:
        dimension = None

    signal_type = data.get("signal_type", "UNKNOWN")
    if signal_type not in VALID_SIGNAL_TYPES:
        signal_type = "UNKNOWN"

    severity = int(data.get("severity", 5))
    severity = max(1, min(10, severity))

    confidence = float(data.get("confidence", 0.5))
    confidence = max(0.0, min(1.0, confidence))

    return ParsedSignal(
        vendor_name=vendor,
        dimension=dimension,
        severity=severity,
        signal_type=signal_type,
        regulatory_implication=data.get("regulatory_implication"),
        confidence=confidence,
        summary=data.get("summary", ""),
        raw_text=text,
    )
