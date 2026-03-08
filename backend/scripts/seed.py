"""
Seed script — ports mockData.ts into PostgreSQL.
Run: python -m scripts.seed
"""
import asyncio
from datetime import date, datetime, timezone, timedelta

from sqlalchemy import text

from app.core.database import engine, async_session_factory, Base
from app.core.security import hash_password
from app.models import *  # noqa: F401, F403


VENDORS = [
    {
        "id": "v001",
        "name": "Acme Payments Ltd.",
        "category": "Payment Switch Operator",
        "composite_score": 34,
        "previous_score": 61,
        "risk_band": "high",
        "tier": "material",
        "contract_expiry": date(2025, 6, 30),
        "last_assessed": datetime(2024, 3, 4, tzinfo=timezone.utc),
        "score_cybersecurity": 28,
        "score_regulatory": 61,
        "score_operational": 70,
        "score_news_legal": 55,
        "score_financial_health": 80,
        "score_data_privacy": 72,
        "score_concentration": 65,
        "score_esg": 58,
        "score_fourth_party": 45,
        "triggers": [
            "Dark web credential dump detected (12,400 records)",
            "CVE-2024-1187 unpatched for 14 days",
        ],
        "cert_in_clock_active": True,
        "cert_in_clock_started": datetime(2024, 3, 4, 3, 17, 0, tzinfo=timezone.utc),
    },
    {
        "id": "v002",
        "name": "TechServe Infrastructure",
        "category": "Cloud Infrastructure Provider",
        "composite_score": 21,
        "previous_score": 62,
        "risk_band": "critical",
        "tier": "material",
        "contract_expiry": date(2024, 12, 31),
        "last_assessed": datetime(2024, 3, 3, tzinfo=timezone.utc),
        "score_cybersecurity": 15,
        "score_regulatory": 18,
        "score_operational": 32,
        "score_news_legal": 12,
        "score_financial_health": 41,
        "score_data_privacy": 28,
        "score_concentration": 35,
        "score_esg": 42,
        "score_fourth_party": 20,
        "triggers": [
            "RBI enforcement action filed",
            "CEO under investigation",
            "3 critical CVEs unpatched",
        ],
        "cert_in_clock_active": True,
        "cert_in_clock_started": datetime(2024, 3, 4, 1, 30, 0, tzinfo=timezone.utc),
    },
    {
        "id": "v003",
        "name": "DataBridge Analytics",
        "category": "KYC/AML Bureau",
        "composite_score": 43,
        "previous_score": 61,
        "risk_band": "high",
        "tier": "material",
        "contract_expiry": date(2025, 3, 31),
        "last_assessed": datetime(2024, 3, 2, tzinfo=timezone.utc),
        "score_cybersecurity": 52,
        "score_regulatory": 38,
        "score_operational": 55,
        "score_news_legal": 41,
        "score_financial_health": 32,
        "score_data_privacy": 45,
        "score_concentration": 48,
        "score_esg": 55,
        "score_fourth_party": 38,
        "triggers": [
            "MCA filing anomaly detected",
            "Liquidity stress indicators elevated",
        ],
        "cert_in_clock_active": False,
        "cert_in_clock_started": None,
    },
    {
        "id": "v004",
        "name": "CloudSec Systems",
        "category": "SOC Outsourcer",
        "composite_score": 47,
        "previous_score": 61,
        "risk_band": "high",
        "tier": "significant",
        "contract_expiry": date(2025, 9, 30),
        "last_assessed": datetime(2024, 3, 1, tzinfo=timezone.utc),
        "score_cybersecurity": 38,
        "score_regulatory": 55,
        "score_operational": 48,
        "score_news_legal": 62,
        "score_financial_health": 72,
        "score_data_privacy": 42,
        "score_concentration": 55,
        "score_esg": 48,
        "score_fourth_party": 35,
        "triggers": [
            "CVE-2024-1187 unpatched",
            "SLA breach: response time exceeded 3x in February",
        ],
        "cert_in_clock_active": False,
        "cert_in_clock_started": None,
    },
    {
        "id": "v005",
        "name": "FinCore Banking Solutions",
        "category": "Core Banking Platform",
        "composite_score": 78,
        "previous_score": 75,
        "risk_band": "stable",
        "tier": "material",
        "contract_expiry": date(2026, 12, 31),
        "last_assessed": datetime(2024, 2, 28, tzinfo=timezone.utc),
        "score_cybersecurity": 82,
        "score_regulatory": 88,
        "score_operational": 85,
        "score_news_legal": 90,
        "score_financial_health": 78,
        "score_data_privacy": 75,
        "score_concentration": 42,
        "score_esg": 72,
        "score_fourth_party": 55,
        "triggers": [],
        "cert_in_clock_active": False,
        "cert_in_clock_started": None,
    },
    {
        "id": "v006",
        "name": "SecureAuth India",
        "category": "Identity & Access Management",
        "composite_score": 85,
        "previous_score": 82,
        "risk_band": "stable",
        "tier": "significant",
        "contract_expiry": date(2025, 11, 30),
        "last_assessed": datetime(2024, 2, 28, tzinfo=timezone.utc),
        "score_cybersecurity": 90,
        "score_regulatory": 85,
        "score_operational": 88,
        "score_news_legal": 92,
        "score_financial_health": 82,
        "score_data_privacy": 88,
        "score_concentration": 72,
        "score_esg": 78,
        "score_fourth_party": 62,
        "triggers": [],
        "cert_in_clock_active": False,
        "cert_in_clock_started": None,
    },
    {
        "id": "v007",
        "name": "PaySwitch Pro",
        "category": "Payment Gateway",
        "composite_score": 62,
        "previous_score": 68,
        "risk_band": "watch",
        "tier": "material",
        "contract_expiry": date(2025, 8, 15),
        "last_assessed": datetime(2024, 3, 1, tzinfo=timezone.utc),
        "score_cybersecurity": 65,
        "score_regulatory": 58,
        "score_operational": 62,
        "score_news_legal": 70,
        "score_financial_health": 55,
        "score_data_privacy": 68,
        "score_concentration": 58,
        "score_esg": 52,
        "score_fourth_party": 48,
        "triggers": [
            "Minor SLA degradation in February",
            "Competitor acquisition rumor",
        ],
        "cert_in_clock_active": False,
        "cert_in_clock_started": None,
    },
    {
        "id": "v008",
        "name": "ATM Networks India",
        "category": "ATM Operations",
        "composite_score": 71,
        "previous_score": 73,
        "risk_band": "watch",
        "tier": "significant",
        "contract_expiry": date(2025, 5, 31),
        "last_assessed": datetime(2024, 2, 25, tzinfo=timezone.utc),
        "score_cybersecurity": 72,
        "score_regulatory": 75,
        "score_operational": 68,
        "score_news_legal": 78,
        "score_financial_health": 70,
        "score_data_privacy": 65,
        "score_concentration": 75,
        "score_esg": 62,
        "score_fourth_party": 55,
        "triggers": ["Contract renewal approaching"],
        "cert_in_clock_active": False,
        "cert_in_clock_started": None,
    },
    {
        "id": "v009",
        "name": "DataVault Storage",
        "category": "Data Center Provider",
        "composite_score": 88,
        "previous_score": 86,
        "risk_band": "stable",
        "tier": "standard",
        "contract_expiry": date(2026, 6, 30),
        "last_assessed": datetime(2024, 2, 20, tzinfo=timezone.utc),
        "score_cybersecurity": 92,
        "score_regulatory": 90,
        "score_operational": 88,
        "score_news_legal": 95,
        "score_financial_health": 85,
        "score_data_privacy": 82,
        "score_concentration": 80,
        "score_esg": 88,
        "score_fourth_party": 72,
        "triggers": [],
        "cert_in_clock_active": False,
        "cert_in_clock_started": None,
    },
    {
        "id": "v010",
        "name": "ComplianceFirst",
        "category": "Regulatory Reporting",
        "composite_score": 55,
        "previous_score": 60,
        "risk_band": "watch",
        "tier": "standard",
        "contract_expiry": date(2025, 4, 30),
        "last_assessed": datetime(2024, 2, 28, tzinfo=timezone.utc),
        "score_cybersecurity": 58,
        "score_regulatory": 52,
        "score_operational": 60,
        "score_news_legal": 55,
        "score_financial_health": 62,
        "score_data_privacy": 50,
        "score_concentration": 48,
        "score_esg": 45,
        "score_fourth_party": 42,
        "triggers": ["Data privacy audit finding pending"],
        "cert_in_clock_active": False,
        "cert_in_clock_started": None,
    },
]

