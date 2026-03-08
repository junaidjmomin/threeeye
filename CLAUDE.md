# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Third Eye** is an AI-powered vendor risk intelligence platform for Indian banks and financial institutions. It monitors third-party vendor risk continuously across 9 dimensions with compliance enforcement for RBI, CERT-In, and DPDP Act regulations.

**Repositories:**
- This repo (`Threeeye`) — product spec (`readme.md`) and prototype frontend (`third-eye-app/`)
- **Production frontend:** `https://github.com/junaidjmomin/vendor-guardian.git` — the active, full-featured React app

---

## Frontend (vendor-guardian) — Development Commands

```bash
npm run dev          # Start dev server on port 8080 (Vite + SWC)
npm run build        # Production build (vite build)
npm run build:dev    # Dev-mode production build
npm run lint         # ESLint
npm run preview      # Preview production build
npm run test         # Run tests once (Vitest + jsdom)
npm run test:watch   # Run tests in watch mode
```

**Path alias:** `@/` maps to `src/` — always use `@/` for imports.

---

## Architecture

**Stack:** React 18, TypeScript, Vite (SWC), Tailwind CSS, shadcn/ui (Radix), Framer Motion, D3.js, React Three Fiber, TanStack Query, React Router v6, Zod, React Hook Form

### Routing & Shell

`App.tsx` handles two modes:
- `/` → `LandingPage` (full-screen marketing page, no shell)
- All other routes → `AppShell` (sidebar + top bar layout)

`AppShell` composes `AppSidebar` + `TopBar` + `AppRoutes`. Page transitions use `AnimatePresence` from Framer Motion.

### Page Routes

| Route | Page | Description |
|---|---|---|
| `/dashboard` | `Dashboard` | Risk Command Center — primary view |
| `/vendors` | `VendorRegistry` | Full vendor list with filters |
| `/vendors/:id` | `VendorDetail` | Per-vendor scorecard and drill-down |
| `/alerts` | `AlertsPage` | Alert feed and triage |
| `/workflows` | `WorkflowsPage` | Mitigation workflow tracking |
| `/compliance` | `CompliancePage` | RBI/CERT-In/DPDP compliance status |
| `/reports` | `ReportsPage` | RBI-ready report generation |
| `/consortium` | `ConsortiumPage` | DLT inter-bank network view |
| `/settings` | `SettingsPage` | Configuration |

### Data Layer

Types and helpers are in `src/data/types.ts`. Mock data is still in `src/data/mockData.ts` (used by pages until full API switchover).

API hooks are in `src/hooks/api/`:
- `useVendors`, `useVendor`, `useVendorHistory`, `useRescore`
- `useAlerts`, `useUpdateAlertStatus`
- `useWorkflows`, `useUpdateWorkflow`, `useCreateWorkflow`
- `useCompliance`
- `useDashboardSummary`
- `useRiskTrends`
- `useAuth` (`useLogin`, `useCurrentUser`, `useLogout`)

WebSocket hook: `src/hooks/useRealtimeUpdates.ts` — auto-reconnecting, invalidates queries on score updates, new alerts, clock ticks.

API client: `src/lib/api.ts` — axios instance with JWT interceptor, auto-redirect to `/login` on 401.

Key types: `Vendor`, `Alert`, `WorkflowItem`, `ComplianceStatus`, `DashboardSummary`, `RiskBand`.

### Key Custom Components

- **`CertInClock`** — Displays the live CERT-In 6-hour countdown; appears prominently on Dashboard for any vendor with `certInClock.active = true`
- **`RiskBadge`** — Color-coded band indicator using risk CSS tokens
- **`ScoreGauge`** — Circular gauge for composite score display
- **`RiskOrb`** — Animated Three.js orb (color/distortion driven by risk score)
- **`D3RiskHeatmap`** — D3 heatmap of vendor × dimension scores
- **`D3ConcentrationTreemap`** — D3 treemap for concentration risk
- **`D3FourthPartyGraph`** — D3 force graph for vendor dependency chains
- **`D3VendorSunburst`** — D3 sunburst for vendor categorization
- **`D3AlertTimeline`** — D3 timeline of alert history
- **`ConsortiumNetworkViz`** — Inter-bank DLT network visualization

Motion primitives in `src/components/motion/`: `PageTransition`, `StaggerContainer`, `StaggerItem` — wrap page content with these for consistent entrance animations.

### Styling Conventions

CSS variables are defined in `src/index.css`. Key semantic tokens:
- Risk bands: `--risk-critical`, `--risk-high`, `--risk-watch`, `--risk-stable` (and their `-foreground` variants)
- Regulatory: `--rbi`, `--certin`, `--dpdp`
- Fonts: `font-display` (Cabinet Grotesk), `font-body` (General Sans), `font-mono` (JetBrains Mono)

Use `cn()` from `src/lib/utils.ts` for conditional class composition (clsx + tailwind-merge).

### Testing

Tests go in `src/**/*.{test,spec}.{ts,tsx}`. Setup file at `src/test/setup.ts`. Uses `@testing-library/react` + `jsdom`.

---

## Risk Scoring Reference

| Band | Score Range | CSS token | Action |
|---|---|---|---|
| Critical | 0–24 | `risk-critical` | Activates CERT-In 6-hour clock |
| High Risk | 25–49 | `risk-high` | Escalate to CISO + CRO |
| Watch | 50–74 | `risk-watch` | Monitor, notify risk team |
| Stable | 75–100 | `risk-stable` | Routine monitoring |

9 risk dimensions: `cybersecurity`, `regulatory`, `operational`, `newsLegal`, `financialHealth`, `dataPrivacy`, `concentration`, `esg`, `fourthParty`.

---

## Backend (`backend/`)

**Stack:** FastAPI (Python 3.11+), SQLAlchemy async, PostgreSQL 16, Redis 7, Celery, Alembic

**Run:** `cd backend && docker-compose up -d postgres redis && pip install -e ".[dev]" && python -m scripts.seed && uvicorn app.main:app --reload --port 8000`

**Structure:** `app/core/` (config, db, auth), `app/models/` (10 ORM models), `app/schemas/` (Pydantic response shapes matching frontend types), `app/api/v1/` (all API routes), `app/services/` (business logic), `app/workers/` (Celery tasks), `app/engine/` (AI engine: LLM provider, ML scoring, Policy-as-Code rules)

**API routes:** All under `/api/v1`. JWT Bearer auth. Key endpoints: `/dashboard/summary` (single call for whole Dashboard), `/vendors`, `/alerts`, `/workflows`, `/compliance`, `/reports`, `/consortium`, `/risk-trends`, `WS /ws/live`

**AI Engine (Phase 2):** `engine/rules/cert_in.py` (CERT-In 6-hour clock), `engine/rules/rbi_outsourcing.py`, `engine/rules/dpdp.py` — each with regulatory citations. `engine/ml/altman_zscore.py` (financial health), `engine/ml/correlation_engine.py` (compound risk detection)

**Seed data:** `scripts/seed.py` ports all mockData.ts records into PostgreSQL. Login: `admin@thirdeye.io` / `thirdeye_admin`
