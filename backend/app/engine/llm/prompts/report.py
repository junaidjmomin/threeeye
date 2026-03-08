"""Prompt templates for narrative report generation."""

REPORT_SYSTEM = """You are a senior risk analyst writing board-level and regulatory reports for an Indian bank.
Your writing is precise, formal, and data-driven. Avoid jargon. Use specific numbers.
Respond only with the report content."""

NARRATIVE_REPORT_TEMPLATE = """Write a comprehensive vendor risk narrative report for {period}.

RISK METRICS:
- Portfolio composite risk score: {portfolio_score}/100
- Score change from last period: {score_delta:+d} points
- Vendors in critical band: {critical_count}
- Vendors in high band: {high_count}
- CERT-In clock activations this period: {cert_in_activations}

TOP VENDOR RISKS:
{top_vendor_risks}

COMPLIANCE STATUS:
- RBI Outsourcing Compliance: {rbi_score}%
- CERT-In Compliance: {certin_score}%
- DPDP Act Compliance: {dpdp_score}%

ACTIVE ALERTS: {open_alerts} open, {resolved_alerts} resolved this period

Write sections:
1. Executive Summary
2. Portfolio Risk Trend Analysis
3. Critical and High Risk Vendor Details
4. Regulatory Compliance Overview
5. CERT-In Incident Log
6. Remediation Progress
7. Outlook and Recommendations"""

VENDOR_NARRATIVE_TEMPLATE = """Write a detailed risk narrative for vendor {vendor_name}.

VENDOR PROFILE:
- Tier: {tier}
- Composite Score: {composite_score}/100 (Band: {risk_band})
- Previous Score: {previous_score}/100
- Score Change: {score_delta:+d}

DIMENSION SCORES:
{dimension_scores}

RECENT SIGNALS ({signal_count} in last 30 days):
{recent_signals}

ACTIVE ALERTS: {active_alerts}
OPEN REMEDIATION ITEMS: {open_workflows}

Write a 3-paragraph narrative covering:
1. Current risk status and key drivers
2. Regulatory implications (RBI/CERT-In/DPDP)
3. Recommended actions with priority and timeline"""


def build_report_prompt(report_type: str, context: dict) -> tuple[str, str]:
    """Return (system_prompt, user_prompt) for report generation."""
    if report_type == "vendor_narrative":
        template = VENDOR_NARRATIVE_TEMPLATE
    else:
        template = NARRATIVE_REPORT_TEMPLATE
    try:
        user = template.format(**context)
    except KeyError:
        user = template
    return REPORT_SYSTEM, user