ALERTS = [
    {"id": "a001", "vendor_id": "v002", "vendor_name": "TechServe Infrastructure", "severity": "critical", "title": "RBI Enforcement Action Filed", "description": "Reserve Bank of India has filed an enforcement action against TechServe Infrastructure for non-compliance with IT outsourcing directions.", "dimension": "Regulatory Compliance", "status": "new", "created_at": datetime(2024, 3, 4, 1, 30, tzinfo=timezone.utc)},
    {"id": "a002", "vendor_id": "v001", "vendor_name": "Acme Payments Ltd.", "severity": "high", "title": "Dark Web Credential Dump", "description": "12,400 credential records linked to Acme Payments detected on dark web marketplace. Includes employee and potentially customer-linked data.", "dimension": "Cybersecurity Posture", "status": "acknowledged", "created_at": datetime(2024, 3, 4, 3, 17, tzinfo=timezone.utc)},
    {"id": "a003", "vendor_id": "v003", "vendor_name": "DataBridge Analytics", "severity": "high", "title": "Financial Stress Indicators", "description": "MCA21 filing anomaly detected. Delayed annual returns and liquidity stress indicators suggest financial health deterioration.", "dimension": "Financial Health", "status": "assigned", "assigned_to": "Rahul Mehta", "created_at": datetime(2024, 3, 3, 14, 22, tzinfo=timezone.utc)},
    {"id": "a004", "vendor_id": "v004", "vendor_name": "CloudSec Systems", "severity": "high", "title": "Critical CVE Unpatched", "description": "CVE-2024-1187 (CVSS 9.8) remains unpatched after 14 days. Affects CloudSec's perimeter firewall appliances.", "dimension": "Cybersecurity Posture", "status": "assigned", "assigned_to": "Priya Sharma", "created_at": datetime(2024, 3, 2, 9, 45, tzinfo=timezone.utc)},
    {"id": "a005", "vendor_id": "v007", "vendor_name": "PaySwitch Pro", "severity": "watch", "title": "SLA Performance Degradation", "description": "Transaction processing latency exceeded SLA thresholds 3 times in February. P99 latency increased 40% month-over-month.", "dimension": "Operational Resilience", "status": "acknowledged", "created_at": datetime(2024, 3, 1, 11, 0, tzinfo=timezone.utc)},
    {"id": "a006", "vendor_id": "v002", "vendor_name": "TechServe Infrastructure", "severity": "critical", "title": "CEO Under Investigation", "description": "TechServe CEO named in SEBI investigation for insider trading. Board instability risk elevated.", "dimension": "News & Legal", "status": "new", "created_at": datetime(2024, 3, 3, 8, 15, tzinfo=timezone.utc)},
    {"id": "a007", "vendor_id": "v010", "vendor_name": "ComplianceFirst", "severity": "watch", "title": "Data Privacy Audit Finding", "description": "Pending audit finding related to DPDP Act compliance. Data processing agreement requires update.", "dimension": "Data Privacy", "status": "assigned", "assigned_to": "Anil Kumar", "created_at": datetime(2024, 2, 28, 16, 30, tzinfo=timezone.utc)},
]

