"""Prompt templates for playbook generation (Letters of Concern, Remediation Tickets, RBI Summaries)."""

PLAYBOOK_SYSTEM = """You are the Chief Risk Officer's AI assistant at an Indian bank.
You draft formal risk communications in professional financial/regulatory language.
Respond only with the document content — no preamble, no explanation."""

LETTER_OF_CONCERN_TEMPLATE = """Draft a formal Letter of Concern to the vendor {vendor_name} regarding the following risk event.

VENDOR DETAILS:
- Name: {vendor_name}
- Tier: {tier}
- Composite Risk Score: {composite_score}/100 (Band: {risk_band})
- Affected Dimension: {dimension}
- Incident Summary: {incident_summary}

REGULATORY CONTEXT: {regulatory_context}

The letter must:
1. Reference the specific RBI/CERT-In/DPDP regulation violated or at risk
2. State the bank's escalation timeline (24h response required for critical, 72h for high)
3. Request a written remediation plan with milestones
4. Warn of contract suspension if unaddressed
5. Be signed by "Third Eye Risk Management Platform, on behalf of [Bank Name]"

Format as a formal business letter with date {date}."""

REMEDIATION_TICKET_TEMPLATE = """Create a detailed Remediation Ticket for the following vendor risk finding.

FINDING:
- Vendor: {vendor_name}
- Dimension: {dimension}
- Severity: {severity}/10
- Risk Band: {risk_band}
- Description: {incident_summary}
- Triggered Rule: {triggered_rule}
- Regulatory Citation: {citation}

Generate a structured remediation ticket with:
1. Ticket ID format: REM-{vendor_code}-{date_short}
2. Priority: {priority}
3. Assigned To: [Risk Team / Vendor Management]
4. Due Date: {due_date}
5. Required Actions (numbered list of specific steps)
6. Acceptance Criteria (how we verify remediation)
7. Escalation Path if overdue"""

RBI_SUMMARY_TEMPLATE = """Draft an RBI-ready vendor risk summary for the period {period}.

PORTFOLIO OVERVIEW:
- Total Vendors Monitored: {total_vendors}
- Critical Risk: {critical_count}
- High Risk: {high_count}
- Watch: {watch_count}
- Stable: {stable_count}

TOP RISK FINDINGS:
{top_findings}

CERT-In CLOCK ACTIVATIONS: {cert_in_activations}
REGULATORY ACTIONS TRIGGERED: {regulatory_actions}

Draft this as a formal RBI submission following the format required by:
RBI Master Direction on IT Outsourcing 2023, Section 9 (Reporting Requirements).
Include: Executive Summary, Risk Heat Map description, Material Vendor Status, Remediation Status, and Forward-Looking Risk Assessment."""

BOARD_PAPER_TEMPLATE = """Draft a Board-level risk paper on vendor risk posture for {period}.

DATA:
{vendor_summary}

ALERTS SUMMARY:
{alerts_summary}

Write in formal board paper style:
1. Executive Summary (3 sentences max)
2. Current Vendor Risk Posture (with reference to risk bands)
3. Material Vendor Status (Tier 1 vendors only)
4. CERT-In Compliance Status
5. Emerging Risks (top 3)
6. Recommendations for Board Action
7. Next Review Date"""


def build_playbook_prompt(playbook_type: str, context: dict) -> tuple[str, str]:
    """Return (system_prompt, user_prompt) for the given playbook type."""
    templates = {
        "letter_of_concern": LETTER_OF_CONCERN_TEMPLATE,
        "remediation_ticket": REMEDIATION_TICKET_TEMPLATE,
        "rbi_summary": RBI_SUMMARY_TEMPLATE,
        "board_paper": BOARD_PAPER_TEMPLATE,
    }
    template = templates.get(playbook_type, REMEDIATION_TICKET_TEMPLATE)
    try:
        user = template.format(**context)
    except KeyError:
        user = template  # return raw template if context keys missing
    return PLAYBOOK_SYSTEM, user
