<div align="center">

```
████████╗██╗  ██╗██╗██████╗ ██████╗     ███████╗██╗   ██╗███████╗
╚══██╔══╝██║  ██║██║██╔══██╗██╔══██╗    ██╔════╝╚██╗ ██╔╝██╔════╝
   ██║   ███████║██║██████╔╝██║  ██║    █████╗   ╚████╔╝ █████╗  
   ██║   ██╔══██║██║██╔══██╗██║  ██║    ██╔══╝    ╚██╔╝  ██╔══╝  
   ██║   ██║  ██║██║██║  ██║██████╔╝    ███████╗   ██║   ███████╗
   ╚═╝   ╚═╝  ╚═╝╚═╝╚═╝  ╚═╝╚═════╝    ╚══════╝   ╚═╝   ╚══════╝
```

# 👁 THIRD EYE

### *Your Risk Is Our Risk.*

> **AI-Powered Continuous Vendor Risk Intelligence Platform**  
> Built for Indian Banks & Financial Institutions Operating Under RBI, CERT-In, and DPDP Pressure

---

![Status](https://img.shields.io/badge/Status-Active%20Development-brightgreen?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-blue?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.11+-yellow?style=for-the-badge&logo=python)
![React](https://img.shields.io/badge/React-18+-61DAFB?style=for-the-badge&logo=react)
![AWS](https://img.shields.io/badge/AWS-Mumbai%20Region-FF9900?style=for-the-badge&logo=amazon-aws)
![Compliance](https://img.shields.io/badge/RBI%20%7C%20DPDP%20%7C%20CERT--In-Compliant%20Architecture-red?style=for-the-badge)

---

**Built by [Arka](https://github.com/junaidjmomin)**

</div>

---

## 📌 Table of Contents

- [The Problem](#-the-problem)
- [What Is Third Eye](#-what-is-third-eye)
- [Who It's Built For](#-who-its-built-for)
- [Core Capabilities](#-core-capabilities)
- [Risk Intelligence Architecture](#-risk-intelligence-architecture)
- [Risk Scoring Model](#-risk-scoring-model)
- [The Command Dashboard](#-the-command-dashboard)
- [User Roles & Access](#-user-roles--access)
- [Workflow Engine](#-workflow-engine)
- [Regulatory Compliance Layer](#-regulatory-compliance-layer)
- [Technical Architecture](#-technical-architecture)
- [Tech Stack](#-tech-stack)
- [Data Sources](#-data-sources)
- [Integrations](#-integrations)
- [Security & Compliance Controls](#-security--compliance-controls)
- [Deployment Model](#-deployment-model)
- [Consortium Intelligence Network](#-consortium-intelligence-network)
- [Product Roadmap](#-product-roadmap)
- [Getting Started](#-getting-started)
- [Contributing](#-contributing)

---

# 🔴 THE PROBLEM

## Vendor Risk Management in Indian Banking Is Broken at the Foundation

Indian banks today manage **300–500+ third-party vendors** simultaneously — core banking platform providers, payment switch operators, KYC bureaus, fintech API partners, cloud infrastructure vendors, ATM operators, SOC outsourcers, and more. Every single one is a potential liability sitting inside the bank's operational perimeter.

### The Industry Reality

| What Exists Today | What Actually Happens |
|---|---|
| Annual vendor audits | A vendor that passed SOC 2 in January can be breached by March |
| Vendor inventory spreadsheets | 6–12 copies across IT, procurement, compliance, and business units — none synchronized |
| Onboarding questionnaires | Done once at onboarding. Never revisited. Risk posture between cycles: unknown |
| Manual compliance reporting | 40+ person-hours per RBI audit cycle, assembled from scattered sources |
| Incident notification clauses | Contracts say "promptly." No defined timeline. No enforcement mechanism |

### Real Incidents That Define the Stakes

> 🔴 **HDFC Third-Party Breach (2023)** — Nearly 6 lakh customer records, including names, email addresses, mobile numbers, and loan details, surfaced on a dark web forum — sourced not from HDFC's core systems, but from an external service provider. The bank's core was clean. The damage was done anyway.

> 🔴 **Hitachi Payment Services Breach (2016)** — 3.2 million debit cards compromised across SBI, HDFC, ICICI, Yes Bank, and Axis Bank. Detection lag: six weeks. Discovery source: foreign banks reporting fraudulent usage in China and the United States — not the vendor, not the bank.

> ⚖️ **DPDP Act 2023** — Vendor-originated data breaches now expose banks to penalties up to ₹200 crore. The bank is liable for what its vendor does with customer data.

> ⏱️ **CERT-In 6-Hour Reporting Clock** — Starts ticking the moment a cyber incident is *detected* — regardless of whether your vendor has told you yet.

### The Root Cause

Banks have vendor risk management **processes**. They do not have vendor risk management **capability**.

The process generates paperwork. The capability generates decisions. The gap between those two things is where breaches, regulatory penalties, and SLA failures live.

> *"You only learn a vendor is a problem after it has become a crisis."*

---

# 👁 WHAT IS THIRD EYE

**Third Eye is a Real-Time Vendor Risk Command Center** — an AI-powered risk intelligence layer that sits on top of a bank's existing GRC infrastructure and transforms static vendor risk programs into continuous, intelligent, regulatory-grade risk operations.

It is not a replacement for ServiceNow, RSA Archer, or MetricStream.  
It is the **AI brain** layered over them.

```
Third Eye transforms static vendor risk programs into real-time risk intelligence systems.
```

### What Third Eye Does

```
External Signals ──────────────────────────────────────────────────────────┐
 (News, Dark Web, Threat Intel, Financial Data, Regulatory Filings)         │
                                                                             ▼
Internal Signals ─────────────────────────────────────► [ Third Eye AI Engine ]
 (SLA Data, Audit Findings, Contract Metadata, Incident History)            │
                                                                             │
                                    ┌────────────────────────────────────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │  LLM Signal Parser   │  ← Reads unstructured news,
                         │  (Unstructured Intel)│    dark web text, notices
                         └─────────┬───────────┘
                                   │
                                   ▼
                         ┌─────────────────────┐
                         │  ML Scoring Engine   │  ← Predicts risk trajectory,
                         │  (Predictive Risk)   │    composite score generation
                         └─────────┬───────────┘
                                   │
                                   ▼
                         ┌─────────────────────┐
                         │  Rule-Based Engine   │  ← RBI/DPDP/CERT-In thresholds,
                         │  (Regulatory Brain)  │    deterministic compliance logic
                         └─────────┬───────────┘
                                   │
                         ┌─────────▼───────────┐
                         │  Risk Score + Band   │
                         │  Alert + Recommend   │
                         │  Workflow Assignment  │
                         │  Audit Trail Entry   │
                         └─────────┬───────────┘
                                   │
                                   ▼
                         ┌─────────────────────┐
                         │  ⛓️ On-Chain Agent   │  ← Autonomous DLT agent
                         │  Consortium Layer    │    broadcasts anonymized
                         │  Hyperledger Fabric  │    risk signals to all
                         └─────────────────────┘    consortium banks instantly
```

---

# 🏦 WHO IT'S BUILT FOR

Third Eye is purpose-built for **Indian banks and financial institutions** operating under:

| Regulatory Body | Key Obligation |
|---|---|
| **Reserve Bank of India (RBI)** | IT Outsourcing Master Directions 2023 — Board-level oversight, continuous monitoring, concentration risk management |
| **CERT-In** | 6-hour cyber incident reporting window |
| **DPDP Act 2023** | ₹200 crore penalty surface for vendor-originated data breaches |
| **RBI Cybersecurity Framework** | SOC requirements, security posture monitoring |
| **MCA / SEBI** | Regulatory filing and enforcement monitoring |

### Primary Institutions

- Public Sector Banks (SBI, Bank of Baroda, Union Bank of India)
- Private Sector Banks (HDFC Bank, ICICI Bank, Axis Bank, Kotak)
- NBFCs and Payment Banks
- Insurance and Capital Markets firms under similar regulatory pressure

---

# ⚙️ CORE CAPABILITIES

## 1. 🔴 Live Risk Command Dashboard
The primary entry point. A Bloomberg Terminal for third-party risk.

- Real-time vendor risk posture across all active vendors
- Color-coded risk band indicators (Critical / High / Watch / Stable)
- Regulatory exposure meter — live RBI / DPDP impact surface
- 6-hour incident clock tracker — auto-activates when a critical event is detected
- Aggregate risk posture trend vs last 7 / 30 / 90 days
- Material risk shift feed — vendors whose scores moved significantly since last session

## 2. 🧠 AI-Powered Continuous Monitoring
Third Eye watches your vendors 24/7 across 9 risk dimensions — so you don't have to.

## 3. 📊 Composite + Category Risk Scoring
Every vendor carries a live, explainable risk score updated as signals arrive.

## 4. 🚨 Intelligent Alerting
Alerts routed by risk band, role, and regulatory urgency — not noise, not email blasts.

## 5. ✅ Mitigation Workflow Engine
From detection to resolution — assigned, tracked, closed, and audit-trailed automatically.

## 6. 📋 RBI-Ready Reporting
One-click regulatory export — Board papers, RBI submissions, audit packages.

## 7. 🔌 GRC Integration Layer
Plugs into existing bank infrastructure — not a replacement, a force multiplier.

## 8. ⛓️ Autonomous On-Chain Risk Agents *(Phase 3)*
A permissioned inter-bank DLT network where autonomous agents share anonymized vendor risk signals across consortium banks in real time — built on Hyperledger Fabric, supervised by RBI-compatible governance. When one bank's Third Eye detects a critical vendor event, every consortium member knows within minutes. Automatically.

---

# 🧩 RISK INTELLIGENCE ARCHITECTURE

## 9-Dimension Risk Framework

Third Eye scores every vendor across nine risk dimensions, structured in three tiers of depth and priority.

---

### 🔴 Tier 1 — Core Engine (Live at Launch)
*Primary drivers of the composite risk score. Non-negotiable for bank credibility.*

| Dimension | What Third Eye Monitors | Key Signal Sources |
|---|---|---|
| **1. Cybersecurity Posture** | Breaches, CVEs, dark web leaks, credential dumps, security rating changes | BitSight, SecurityScorecard, CERT-In, NVD/CVE, dark web feeds |
| **2. Regulatory Compliance** | RBI outsourcing violations, DPDP exposure, CERT-In non-compliance, penalty actions | RBI enforcement DB, MCA21, SEBI, regulatory news feeds |
| **3. Operational Resilience** | SLA breach history, uptime degradation, incident frequency, response time trends | ServiceNow, GRC tools, internal ITSM data |
| **4. Negative News & Legal** | Litigation, sanctions, enforcement actions, leadership changes, negative press | News APIs, court filings, regulatory announcements, media feeds |

---

### 🟡 Tier 2 — Intelligence Layer (Phase 2)
*Differentiators that make Third Eye defensible against competitors.*

| Dimension | What Third Eye Monitors | Key Signal Sources |
|---|---|---|
| **5. Financial Health** | Credit rating changes, liquidity stress, MCA filing anomalies, balance sheet signals | Credit bureaus, MCA21, financial news, company filings |
| **6. Data Privacy Posture** | DPDP compliance posture, data handling practices, privacy incident history | DPDP regulatory guidance, privacy audit data |
| **7. Concentration Risk** | Over-dependence on single vendors, shared infrastructure exposure, sector-level systemic signals | Internal vendor inventory, RBI concentration advisories |

---

### 🔵 Tier 3 — Moat Builders (Phase 3)
*Long-term competitive moat. Nobody in Indian banking is doing this well.*

| Dimension | What Third Eye Monitors |
|---|---|
| **8. ESG Risk** | Environmental, social, and governance signals — emerging regulatory and investor-driven pressure |
| **9. Fourth-Party Exposure** | Vendor's vendor risk — recursive dependency mapping using graph modeling to detect systemic supply chain failures |

---

# 📊 RISK SCORING MODEL

## Architecture: Category → Composite → Band → Action

```
┌──────────────────────────────────────────────────────────────────────┐
│                    VENDOR: Acme Payments Ltd.                        │
├─────────────────────┬────────────────────────────────────────────────┤
│  CATEGORY SCORES    │  COMPOSITE SCORE                               │
│                     │                                                │
│  Cybersecurity  28  │         ┌─────────────┐                        │
│  Regulatory     61  │         │     34      │  ← Composite (0–100)  │
│  Operational    70  │         └──────┬──────┘                        │
│  News/Legal     55  │                │                               │
│  Financial      80  │         ┌──────▼──────┐                        │
│  Data Privacy   72  │         │  🔴 HIGH    │  ← Risk Band          │
│  Concentration  65  │         │    RISK     │                        │
│                     │         └──────┬──────┘                        │
│  Last week: 61  ▼   │                │                               │
│  This week: 34  📉  │    Escalate to CISO + CRO                      │
└─────────────────────┴────────────────────────────────────────────────┘
```

## Risk Band → Action Mapping

| Band | Composite Score | Color | Action Triggered |
|---|---|---|---|
| 🟢 **Stable** | 75 – 100 | Green | Routine monitoring, no action required |
| 🟡 **Watch** | 50 – 74 | Yellow | Notify vendor risk team, log signal |
| 🔴 **High Risk** | 25 – 49 | Red | Escalate to CISO + CRO, initiate review |
| ⚫ **Critical** | 0 – 24 | Black | Activate 6-hour clock, Board-level alert, workflow triggered |

## Score Transparency Principle

Every score movement in Third Eye is **fully explainable**:

```
Score Change: 61 → 34  |  Vendor: Acme Payments  |  Timestamp: 2024-03-04 03:17 IST
Trigger: Dark web mention detected (credential dump, 12,400 records)
Dimension Affected: Cybersecurity Posture (70 → 28)
Model: LLM Signal Parser → ML Scoring Engine
Rule Activated: CERT-In Incident Reporting Threshold
Recommended Action: Initiate vendor notification, assess data scope, prepare RBI report
Assigned To: [CISO Queue]
Audit Log Entry: #AUD-2024-7821
```

---

# 🖥️ THE COMMAND DASHBOARD

> *Designed for a CTO at SBI or HDFC opening Third Eye on Monday morning and asking one question: "Where am I exposed right now?"*

```
╔══════════════════════════════════════════════════════════════════════════════╗
║  👁 THIRD EYE  |  Risk Command Center          Mon, 04 Mar 2024  09:04 IST  ║
╠════════════════╦═════════════════════════════════════════════════════════════╣
║  RISK POSTURE  ║  ACTIVE VENDORS: 347   ⚫ CRITICAL: 2   🔴 HIGH: 11        ║
║  SCORE: 58 ▼  ║  🟡 WATCH: 34         🟢 STABLE: 300                       ║
║  (-6 vs last  ║                                                              ║
║   week)       ║  ⏱ 6-HOUR CLOCK ACTIVE  |  Vendor: Acme Payments  02:14:33 ║
╠════════════════╩═════════════════════════════════════════════════════════════╣
║  CRITICAL VENDORS           SCORE   CHANGE   TRIGGER                        ║
║  ─────────────────────────────────────────────────────────────────────────  ║
║  ⚫ Acme Payments Ltd.         34    ▼ -27   Dark web credential dump       ║
║  ⚫ TechServe Infrastructure   21    ▼ -41   RBI enforcement action filed   ║
║  🔴 DataBridge Analytics       43    ▼ -18   Financial stress: MCA filing   ║
║  🔴 CloudSec Systems           47    ▼ -14   CVE-2024-1187 unpatched        ║
╠═════════════════════════════════════════════════════════════════════════════╣
║  REGULATORY EXPOSURE METER                                                  ║
║  RBI Outsourcing  ████████░░░░  67%   |  DPDP Surface   ██████░░░░  58%   ║
║  CERT-In Ready    █████░░░░░░░  48%   |  Audit Coverage ████████░░  79%   ║
╚═════════════════════════════════════════════════════════════════════════════╝
```

---

# 👥 USER ROLES & ACCESS

Third Eye uses **role-based access control (RBAC)** — one platform, multiple intelligent lenses.

| Role | Primary View | Key Features |
|---|---|---|
| **CTO / CRO** | Aggregate risk posture, Board summary, trend analysis | Executive dashboard, one-click Board reports |
| **CISO** | Cybersecurity dimension deep-dive, CERT-In clock, dark web alerts | Threat intel feed, CVE tracker, incident timeline |
| **Compliance Officer** | RBI/DPDP regulatory exposure, compliance gaps, penalty surface | Rule engine status, one-click RBI export, DPDP reporting |
| **Internal Audit** | Historical risk timeline per vendor, evidence packages, findings log | Immutable audit trail, score change history, AI recommendation log |
| **Vendor Risk / Procurement** | Per-vendor scorecards, onboarding risk tiering, contract flags | Onboarding workflow, contract metadata tracker, renewal alerts |
| **Business Unit Head** | Only their assigned vendors, SLA performance, operational risk | Filtered vendor view, SLA breach alerts |

---

# 🔄 WORKFLOW ENGINE

## Alert → Assign → Track → Resolve → Archive

When Third Eye detects a material risk shift, it doesn't just alert — it **manages the response**:

```
┌─────────────────────────────────────────────────────────────────────────┐
│  DETECTION                                                              │
│  LLM detects signal → ML scores impact → Rule engine classifies        │
│                              │                                          │
│                              ▼                                          │
│  ALERT                                                                  │
│  Routed to correct stakeholder based on risk type + severity           │
│  (CISO for cyber, Compliance for regulatory, CRO for financial)        │
│                              │                                          │
│                              ▼                                          │
│  RECOMMENDATION                                                         │
│  AI generates mitigation recommendation with reasoning + evidence      │
│                              │                                          │
│                              ▼                                          │
│  ASSIGNMENT                                                             │
│  Issue assigned to owner with deadline, priority, and context          │
│                              │                                          │
│                              ▼                                          │
│  RESOLUTION TRACKING                                                    │
│  Owner logs actions taken, Third Eye tracks status in real-time        │
│                              │                                          │
│                              ▼                                          │
│  AUDIT TRAIL ENTRY (Immutable)                                          │
│  Full record: who detected, who was alerted, what was recommended,     │
│  who acted, what was done, when it was resolved                        │
└─────────────────────────────────────────────────────────────────────────┘
```

---

# ⚖️ REGULATORY COMPLIANCE LAYER

## Built for the Indian Regulatory Stack

Third Eye's rule engine is architected as a **Policy-as-Code framework** — compliance rules are version-controlled, traceable, and auditable. Banks cannot afford AI that says "probably non-compliant." Rules are deterministic. Every compliance flag has a regulatory citation.

| Regulation | What Third Eye Enforces |
|---|---|
| **RBI IT Outsourcing Directions 2023** | Vendor inventory completeness, material outsourcing classification, Board reporting triggers, right-to-audit clause monitoring |
| **CERT-In Directions** | 6-hour incident reporting clock — auto-activates on Critical band trigger |
| **DPDP Act 2023** | Data breach notification obligations, PII vendor exposure mapping, ₹200Cr penalty surface tracking |
| **RBI Cybersecurity Framework** | Security posture thresholds, SOC compliance status |
| **SEBI / MCA21** | Regulatory filing anomaly detection, enforcement action monitoring |

### One-Click RBI Export Mode

Every regulatory report in Third Eye is machine-generated and human-verified:

- Vendor risk summary (Board paper format)
- Material outsourcing arrangement register
- Incident timeline with evidence
- Concentration risk assessment
- Audit findings log with remediation status

---

# 🏗️ TECHNICAL ARCHITECTURE

## System Architecture Overview

```
╔══════════════════════════════════════════════════════════════════════════════╗
║                        THIRD EYE — SYSTEM ARCHITECTURE                     ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                              ║
║   EXTERNAL DATA LAYER (Outside Bank Perimeter)                              ║
║   ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐         ║
║   │  News &  │ │   Dark   │ │ Security │ │Financial │ │Regulatory│         ║
║   │  Media   │ │   Web    │ │ Ratings  │ │  Health  │ │ Filings  │         ║
║   │  Feeds   │ │ Monitor  │ │ (BitSight│ │ (MCA21)  │ │ (RBI/SEBI│         ║
║   └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘         ║
║        └────────────┴────────────┴─────────────┴────────────┘               ║
║                                  │                                           ║
║                    [ Encrypted Ingestion Pipeline ]                          ║
║                          Apache Kafka Streams                                ║
║                                  │                                           ║
╠══════════════════════════════════╪═══════════════════════════════════════════╣
║   INSIDE BANK PERIMETER          │                                           ║
║                                  ▼                                           ║
║   INTERNAL DATA LAYER                                                        ║
║   ┌──────────┐ ┌──────────┐ ┌──────────┐                                    ║
║   │ GRC/ITSM │ │  Audit   │ │ Contract │                                    ║
║   │(ServiceNow│ │Findings &│ │ Metadata │                                    ║
║   │ /Archer) │ │Incidents │ │ & SLAs   │                                    ║
║   └────┬─────┘ └────┬─────┘ └────┬─────┘                                    ║
║        └────────────┴────────────┘                                           ║
║                      │                                                       ║
║                       ▼                                                      ║
║            ┌─────────────────────┐                                           ║
║            │   AI ENGINE CORE    │                                           ║
║            │                     │                                           ║
║            │  ① LLM Layer        │  ← OpenAI / Anthropic / Azure (pluggable)║
║            │    (Signal Parsing) │                                           ║
║            │                     │                                           ║
║            │  ② ML Layer         │  ← scikit-learn + XGBoost                ║
║            │    (Risk Scoring)   │                                           ║
║            │                     │                                           ║
║            │  ③ Rule Engine      │  ← Policy-as-Code (RBI/DPDP/CERT-In)    ║
║            │    (Compliance)     │                                           ║
║            └─────────┬───────────┘                                           ║
║                      │                                                       ║
║            ┌─────────▼───────────┐                                           ║
║            │  PostgreSQL (Core)  │                                           ║
║            │  Weaviate (Vector)  │                                           ║
║            │  Redis (Cache)      │                                           ║
║            └─────────┬───────────┘                                           ║
║                      │                                                       ║
║            ┌─────────▼───────────┐                                           ║
║            │   FastAPI Backend   │                                           ║
║            │   (Python 3.11+)    │                                           ║
║            └─────────┬───────────┘                                           ║
║                      │                                                       ║
║            ┌─────────▼───────────┐                                           ║
║            │  ⛓️ On-Chain Agents  │  ← Hyperledger Fabric nodes              ║
║            │  Consortium Network │    Autonomous signal broadcast            ║
║            │  (Permissioned DLT) │    Inter-bank anonymized risk sharing     ║
║            └─────────┬───────────┘                                           ║
║                      │                                                       ║
║            ┌─────────▼───────────┐                                           ║
║            │  React + TypeScript │                                           ║
║            │  Risk Command Center│                                           ║
║            └─────────────────────┘                                           ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

---

# 🛠️ TECH STACK

## Backend

| Layer | Technology | Rationale |
|---|---|---|
| **Core API** | Python 3.11+ + FastAPI | Async-friendly, clean architecture, native ML integration |
| **LLM Layer** | Pluggable Abstraction (OpenAI / Anthropic / Azure OpenAI) | Banks may refuse public API calls — provider must be swappable |
| **ML Scoring** | scikit-learn + XGBoost | Explainable, auditable, proven in financial risk modeling |
| **Rule Engine** | Policy-as-Code (Python, version-controlled) | Deterministic compliance — RBI auditors need traceable logic |
| **Task Queue** | Celery + Redis | Async monitoring jobs; Kafka integration in Phase 2 |
| **Event Streaming** | Apache Kafka | Real-time signal ingestion from external sources |
| **Workflow Engine** | Temporal.io (Phase 2) | Durable workflow orchestration for risk response lifecycle |
| **On-Chain Agents** | Hyperledger Fabric (Phase 3) | Permissioned DLT — autonomous inter-bank risk signal broadcasting, RBI-compatible consortium governance |

## Data & Storage

| Layer | Technology | Rationale |
|---|---|---|
| **Primary Database** | PostgreSQL | JSONB support, reliability, financial-grade ACID compliance |
| **Vector Database** | Weaviate (self-hostable) | On-prem compatible — banks need data control; Pinecone is SaaS-only |
| **Cache** | Redis | Sub-millisecond latency for dashboard real-time updates |

## Frontend

| Layer | Technology | Rationale |
|---|---|---|
| **Framework** | React 18 + TypeScript | Type-safe, enterprise-grade, large talent pool in India |
| **UI Components** | Tailwind CSS + shadcn/ui | Clean, token-based enterprise design system |
| **Data Visualization** | Recharts (Phase 1), D3.js (Phase 3 graph modeling) | Recharts for dashboard; D3 reserved for fourth-party graph UI |

## Infrastructure

| Layer | Technology | Rationale |
|---|---|---|
| **Cloud** | AWS ap-south-1 (Mumbai) | RBI data residency compliance — data must stay in India |
| **Containerization** | Docker + Kubernetes | Mandatory for an Operating System-grade product |
| **CI/CD** | GitHub Actions (self-hosted runners for bank deployments) | Enterprise banks require internal runner control |
| **VPC** | Dedicated VPC per bank tenant | No cross-tenant data leakage, private endpoints only |

---

# 🔌 DATA SOURCES

## External Sources

| Category | Sources |
|---|---|
| **News & Media** | Google News API, RSS feeds, regulatory press releases, Economic Times, Mint |
| **Dark Web Monitoring** | Breach databases, paste site monitoring, credential dump trackers, hacker forum signals |
| **Security Ratings** | BitSight, SecurityScorecard |
| **Financial Health** | MCA21 filings, credit bureau signals, liquidity stress indicators, balance sheet feeds |
| **Regulatory Filings** | RBI enforcement database, SEBI penalty records, MCA21 company filings |
| **Threat Intelligence** | CVE / NVD databases, CERT-In advisories, MITRE ATT&CK framework feeds |

## Internal Sources

| Category | Sources |
|---|---|
| **SLA Performance** | ServiceNow, GRC tools, ITSM ticketing data |
| **Audit & Incident History** | Internal audit management systems, past incident records |
| **Contract Metadata** | Right-to-audit clauses, data sharing scope, renewal windows, PII handling classifications |

---

# 🔗 INTEGRATIONS

## GRC / ITSM
- ServiceNow
- RSA Archer
- MetricStream

## Communication & Alerting
- Microsoft Teams
- Slack
- Email (SMTP)

## Security & Threat Intelligence
- BitSight
- SecurityScorecard
- CERT-In advisory feeds
- CVE / NVD databases

## Regulatory Data
- MCA21 filings API
- RBI enforcement database
- SEBI penalty records

## Identity & Access Management
- LDAP / Active Directory (standard in Indian banking infrastructure)
- SAML / SSO

---

# 🔒 SECURITY & COMPLIANCE CONTROLS

Every control below is **mandatory architecture** — not optional configuration.

| Control | Implementation | Regulatory Basis |
|---|---|---|
| 🔒 **Encryption at rest + in transit** | AES-256 at rest, TLS 1.3 in transit | RBI Cybersecurity Framework, DPDP Act |
| 👤 **Role-Based Access Control (RBAC)** | Granular role definitions, vendor-scoped access, audit-segregated views | RBI IT Governance Directions |
| 📜 **Immutable Audit Logs** | Append-only log store — every action, every timestamp, every actor | RBI examiner requirements, internal audit standards |
| 📊 **Risk Score Change Traceability** | Every score movement carries: trigger signal, model version, timestamp, reason code | AI auditability, regulator defensibility |
| 🤖 **AI Recommendation Logging** | Every AI output logged with input signals, model version, confidence level | Explainable AI for regulated environments |
| 📋 **Regulator Export Mode** | One-click RBI-ready report generation — Board paper, audit package, incident timeline | RBI IT Outsourcing Directions 2023, CERT-In |

### Audit Trail Principle

```
Every action in Third Eye generates an immutable log entry:

WHO → did WHAT → to WHICH VENDOR → at WHEN → triggered by WHAT SIGNAL → model VERSION
```

Banks cannot act on AI output they cannot explain to a regulator.  
Third Eye makes every recommendation **auditable, traceable, and defensible.**

---

# 🚀 DEPLOYMENT MODEL

## Hybrid Architecture — The Only Correct Model for Indian Banks

Given RBI data residency requirements, CERT-In logging obligations, and DPDP Act penalties — Third Eye is deployed as a **hybrid system**.

```
┌─────────────────────────────────────────────────────────────┐
│               INSIDE BANK PERIMETER                          │
│                                                             │
│  ✅ Vendor master data         ✅ Risk scoring engine        │
│  ✅ SLA & contract metadata    ✅ Compliance rule engine     │
│  ✅ Audit trail & logs         ✅ All customer-linked data   │
│                                                             │
└──────────────────────────┬──────────────────────────────────┘
                           │  Encrypted Ingestion Only
                           │  (No raw data leaves perimeter)
┌──────────────────────────▼──────────────────────────────────┐
│               EXTERNAL ENRICHMENT LAYER                      │
│                                                             │
│  ✅ Dark web monitoring        ✅ News & media signals       │
│  ✅ Public regulatory data     ✅ Threat intelligence feeds  │
│  ✅ Financial health signals   ✅ Security rating data       │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

**Deployment options:**
- `On-premises` — full deployment inside bank infrastructure
- `Private Cloud` — dedicated AWS VPC per bank, Mumbai region (ap-south-1)
- `Hybrid` *(recommended)* — sensitive data on-prem, enrichment in isolated cloud

---

# ⛓️ CONSORTIUM INTELLIGENCE NETWORK

## Autonomous On-Chain Risk Agents — The Network Effect That Changes Indian Banking

Indian banks share **60–70% of the same vendor pool.** The same core banking platforms. The same payment switches. The same KYC bureaus. The same cloud infrastructure. When a vendor is breached, it is never one bank's problem — it is every bank's problem simultaneously.

Today, each bank finds out independently. At different times. With different detection lag. That asymmetry is a systemic vulnerability.

**Third Eye's Consortium Intelligence Network eliminates that asymmetry.**

---

### How It Works

```
┌──────────────────────────────────────────────────────────────────────────┐
│              THIRD EYE CONSORTIUM INTELLIGENCE NETWORK                   │
│                   (Permissioned DLT — Hyperledger Fabric)                │
│                                                                          │
│   ┌─────────────┐     ┌─────────────┐     ┌─────────────┐               │
│   │  SBI Node   │     │  HDFC Node  │     │  ICICI Node │               │
│   │  ⛓️ Agent   │     │  ⛓️ Agent   │     │  ⛓️ Agent   │               │
│   └──────┬──────┘     └──────┬──────┘     └──────┬──────┘               │
│          └──────────────────┬┴────────────────────┘                      │
│                             │                                            │
│                  ┌──────────▼──────────┐                                 │
│                  │  Shared Ledger      │                                 │
│                  │  (Anonymized Only)  │                                 │
│                  └──────────┬──────────┘                                 │
│                             │                                            │
│        What autonomous agents broadcast (anonymized):                    │
│        ✅ Vendor risk score threshold breach events                      │
│        ✅ Confirmed breach signals (post-public-disclosure)              │
│        ✅ Regulatory enforcement actions (already public record)         │
│        ✅ CERT-In advisory correlation signals                           │
│                                                                          │
│        What NEVER leaves a bank's perimeter:                             │
│        ❌ Raw SLA performance data                                        │
│        ❌ Contract terms or commercial metadata                          │
│        ❌ Internal audit findings                                         │
│        ❌ Any customer-linked data of any kind                           │
└──────────────────────────────────────────────────────────────────────────┘
```

---

### The Autonomous Agent Architecture

Each bank's Third Eye instance runs a **dedicated on-chain agent** — a permissioned node on the Hyperledger Fabric consortium network. These agents act autonomously within pre-defined governance rules:

```
TRIGGER:  Third Eye ML engine scores Vendor X as Critical (score drops below 24)
                              │
                              ▼
AGENT DECISION:  Does this event meet consortium broadcast criteria?
                 (Severity threshold + Signal type + Disclosure policy check)
                              │
                   ┌──────────┴──────────┐
                   │  YES — Broadcast    │
                   └──────────┬──────────┘
                              │
                              ▼
ANONYMIZED SIGNAL WRITTEN TO SHARED LEDGER:
  {
    vendor_hash:       "sha256:a3f9...",   ← Vendor identity hashed
    signal_type:       "CRITICAL_BREACH",
    risk_dimension:    "CYBERSECURITY",
    severity:          "CRITICAL",
    source_bank:       "REDACTED",         ← Bank identity never exposed
    timestamp:         "2024-03-04T03:17Z",
    cert_in_relevant:  true,
    recommended_action: "INITIATE_6HR_CLOCK"
  }
                              │
                              ▼
ALL CONSORTIUM MEMBERS' THIRD EYE INSTANCES:
  → Auto-update affected vendor's risk score
  → Trigger internal alert workflow
  → Activate 6-hour CERT-In clock if applicable
  → Log consortium signal in immutable audit trail
```

---

### Why Permissioned DLT — Not Public Blockchain

| Approach | RBI Stance | Third Eye Decision |
|---|---|---|
| Public blockchain (Ethereum, Solana) | ❌ Hostile — no governing body, anonymity risk | Rejected |
| DeFi / DAO governance | ❌ Explicitly flagged by RBI Governor | Rejected |
| Permissioned consortium DLT (Hyperledger Fabric) | ✅ Aligned with RBI's own DLT pilots and Innovation Hub whitepaper | **Selected** |

Hyperledger Fabric gives Third Eye:
- **Identity-permissioned nodes** — only verified bank participants can join
- **Private data channels** — granular control over what each node sees
- **No cryptocurrency** — pure enterprise DLT, zero speculative asset exposure
- **RBI audit compatibility** — the regulator can be given observer node access

---

### The Network Effect

```
1 bank on Third Eye    →  Powerful single-institution risk intelligence
5 banks on Third Eye   →  Early warning network across ₹40L Cr+ in vendor exposure
15 banks on Third Eye  →  De facto standard for Indian banking vendor risk
                          RBI has a real-time systemic vendor risk view
                          Third Eye becomes irreplaceable infrastructure
```

> *This is not a feature. This is an industry utility — the kind regulators eventually mandate.*

---

## Phase 1 — Foundation (MVP)
> *Prove the core value. Win the first bank.*

- [ ] Live Risk Command Dashboard
- [ ] Tier 1 risk dimensions (Cybersecurity, Regulatory, Operational, News/Legal)
- [ ] Composite score + category scores + risk bands
- [ ] LLM signal parsing (news, dark web, regulatory notices)
- [ ] ML risk scoring engine (scikit-learn + XGBoost)
- [ ] Policy-as-Code rule engine (RBI, CERT-In, DPDP)
- [ ] Alert + Recommendation + Workflow assignment
- [ ] RBAC with 6 role profiles
- [ ] ServiceNow + RSA Archer integration
- [ ] RBI-ready one-click export
- [ ] Immutable audit trail
- [ ] AWS Mumbai hybrid deployment

## Phase 2 — Intelligence Layer
> *Make Third Eye defensible against competitors.*

- [ ] Financial health monitoring (MCA21, credit signals)
- [ ] Data privacy posture scoring (DPDP-specific)
- [ ] Concentration risk analysis
- [ ] Kafka-based real-time streaming pipeline
- [ ] Temporal.io workflow orchestration
- [ ] LightGBM upgrade for ML scoring
- [ ] Vendor onboarding risk tiering workflow
- [ ] Full GRC integration suite (MetricStream, full ServiceNow API)
- [ ] ESG risk signals (early signals)

## Phase 3 — Moat Builders
> *The features that make Third Eye impossible to replace.*

- [ ] **Fourth-Party Intelligence Engine** — Recursive vendor dependency mapping using graph modeling. Detects systemic concentration risk across the Indian banking supply chain. When your vendor's vendor fails — Third Eye sees it first.
- [ ] D3.js-powered vendor dependency graph visualization
- [ ] Sector-level systemic risk aggregation across multiple bank clients
- [ ] Predictive vendor failure modeling (12-month horizon)
- [ ] AI-generated monthly executive risk briefings (narrative format)
- [ ] DPDP full enforcement readiness suite
- [ ] **⛓️ Consortium Intelligence Network** — Permissioned Hyperledger Fabric consortium network with autonomous on-chain agents per bank node. Anonymized vendor risk signals broadcast automatically across member banks. When one bank's Third Eye detects a critical event — every consortium member knows within minutes, autonomously.
- [ ] Autonomous agent governance framework (broadcast rules, signal criteria, consent model)
- [ ] RBI observer node integration — regulator-compatible systemic risk view
- [ ] Consortium onboarding SDK for new bank members
- [ ] Network effect dashboard — aggregate sector-level vendor risk posture across all consortium banks

---

# ⚡ GETTING STARTED

## Prerequisites

```bash
# Required
Python 3.11+
Node.js 18+
Docker + Docker Compose
PostgreSQL 15+
Redis 7+
```

## Quick Start

```bash
# Clone repository
git clone https://github.com/junaidjmomin/third-eye.git
cd third-eye

# Set up environment
cp .env.example .env
# Configure your LLM provider, DB credentials, and API keys in .env

# Start all services
docker-compose up -d

# Run database migrations
python manage.py migrate

# Start the backend
uvicorn app.main:app --reload --port 8000

# Start the frontend
cd frontend
npm install
npm run dev
```

## Environment Configuration

```env
# LLM Provider (pluggable — choose one)
LLM_PROVIDER=openai           # or: anthropic | azure_openai
OPENAI_API_KEY=your_key_here

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/thirdeye
REDIS_URL=redis://localhost:6379

# Vector Database
WEAVIATE_URL=http://localhost:8080

# AWS Configuration (Mumbai Region)
AWS_REGION=ap-south-1
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret

# Security
SECRET_KEY=your_secret_key
ENCRYPTION_KEY=your_aes_256_key

# On-Chain Consortium (Phase 3)
FABRIC_NETWORK_ENABLED=false         # set true when joining consortium
FABRIC_PEER_ENDPOINT=grpcs://peer0.bank.thirdeye.network:7051
FABRIC_CHANNEL_NAME=vendor-risk-consortium
FABRIC_CHAINCODE_NAME=risk-agent
```

---

# 🤝 CONTRIBUTING

Third Eye is built to solve a real problem that affects the financial security of millions of Indians.  
If you're working on vendor risk, bank compliance, AI, or financial infrastructure — contributions are welcome.

```bash
# Development workflow
git checkout -b feature/your-feature-name
# Make your changes
git commit -m "feat: your descriptive commit message"
git push origin feature/your-feature-name
# Open a Pull Request
```

Please read `CONTRIBUTING.md` for code standards, testing requirements, and architecture guidelines.

---

## 📄 License

MIT License — see `LICENSE` for details.

---

<div align="center">

---

**👁 THIRD EYE**

*Your Risk Is Our Risk.*

Built with intent by **[Arka](https://github.com/junaidjmomin)**

*For the banks that cannot afford to be reactive.*

---

</div>