WORKFLOWS = [
    {"id": "w001", "vendor_id": "v002", "vendor_name": "TechServe Infrastructure", "title": "Initiate vendor review — RBI enforcement action", "priority": "critical", "status": "open", "assigned_to": "CISO Office", "assigned_role": "CISO", "due_date": datetime(2024, 3, 4, 7, 30, tzinfo=timezone.utc), "audit_trail_id": "AUD-2024-7820", "created_at": datetime(2024, 3, 4, 1, 35, tzinfo=timezone.utc)},
    {"id": "w002", "vendor_id": "v001", "vendor_name": "Acme Payments Ltd.", "title": "Assess data scope — dark web credential dump", "priority": "critical", "status": "in_progress", "assigned_to": "Priya Sharma", "assigned_role": "CISO", "due_date": datetime(2024, 3, 4, 9, 17, tzinfo=timezone.utc), "audit_trail_id": "AUD-2024-7821", "created_at": datetime(2024, 3, 4, 3, 20, tzinfo=timezone.utc)},
    {"id": "w003", "vendor_id": "v003", "vendor_name": "DataBridge Analytics", "title": "Review financial health — MCA filing anomaly", "priority": "high", "status": "in_progress", "assigned_to": "Rahul Mehta", "assigned_role": "CRO", "due_date": datetime(2024, 3, 5, 14, 30, tzinfo=timezone.utc), "audit_trail_id": "AUD-2024-7815", "created_at": datetime(2024, 3, 3, 14, 30, tzinfo=timezone.utc)},
    {"id": "w004", "vendor_id": "v004", "vendor_name": "CloudSec Systems", "title": "Verify CVE-2024-1187 patch status", "priority": "high", "status": "pending_review", "assigned_to": "Priya Sharma", "assigned_role": "CISO", "due_date": datetime(2024, 3, 4, 10, 0, tzinfo=timezone.utc), "audit_trail_id": "AUD-2024-7810", "created_at": datetime(2024, 3, 2, 10, 0, tzinfo=timezone.utc)},
    {"id": "w005", "vendor_id": "v007", "vendor_name": "PaySwitch Pro", "title": "SLA breach root cause analysis", "priority": "medium", "status": "open", "assigned_to": "Vendor Risk Team", "assigned_role": "Vendor Risk", "due_date": datetime(2024, 3, 6, 11, 15, tzinfo=timezone.utc), "audit_trail_id": "AUD-2024-7805", "created_at": datetime(2024, 3, 1, 11, 15, tzinfo=timezone.utc)},
    {"id": "w006", "vendor_id": "v010", "vendor_name": "ComplianceFirst", "title": "Update data processing agreement — DPDP", "priority": "medium", "status": "open", "assigned_to": "Anil Kumar", "assigned_role": "Compliance", "due_date": datetime(2024, 3, 10, 17, 0, tzinfo=timezone.utc), "audit_trail_id": "AUD-2024-7798", "created_at": datetime(2024, 2, 28, 17, 0, tzinfo=timezone.utc)},
]

