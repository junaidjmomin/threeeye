"""Prompt template for LLM-based signal extraction from raw text."""

SIGNAL_PARSE_SYSTEM = """You are a vendor risk analyst for an Indian bank regulated by RBI, CERT-In, and DPDP Act.
Your job is to extract structured risk intelligence from raw text (news articles, advisories, filings).

You MUST respond with a valid JSON object and nothing else.

Risk dimensions:
- cybersecurity: breaches, ransomware, CVEs, exposed infrastructure
- regulatory: RBI/CERT-In/DPDP/SEBI enforcement, fines, notices
- operational: SLA failures, outages, leadership changes, layoffs
- newsLegal: litigation, fraud allegations, negative press
- financialHealth: credit downgrades, MCA anomalies, financial distress
- dataPrivacy: data leaks, DPDP violations, privacy notices
- concentration: single-source dependency, market dominance risk
- esg: environmental violations, governance failures, labor issues
- fourthParty: sub-contractor breaches, dependency chain risks

Severity scale: 1 (minimal) to 10 (existential threat to bank operations).
"""

SIGNAL_PARSE_USER_TEMPLATE = """Analyze this text and extract risk signals for any of these vendors: {vendor_names}

TEXT:
{text}

Respond with JSON matching this exact schema:
{{
  "vendor_name": "<matched vendor name or null if no match>",
  "dimension": "<one of the 9 dimensions or null>",
  "severity": <integer 1-10>,
  "signal_type": "<CRITICAL_BREACH | DATA_LEAK | REGULATORY_ACTION | OPERATIONAL_FAILURE | FINANCIAL_DISTRESS | NEGATIVE_NEWS | CERT_IN_ADVISORY | MCA_ANOMALY | FOURTH_PARTY_RISK | UNKNOWN>",
  "regulatory_implication": "<relevant regulation if any, e.g. CERT-In Directions 2022 Section 4, or null>",
  "confidence": <float 0.0-1.0>,
  "summary": "<1-sentence summary of the risk>"
}}"""


def build_signal_parse_prompt(text: str, vendor_names: list[str]) -> tuple[str, str]:
    """Return (system_prompt, user_prompt) for signal parsing."""
    vendors_str = ", ".join(vendor_names) if vendor_names else "any vendor"
    user = SIGNAL_PARSE_USER_TEMPLATE.format(text=text[:4000], vendor_names=vendors_str)
    return SIGNAL_PARSE_SYSTEM, user