COMPLIANCE = [
    {"regulation": "RBI IT Outsourcing Directions 2023", "category": "RBI", "score": 67, "status": "partial", "last_checked": date(2024, 3, 4), "gaps": ["Board reporting frequency below quarterly threshold", "3 vendors missing right-to-audit clause", "Material outsourcing register incomplete"]},
    {"regulation": "CERT-In Cyber Incident Reporting", "category": "CERT-In", "score": 48, "status": "non_compliant", "last_checked": date(2024, 3, 4), "gaps": ["6-hour reporting workflow not fully automated", "2 critical vendors lack incident notification SLA", "Dark web monitoring coverage at 60%"]},
    {"regulation": "DPDP Act 2023", "category": "DPDP", "score": 58, "status": "partial", "last_checked": date(2024, 3, 3), "gaps": ["PII vendor exposure mapping incomplete", "Data processing agreements need updating for 8 vendors", "Breach notification workflow not DPDP-aligned"]},
    {"regulation": "RBI Cybersecurity Framework", "category": "RBI", "score": 72, "status": "partial", "last_checked": date(2024, 3, 2), "gaps": ["SOC 2 compliance verification pending for 4 vendors", "Security posture monitoring gaps in Tier 2 vendors"]},
    {"regulation": "SEBI / MCA21 Monitoring", "category": "SEBI", "score": 79, "status": "compliant", "last_checked": date(2024, 3, 1), "gaps": ["Filing anomaly detection latency above 24 hours for MCA21"]},
]

RISK_TRENDS = [
    {"snapshot_date": date(2024, 2, 4), "aggregate_score": 68, "critical_count": 0, "high_count": 5, "watch_count": 18},
    {"snapshot_date": date(2024, 2, 11), "aggregate_score": 66, "critical_count": 0, "high_count": 6, "watch_count": 20},
    {"snapshot_date": date(2024, 2, 18), "aggregate_score": 64, "critical_count": 1, "high_count": 7, "watch_count": 22},
    {"snapshot_date": date(2024, 2, 25), "aggregate_score": 62, "critical_count": 1, "high_count": 8, "watch_count": 25},
    {"snapshot_date": date(2024, 3, 1), "aggregate_score": 60, "critical_count": 1, "high_count": 9, "watch_count": 28},
    {"snapshot_date": date(2024, 3, 4), "aggregate_score": 58, "critical_count": 2, "high_count": 11, "watch_count": 34},
]

CONSORTIUM_NODES = [
    {"bank_name": "State Bank of India", "node_status": "online", "vendors_monitored": 420, "last_signal_at": datetime(2024, 3, 4, 3, 15, tzinfo=timezone.utc)},
    {"bank_name": "HDFC Bank", "node_status": "online", "vendors_monitored": 380, "last_signal_at": datetime(2024, 3, 4, 3, 17, tzinfo=timezone.utc)},
    {"bank_name": "ICICI Bank", "node_status": "syncing", "vendors_monitored": 350, "last_signal_at": datetime(2024, 3, 4, 2, 45, tzinfo=timezone.utc)},
    {"bank_name": "Axis Bank", "node_status": "online", "vendors_monitored": 310, "last_signal_at": datetime(2024, 3, 4, 3, 10, tzinfo=timezone.utc)},
    {"bank_name": "Kotak Mahindra Bank", "node_status": "offline", "vendors_monitored": 280, "last_signal_at": datetime(2024, 3, 3, 22, 0, tzinfo=timezone.utc)},
]

CONSORTIUM_SIGNALS = [
    {"signal_type": "CRITICAL_BREACH", "dimension": "Cybersecurity", "vendor_hash": "sha256:a3f9e2c1d8b7", "severity": "critical", "cert_in_relevant": True, "received_at": datetime(2024, 3, 4, 3, 17, tzinfo=timezone.utc)},
    {"signal_type": "ENFORCEMENT_ACTION", "dimension": "Regulatory", "vendor_hash": "sha256:b4e8d3a2c9f6", "severity": "critical", "cert_in_relevant": False, "received_at": datetime(2024, 3, 4, 1, 30, tzinfo=timezone.utc)},
    {"signal_type": "FINANCIAL_STRESS", "dimension": "Financial Health", "vendor_hash": "sha256:c7d6e5f4a3b2", "severity": "high", "cert_in_relevant": False, "received_at": datetime(2024, 3, 3, 14, 22, tzinfo=timezone.utc)},
    {"signal_type": "CVE_CRITICAL", "dimension": "Cybersecurity", "vendor_hash": "sha256:d1e2f3a4b5c6", "severity": "high", "cert_in_relevant": True, "received_at": datetime(2024, 3, 2, 9, 45, tzinfo=timezone.utc)},
]

REPORTS = [
    {"title": "Vendor Risk Summary — Board Paper Q1 2024", "report_type": "board_paper", "regulation": "RBI", "status": "ready", "generated_at": datetime(2024, 3, 4, tzinfo=timezone.utc)},
    {"title": "Material Outsourcing Register", "report_type": "regulatory_register", "regulation": "RBI", "status": "ready", "generated_at": datetime(2024, 3, 3, tzinfo=timezone.utc)},
    {"title": "CERT-In Incident Timeline — March 2024", "report_type": "incident_report", "regulation": "CERT-In", "status": "ready", "generated_at": datetime(2024, 3, 4, tzinfo=timezone.utc)},
    {"title": "Concentration Risk Assessment", "report_type": "risk_analysis", "regulation": "RBI", "status": "ready", "generated_at": datetime(2024, 3, 2, tzinfo=timezone.utc)},
    {"title": "DPDP Compliance Status Report", "report_type": "compliance_report", "regulation": "DPDP", "status": "ready", "generated_at": datetime(2024, 3, 1, tzinfo=timezone.utc)},
    {"title": "Audit Findings Package — Q1 2024", "report_type": "audit_package", "regulation": "RBI", "status": "generating"},
]


async def seed():
    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    async with async_session_factory() as session:
        # Admin user
        admin = User(
            email="admin@thirdeye.io",
            hashed_password=hash_password("thirdeye_admin"),
            full_name="Third Eye Admin",
            role="cto",
        )
        session.add(admin)

        # Demo users
        for role, name, email in [
            ("ciso", "Priya Sharma", "priya@thirdeye.io"),
            ("compliance", "Anil Kumar", "anil@thirdeye.io"),
            ("vendor_risk", "Rahul Mehta", "rahul@thirdeye.io"),
        ]:
            session.add(User(
                email=email,
                hashed_password=hash_password("demo123"),
                full_name=name,
                role=role,
            ))

        # Vendors — must flush before FK-dependent tables
        for v_data in VENDORS:
            session.add(Vendor(**v_data))
        await session.flush()

        # Alerts (FK → vendors)
        for a_data in ALERTS:
            session.add(Alert(**a_data))

        # Workflows (FK → vendors)
        for w_data in WORKFLOWS:
            session.add(WorkflowItem(**w_data))

        # Compliance
        for c_data in COMPLIANCE:
            session.add(ComplianceStatus(**c_data))

        # Risk trends
        for t_data in RISK_TRENDS:
            session.add(RiskTrendSnapshot(**t_data))

        # Consortium nodes
        for n_data in CONSORTIUM_NODES:
            session.add(ConsortiumNode(**n_data))

        # Consortium signals
        for s_data in CONSORTIUM_SIGNALS:
            session.add(ConsortiumSignal(**s_data))

        # Reports
        for r_data in REPORTS:
            session.add(Report(**r_data))

        await session.commit()
        print("Seed complete. Database populated with mockData equivalent.")
        print("Admin login: admin@thirdeye.io / thirdeye_admin")


if __name__ == "__main__":
    asyncio.run(seed())
