# IMPLEMENTATION.md

# Third Eye — Complete Production-Grade Implementation Plan

> From `mockData.ts` to a fully operational Risk Operating System.
> Built for `vendor-guardian` frontend + new FastAPI backend.

---

## Table of Contents

1. [Current State & Target State](#1-current-state--target-state)
2. [Phase 1 — Backend Foundation & API Layer](#2-phase-1--backend-foundation--api-layer)
3. [Phase 2 — AI Engine & Signal Ingestion](#3-phase-2--ai-engine--signal-ingestion)
4. [Phase 3 — Streaming, Consortium & Production](#4-phase-3--streaming-consortium--production)
5. [Frontend Integration Strategy](#5-frontend-integration-strategy)
6. [Database Schema](#6-database-schema)
7. [API Contract — Every Endpoint](#7-api-contract--every-endpoint)
8. [AI Engine Architecture](#8-ai-engine-architecture)
9. [Data Ingestion Pipeline](#9-data-ingestion-pipeline)
10. [Infrastructure & Deployment](#10-infrastructure--deployment)
11. [Testing Strategy](#11-testing-strategy)
12. [Environment Variables](#12-environment-variables)

---

## 1. Current State & Target State

### What Exists

**Frontend (`vendor-guardian`)** — 9 fully built pages, all reading from `src/data/mockData.ts`:

| Page | Route | Data it consumes from mockData |
|---|---|---|
| Dashboard | `/dashboard` | `vendors`, `alerts`, `riskTrendData`, `complianceData` |
| VendorRegistry | `/vendors` | `vendors` (filtered by band, searched by name/category) |
| VendorDetail | `/vendors/:id` | `vendors` (single), `alerts` (filtered by vendorId), `workflowItems` (filtered), `dimensionLabels` |
| AlertsPage | `/alerts` | `alerts` (filtered by severity + status) |
| WorkflowsPage | `/workflows` | `workflowItems` (grouped by status columns) |
| CompliancePage | `/compliance` | `complianceData` |
| ReportsPage | `/reports` | hardcoded report list (no mockData import) |
| ConsortiumPage | `/consortium` | hardcoded `consortiumNodes` + `recentSignals` |
| SettingsPage | `/settings` | none |

**Key frontend data types already defined:**
- `Vendor` — 9 dimension scores, `compositeScore`, `previousScore`, `riskBand`, `tier`, `certInClock`
- `Alert` — linked to vendor, has `severity`, `status`, `dimension`, `assignedTo`
- `WorkflowItem` — `priority`, `status`, `assignedTo`, `assignedRole`, `auditTrailId`
- `ComplianceStatus` — per-regulation `score`, `status`, `gaps[]`
- `RiskBand` — `"critical" | "high" | "watch" | "stable"`

### Target State

A production backend that:
1. Serves exactly the data shapes the frontend already consumes
2. Stores everything in PostgreSQL with full audit trail
3. Runs an AI engine that computes scores from real signals
4. Pushes real-time updates over WebSocket
5. Ingests external signals (news, CVE, dark web, regulatory)
6. Enforces RBI/DPDP/CERT-In rules deterministically
7. Broadcasts anonymized signals over Hyperledger Fabric consortium

---

## 2. Phase 1 — Backend Foundation & API Layer

**Goal:** Replace `mockData.ts` with a real database + API. Every frontend page stays identical visually — just live data underneath.

### 2.1 Backend Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                         # FastAPI app factory, CORS, lifespan
│   ├── core/
│   │   ├── config.py                   # pydantic-settings, all env vars typed
│   │   ├── security.py                 # JWT creation/validation, bcrypt
│   │   ├── database.py                 # SQLAlchemy async engine + session
│   │   ├── redis_client.py             # aioredis connection pool
│   │   └── dependencies.py             # Depends() — get_db, get_current_user
│   │
│   ├── models/                         # SQLAlchemy ORM models
│   │   ├── vendor.py
│   │   ├── vendor_dimension_score.py
│   │   ├── alert.py
│   │   ├── workflow.py
│   │   ├── compliance.py
│   │   ├── score_audit_log.py          # Append-only, never updated
│   │   ├── signal.py                   # Raw + parsed signals
│   │   ├── report.py
│   │   ├── consortium_signal.py
│   │   └── user.py
│   │
│   ├── schemas/                        # Pydantic request/response models
│   │   ├── vendor.py
│   │   ├── alert.py
│   │   ├── workflow.py
│   │   ├── compliance.py
│   │   ├── dashboard.py
│   │   ├── report.py
│   │   ├── consortium.py
│   │   └── auth.py
│   │
│   ├── api/v1/
│   │   ├── router.py                   # Aggregates all sub-routers under /api/v1
│   │   ├── auth.py                     # POST /login, /refresh, GET /me
│   │   ├── dashboard.py                # GET /dashboard/summary
│   │   ├── vendors.py                  # CRUD + /history, /rescore
│   │   ├── alerts.py                   # List + status updates
│   │   ├── workflows.py                # CRUD + status transitions
│   │   ├── compliance.py               # List + refresh
│   │   ├── reports.py                  # List + generate + export PDF
│   │   ├── consortium.py               # Nodes + signals
│   │   ├── risk_trends.py              # Historical trend data
│   │   └── websocket.py                # WS /ws/live — dashboard + clock
│   │
│   ├── services/                       # Business logic (no HTTP awareness)
│   │   ├── vendor_service.py
│   │   ├── alert_service.py
│   │   ├── workflow_service.py
│   │   ├── compliance_service.py
│   │   ├── scoring_service.py          # Composite score calculation
│   │   ├── report_service.py
│   │   └── audit_service.py            # Immutable log writer
│   │
│   ├── workers/                        # Celery async tasks
│   │   ├── celery_app.py
│   │   ├── score_tasks.py
│   │   ├── alert_tasks.py
│   │   ├── compliance_tasks.py
│   │   └── report_tasks.py
│   │
│   └── engine/                         # AI engine (Phase 2, scaffolded in Phase 1)
│       ├── llm/
│       ├── ml/
│       └── rules/
│
├── migrations/                         # Alembic
│   ├── env.py
│   └── versions/
│
├── scripts/
│   ├── seed.py                         # Port mockData.ts → SQL inserts
│   └── create_superuser.py
│
├── tests/
│   ├── conftest.py                     # Fixtures: async db, test client
│   ├── test_vendors.py
│   ├── test_alerts.py
│   ├── test_workflows.py
│   ├── test_dashboard.py
│   └── test_auth.py
│
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml
├── alembic.ini
└── .env.example
```

### 2.2 Key Dependencies (`pyproject.toml`)

```toml
[project]
name = "thirdeye-backend"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = [
    "fastapi>=0.115.0",
    "uvicorn[standard]>=0.30.0",
    "sqlalchemy[asyncio]>=2.0.0",
    "asyncpg>=0.30.0",
    "alembic>=1.14.0",
    "pydantic-settings>=2.0.0",
    "passlib[bcrypt]>=1.7.4",
    "python-jose[cryptography]>=3.3.0",
    "celery[redis]>=5.4.0",
    "redis>=5.0.0",
    "httpx>=0.28.0",
    "python-multipart>=0.0.9",
    "websockets>=13.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0.0",
    "pytest-asyncio>=0.24.0",
    "httpx>=0.28.0",
    "ruff>=0.8.0",
]
ai = [
    "anthropic>=0.40.0",
    "openai>=1.50.0",
    "scikit-learn>=1.5.0",
    "xgboost>=2.1.0",
    "weaviate-client>=4.9.0",
]
```

### 2.3 Docker Compose — Local Dev

```yaml
# docker-compose.yml
services:
  postgres:
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: thirdeye
      POSTGRES_USER: thirdeye
      POSTGRES_PASSWORD: thirdeye_dev
    ports: ["5432:5432"]
    volumes: [pgdata:/var/lib/postgresql/data]
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U thirdeye"]
      interval: 5s

  redis:
    image: redis:7-alpine
    ports: ["6379:6379"]
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 5s

  backend:
    build: ./backend
    ports: ["8000:8000"]
    env_file: ./backend/.env
    depends_on:
      postgres: { condition: service_healthy }
      redis: { condition: service_healthy }
    command: >
      sh -c "alembic upgrade head &&
             uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"
    volumes: ["./backend:/app"]

  celery_worker:
    build: ./backend
    env_file: ./backend/.env
    depends_on:
      postgres: { condition: service_healthy }
      redis: { condition: service_healthy }
    command: celery -A app.workers.celery_app worker -l info -Q default,scoring,alerts

  celery_beat:
    build: ./backend
    env_file: ./backend/.env
    depends_on: [redis]
    command: celery -A app.workers.celery_app beat -l info

volumes:
  pgdata:
```

### 2.4 Seed Script — Porting mockData.ts to Database

`scripts/seed.py` takes the exact vendor/alert/workflow/compliance data from `mockData.ts` and inserts it into PostgreSQL. This means the frontend sees identical data through the API as it does today through static imports — zero visual diff during migration.

---

## 3. Phase 2 — AI Engine & Signal Ingestion

**Goal:** Replace static scores with AI-computed scores from real external signals.

### What gets built:

1. **LLM Signal Parser** — reads raw text from news/dark web/regulatory sources, extracts structured risk signals
2. **ML Scoring Engine** — XGBoost models predict per-dimension scores from signal features + Altman Z-Score for financial health
3. **Correlation Engine** — detects compound risks (negative news + open Shodan ports + SLA degradation = high breach probability)
4. **Policy-as-Code Rule Engine** — deterministic RBI/DPDP/CERT-In compliance logic with regulatory citations
5. **Signal Connectors** — news feeds, CVE/NVD, MCA21, Shodan, HaveIBeenPwned, CERT-In advisories
6. **Weaviate Vector DB** — stores signal embeddings for semantic search and RAG-powered report generation
7. **Playbook Generator** — auto-drafts Letters of Concern, Remediation Tickets, RBI summaries using LLM

### What changes in the API:

- `POST /vendors/:id/rescore` triggers a full AI re-evaluation pipeline
- `GET /dashboard/summary` now returns AI-computed scores, not static ones
- `POST /compliance/refresh` runs all regulatory rules and updates compliance status
- New: `POST /reports/generate/:type` uses LLM to generate narrative Board papers
- WebSocket pushes real-time score updates as signals are processed

---

## 4. Phase 3 — Streaming, Consortium & Production

**Goal:** Event-driven architecture, inter-bank DLT network, Kubernetes production deployment.

### What gets built:

1. **Apache Kafka** replaces Celery Beat polling with event-driven streaming
2. **Hyperledger Fabric** consortium with autonomous on-chain agents per bank node
3. **Smart Contract Circuit Breakers** — including escrow holds on vendor payments
4. **Digital Twin Simulation** — model vendor failure blast radius
5. **Predictive Failure Modeling** — 12-month horizon using LightGBM
6. **EKS Production Deployment** — AWS Mumbai, multi-AZ, private VPC per tenant

---

## 5. Frontend Integration Strategy

### Step 1: API Client (`src/lib/api.ts`)

```typescript
import axios from "axios";

export const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL ?? "http://localhost:8000/api/v1",
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem("thirdeye_token");
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

api.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err.response?.status === 401) {
      localStorage.removeItem("thirdeye_token");
      window.location.href = "/login";
    }
    return Promise.reject(err);
  }
);
```

### Step 2: TanStack Query Hooks (`src/hooks/api/`)

One file per domain. Each hook maps 1:1 to what a page currently imports from `mockData.ts`.

```typescript
// src/hooks/api/useVendors.ts
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "@/lib/api";
import type { Vendor, RiskBand } from "@/data/types";

export function useVendors(filters?: { band?: RiskBand; search?: string }) {
  return useQuery({
    queryKey: ["vendors", filters],
    queryFn: () =>
      api.get<Vendor[]>("/vendors", { params: filters }).then((r) => r.data),
    staleTime: 30_000,
  });
}

export function useVendor(id: string) {
  return useQuery({
    queryKey: ["vendors", id],
    queryFn: () => api.get<Vendor>(`/vendors/${id}`).then((r) => r.data),
    enabled: !!id,
  });
}

export function useVendorHistory(id: string) {
  return useQuery({
    queryKey: ["vendors", id, "history"],
    queryFn: () => api.get(`/vendors/${id}/history`).then((r) => r.data),
    enabled: !!id,
  });
}

export function useRescore(id: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: () => api.post(`/vendors/${id}/rescore`),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["vendors"] });
      qc.invalidateQueries({ queryKey: ["dashboard-summary"] });
    },
  });
}
```

```typescript
// src/hooks/api/useDashboard.ts
import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";

interface DashboardSummary {
  aggregateScore: number;
  vendorCountsByBand: Record<string, number>;
  activeCertInClocks: Array<{
    vendorId: string;
    vendorName: string;
    remaining: string;
  }>;
  newAlertsCount: number;
  riskTrendData: Array<{
    date: string;
    score: number;
    critical: number;
    high: number;
    watch: number;
  }>;
  complianceSummary: Array<{
    regulation: string;
    category: string;
    score: number;
    status: string;
  }>;
  criticalVendors: Array<{
    id: string;
    name: string;
    compositeScore: number;
    change: number;
    trigger: string;
    riskBand: string;
  }>;
}

export function useDashboardSummary() {
  return useQuery({
    queryKey: ["dashboard-summary"],
    queryFn: () =>
      api.get<DashboardSummary>("/dashboard/summary").then((r) => r.data),
    refetchInterval: 60_000, // poll every 60s
  });
}
```

```typescript
// src/hooks/api/useAlerts.ts
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "@/lib/api";
import type { Alert, RiskBand } from "@/data/types";

export function useAlerts(filters?: { severity?: RiskBand; status?: string }) {
  return useQuery({
    queryKey: ["alerts", filters],
    queryFn: () =>
      api.get<Alert[]>("/alerts", { params: filters }).then((r) => r.data),
  });
}

export function useUpdateAlertStatus() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({
      id,
      status,
      assignedTo,
    }: {
      id: string;
      status: string;
      assignedTo?: string;
    }) => api.patch(`/alerts/${id}/status`, { status, assigned_to: assignedTo }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["alerts"] });
      qc.invalidateQueries({ queryKey: ["dashboard-summary"] });
    },
  });
}
```

```typescript
// src/hooks/api/useWorkflows.ts
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "@/lib/api";
import type { WorkflowItem } from "@/data/types";

export function useWorkflows(filters?: { status?: string; priority?: string }) {
  return useQuery({
    queryKey: ["workflows", filters],
    queryFn: () =>
      api
        .get<WorkflowItem[]>("/workflows", { params: filters })
        .then((r) => r.data),
  });
}

export function useUpdateWorkflowStatus() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({
      id,
      status,
      resolution,
    }: {
      id: string;
      status: string;
      resolution?: string;
    }) => api.patch(`/workflows/${id}`, { status, resolution }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["workflows"] }),
  });
}
```

```typescript
// src/hooks/api/useCompliance.ts
export function useCompliance() {
  return useQuery({
    queryKey: ["compliance"],
    queryFn: () => api.get("/compliance").then((r) => r.data),
  });
}

// src/hooks/api/useReports.ts
export function useReports() {
  return useQuery({
    queryKey: ["reports"],
    queryFn: () => api.get("/reports").then((r) => r.data),
  });
}

export function useGenerateReport() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (type: string) => api.post(`/reports/generate/${type}`),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["reports"] }),
  });
}

// src/hooks/api/useConsortium.ts
export function useConsortiumNodes() {
  return useQuery({
    queryKey: ["consortium-nodes"],
    queryFn: () => api.get("/consortium/nodes").then((r) => r.data),
  });
}

export function useConsortiumSignals() {
  return useQuery({
    queryKey: ["consortium-signals"],
    queryFn: () => api.get("/consortium/signals").then((r) => r.data),
    refetchInterval: 30_000,
  });
}

// src/hooks/api/useRiskTrends.ts
export function useRiskTrends(days: number = 30) {
  return useQuery({
    queryKey: ["risk-trends", days],
    queryFn: () =>
      api.get("/risk-trends", { params: { days } }).then((r) => r.data),
  });
}
```

### Step 3: WebSocket for Real-Time Updates

```typescript
// src/hooks/useRealtimeUpdates.ts
import { useEffect } from "react";
import { useQueryClient } from "@tanstack/react-query";

export function useRealtimeUpdates() {
  const qc = useQueryClient();

  useEffect(() => {
    const wsUrl = import.meta.env.VITE_WS_URL ?? "ws://localhost:8000";
    const token = localStorage.getItem("thirdeye_token");
    const ws = new WebSocket(`${wsUrl}/ws/live?token=${token}`);

    ws.onmessage = (event) => {
      const msg = JSON.parse(event.data);

      switch (msg.type) {
        case "vendor_score_update":
          qc.invalidateQueries({ queryKey: ["vendors"] });
          qc.invalidateQueries({ queryKey: ["dashboard-summary"] });
          break;
        case "new_alert":
          qc.invalidateQueries({ queryKey: ["alerts"] });
          qc.invalidateQueries({ queryKey: ["dashboard-summary"] });
          break;
        case "cert_in_clock_tick":
          // Update the specific vendor's clock without full refetch
          qc.setQueryData(["dashboard-summary"], (old: any) => {
            if (!old) return old;
            return {
              ...old,
              activeCertInClocks: old.activeCertInClocks.map((c: any) =>
                c.vendorId === msg.vendorId
                  ? { ...c, remaining: msg.remaining }
                  : c
              ),
            };
          });
          break;
        case "workflow_update":
          qc.invalidateQueries({ queryKey: ["workflows"] });
          break;
      }
    };

    ws.onerror = () => {
      // Reconnect after 5s
      setTimeout(() => ws.close(), 0);
    };

    return () => ws.close();
  }, [qc]);
}
```

### Step 4: Page-by-Page Migration

Each page changes from static import to hook. Example — `Dashboard.tsx`:

```typescript
// BEFORE
import { vendors, alerts, riskTrendData, complianceData } from "@/data/mockData";
// ... use directly

// AFTER
import { useDashboardSummary } from "@/hooks/api/useDashboard";
import { useRealtimeUpdates } from "@/hooks/useRealtimeUpdates";

export default function Dashboard() {
  useRealtimeUpdates(); // activate WebSocket
  const { data, isLoading, error } = useDashboardSummary();

  if (isLoading) return <DashboardSkeleton />;
  if (error) return <ErrorState />;

  const {
    aggregateScore,
    vendorCountsByBand,
    activeCertInClocks,
    newAlertsCount,
    riskTrendData,
    complianceSummary,
    criticalVendors,
  } = data;

  // ... rest of component stays identical, just uses data from hook
}
```

### Step 5: Extract Types to Shared File

Move all type definitions out of `mockData.ts` into `src/data/types.ts` so they survive the migration:

```typescript
// src/data/types.ts
export type RiskBand = "critical" | "high" | "watch" | "stable";

export interface Vendor { /* same as current mockData */ }
export interface Alert { /* same */ }
export interface WorkflowItem { /* same */ }
export interface ComplianceStatus { /* same */ }

// Keep helper functions too
export function getRiskBandColor(band: RiskBand): string { /* same */ }
export function getRiskBandBg(band: RiskBand): string { /* same */ }
export function getRiskBandLabel(band: RiskBand): string { /* same */ }

export const dimensionLabels: Record<string, string> = { /* same */ };
```

### Step 6: Auth Flow

Add a `/login` page and auth context:

```typescript
// src/hooks/api/useAuth.ts
export function useLogin() {
  return useMutation({
    mutationFn: (creds: { email: string; password: string }) =>
      api.post("/auth/login", creds).then((r) => {
        localStorage.setItem("thirdeye_token", r.data.access_token);
        return r.data;
      }),
  });
}

export function useCurrentUser() {
  return useQuery({
    queryKey: ["current-user"],
    queryFn: () => api.get("/auth/me").then((r) => r.data),
    retry: false,
  });
}
```

---

## 6. Database Schema

```sql
-- ============================================================
-- VENDORS
-- ============================================================
CREATE TABLE vendors (
    id                      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name                    TEXT NOT NULL,
    category                TEXT NOT NULL,
    tier                    TEXT NOT NULL CHECK (tier IN ('material','significant','standard')),

    -- Scores
    composite_score         INTEGER NOT NULL DEFAULT 100,
    previous_score          INTEGER,
    risk_band               TEXT NOT NULL CHECK (risk_band IN ('critical','high','watch','stable')),

    -- 9 dimension scores
    score_cybersecurity     INTEGER NOT NULL DEFAULT 100,
    score_regulatory        INTEGER NOT NULL DEFAULT 100,
    score_operational       INTEGER NOT NULL DEFAULT 100,
    score_news_legal        INTEGER NOT NULL DEFAULT 100,
    score_financial_health  INTEGER NOT NULL DEFAULT 100,
    score_data_privacy      INTEGER NOT NULL DEFAULT 100,
    score_concentration     INTEGER NOT NULL DEFAULT 100,
    score_esg               INTEGER NOT NULL DEFAULT 100,
    score_fourth_party      INTEGER NOT NULL DEFAULT 100,

    -- Metadata
    contract_expiry         DATE,
    last_assessed           TIMESTAMPTZ,
    triggers                TEXT[] DEFAULT '{}',

    -- CERT-In 6-hour clock
    cert_in_clock_active    BOOLEAN DEFAULT FALSE,
    cert_in_clock_started   TIMESTAMPTZ,

    created_at              TIMESTAMPTZ DEFAULT NOW(),
    updated_at              TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_vendors_risk_band ON vendors(risk_band);
CREATE INDEX idx_vendors_tier ON vendors(tier);

-- ============================================================
-- ALERTS
-- ============================================================
CREATE TABLE alerts (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    vendor_id       UUID NOT NULL REFERENCES vendors(id) ON DELETE CASCADE,
    vendor_name     TEXT NOT NULL,  -- denormalized for read performance
    severity        TEXT NOT NULL CHECK (severity IN ('critical','high','watch','stable')),
    title           TEXT NOT NULL,
    description     TEXT,
    dimension       TEXT,
    status          TEXT NOT NULL DEFAULT 'new'
                    CHECK (status IN ('new','acknowledged','assigned','resolved')),
    assigned_to     TEXT,
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_alerts_vendor ON alerts(vendor_id);
CREATE INDEX idx_alerts_status ON alerts(status);
CREATE INDEX idx_alerts_severity ON alerts(severity);

-- ============================================================
-- WORKFLOW ITEMS
-- ============================================================
CREATE TABLE workflow_items (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    vendor_id       UUID NOT NULL REFERENCES vendors(id) ON DELETE CASCADE,
    vendor_name     TEXT NOT NULL,
    title           TEXT NOT NULL,
    priority        TEXT NOT NULL CHECK (priority IN ('critical','high','medium','low')),
    status          TEXT NOT NULL DEFAULT 'open'
                    CHECK (status IN ('open','in_progress','pending_review','resolved','closed')),
    assigned_to     TEXT NOT NULL,
    assigned_role   TEXT NOT NULL,
    due_date        TIMESTAMPTZ,
    resolution      TEXT,
    audit_trail_id  TEXT UNIQUE NOT NULL,  -- e.g. AUD-2024-7821
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_workflows_vendor ON workflow_items(vendor_id);
CREATE INDEX idx_workflows_status ON workflow_items(status);

-- ============================================================
-- COMPLIANCE STATUSES
-- ============================================================
CREATE TABLE compliance_statuses (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    regulation      TEXT NOT NULL,
    category        TEXT NOT NULL,     -- 'RBI', 'CERT-In', 'DPDP', 'SEBI'
    score           INTEGER NOT NULL,
    status          TEXT NOT NULL CHECK (status IN (
                    'compliant','partial','non_compliant','not_assessed')),
    gaps            TEXT[] DEFAULT '{}',
    last_checked    DATE,
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================
-- SCORE AUDIT LOG (append-only — NEVER UPDATE OR DELETE)
-- ============================================================
CREATE TABLE score_audit_log (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    vendor_id           UUID NOT NULL REFERENCES vendors(id),
    old_composite       INTEGER,
    new_composite       INTEGER,
    old_band            TEXT,
    new_band            TEXT,
    dimension_affected  TEXT,
    old_dimension_score INTEGER,
    new_dimension_score INTEGER,
    trigger_signal      TEXT NOT NULL,
    model_version       TEXT NOT NULL,
    rule_activated      TEXT,
    regulatory_citation TEXT,
    recommended_action  TEXT,
    actor               TEXT NOT NULL DEFAULT 'system',
    created_at          TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_audit_vendor ON score_audit_log(vendor_id);
CREATE INDEX idx_audit_created ON score_audit_log(created_at);

-- ============================================================
-- SIGNALS (raw + parsed)
-- ============================================================
CREATE TABLE signals (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    vendor_id       UUID REFERENCES vendors(id),
    source          TEXT NOT NULL,     -- 'news', 'cve', 'dark_web', 'mca21', 'shodan', etc.
    source_url      TEXT,
    raw_text        TEXT,
    parsed_dimension TEXT,
    parsed_severity  INTEGER,          -- 1-10
    parsed_summary   TEXT,
    regulatory_flag  TEXT,             -- 'RBI', 'CERT-In', 'DPDP', null
    is_processed     BOOLEAN DEFAULT FALSE,
    llm_model_used   TEXT,
    created_at       TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_signals_vendor ON signals(vendor_id);
CREATE INDEX idx_signals_processed ON signals(is_processed);

-- ============================================================
-- REPORTS
-- ============================================================
CREATE TABLE reports (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title           TEXT NOT NULL,
    report_type     TEXT NOT NULL,     -- 'board_paper', 'regulatory_register', etc.
    regulation      TEXT,
    status          TEXT NOT NULL DEFAULT 'ready'
                    CHECK (status IN ('ready','generating','failed')),
    file_path       TEXT,              -- S3 key or local path to generated PDF
    generated_at    TIMESTAMPTZ,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================
-- CONSORTIUM SIGNALS (anonymized, from DLT)
-- ============================================================
CREATE TABLE consortium_signals (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    signal_type     TEXT NOT NULL,     -- 'CRITICAL_BREACH', 'ENFORCEMENT_ACTION', etc.
    dimension       TEXT,
    vendor_hash     TEXT NOT NULL,     -- sha256 hash of vendor identity
    severity        TEXT NOT NULL,
    cert_in_relevant BOOLEAN DEFAULT FALSE,
    source_node     TEXT DEFAULT 'REDACTED',
    received_at     TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================
-- CONSORTIUM NODES
-- ============================================================
CREATE TABLE consortium_nodes (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    bank_name       TEXT NOT NULL,
    node_status     TEXT NOT NULL DEFAULT 'offline'
                    CHECK (node_status IN ('online','syncing','offline')),
    last_signal_at  TIMESTAMPTZ,
    vendors_monitored INTEGER DEFAULT 0,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================
-- RISK TREND SNAPSHOTS (populated by daily Celery Beat job)
-- ============================================================
CREATE TABLE risk_trend_snapshots (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    snapshot_date   DATE NOT NULL,
    aggregate_score INTEGER NOT NULL,
    critical_count  INTEGER NOT NULL DEFAULT 0,
    high_count      INTEGER NOT NULL DEFAULT 0,
    watch_count     INTEGER NOT NULL DEFAULT 0,
    stable_count    INTEGER NOT NULL DEFAULT 0,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE UNIQUE INDEX idx_trend_date ON risk_trend_snapshots(snapshot_date);

-- ============================================================
-- USERS
-- ============================================================
CREATE TABLE users (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email           TEXT UNIQUE NOT NULL,
    hashed_password TEXT NOT NULL,
    full_name       TEXT,
    role            TEXT NOT NULL CHECK (role IN (
                    'cto','ciso','compliance','audit','vendor_risk','business_unit')),
    is_active       BOOLEAN DEFAULT TRUE,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);
```

---

## 7. API Contract — Every Endpoint

All routes under `/api/v1`. JWT Bearer auth on all except `/api/v1/auth/*`.

### Auth

| Method | Endpoint | Request | Response |
|---|---|---|---|
| `POST` | `/auth/login` | `{ email, password }` | `{ access_token, token_type, user }` |
| `POST` | `/auth/refresh` | Bearer token | `{ access_token }` |
| `GET` | `/auth/me` | Bearer token | `User` object |

### Dashboard

| Method | Endpoint | Response |
|---|---|---|
| `GET` | `/dashboard/summary` | `DashboardSummary` (aggregate score, band counts, active clocks, new alerts count, critical vendors, risk trend data, compliance summary) |

This single endpoint returns everything the Dashboard page needs in one call — no waterfall.

### Vendors

| Method | Endpoint | Params | Response |
|---|---|---|---|
| `GET` | `/vendors` | `?band=&tier=&search=&sort=score\|name\|change` | `Vendor[]` |
| `GET` | `/vendors/:id` | — | `Vendor` (full detail with all 9 dimensions) |
| `POST` | `/vendors` | `CreateVendor` body | `Vendor` |
| `PATCH` | `/vendors/:id` | partial update body | `Vendor` |
| `GET` | `/vendors/:id/history` | `?limit=50` | `ScoreAuditLog[]` |
| `POST` | `/vendors/:id/rescore` | — | `{ task_id }` (queues Celery task) |

**Vendor response shape** (matches frontend `Vendor` type exactly):

```json
{
  "id": "v001",
  "name": "Acme Payments Ltd.",
  "category": "Payment Switch Operator",
  "compositeScore": 34,
  "previousScore": 61,
  "riskBand": "high",
  "tier": "material",
  "contractExpiry": "2025-06-30",
  "lastAssessed": "2024-03-04",
  "dimensions": {
    "cybersecurity": 28,
    "regulatory": 61,
    "operational": 70,
    "newsLegal": 55,
    "financialHealth": 80,
    "dataPrivacy": 72,
    "concentration": 65,
    "esg": 58,
    "fourthParty": 45
  },
  "triggers": ["Dark web credential dump detected (12,400 records)"],
  "certInClock": {
    "active": true,
    "remaining": "02:14:33",
    "startedAt": "2024-03-04T03:17:00Z"
  }
}
```

**Note:** Backend stores dimensions as separate columns but serializes them into the `dimensions` dict in the Pydantic response schema. This matches the frontend type exactly.

### Alerts

| Method | Endpoint | Params | Response |
|---|---|---|---|
| `GET` | `/alerts` | `?severity=&status=&vendor_id=` | `Alert[]` |
| `GET` | `/alerts/:id` | — | `Alert` |
| `PATCH` | `/alerts/:id/status` | `{ status, assigned_to? }` | `Alert` |

### Workflows

| Method | Endpoint | Params | Response |
|---|---|---|---|
| `GET` | `/workflows` | `?status=&priority=` | `WorkflowItem[]` |
| `GET` | `/workflows/:id` | — | `WorkflowItem` |
| `POST` | `/workflows` | `CreateWorkflow` body | `WorkflowItem` |
| `PATCH` | `/workflows/:id` | `{ status?, resolution? }` | `WorkflowItem` |

### Compliance

| Method | Endpoint | Response |
|---|---|---|
| `GET` | `/compliance` | `ComplianceStatus[]` |
| `POST` | `/compliance/refresh` | `{ task_id }` (queues rule engine re-evaluation) |

### Reports

| Method | Endpoint | Response |
|---|---|---|
| `GET` | `/reports` | `Report[]` (list of available/generated reports) |
| `POST` | `/reports/generate/:type` | `{ task_id }` (queues PDF generation) |
| `GET` | `/reports/:id/download` | PDF file stream |

### Risk Trends

| Method | Endpoint | Params | Response |
|---|---|---|---|
| `GET` | `/risk-trends` | `?days=30` | `RiskTrendSnapshot[]` |

### Consortium

| Method | Endpoint | Response |
|---|---|---|
| `GET` | `/consortium/nodes` | `ConsortiumNode[]` |
| `GET` | `/consortium/signals` | `ConsortiumSignal[]` |
| `GET` | `/consortium/status` | Own node connectivity + health |

### WebSocket

| Protocol | Endpoint | Message Types |
|---|---|---|
| `WS` | `/ws/live?token=<jwt>` | `vendor_score_update`, `new_alert`, `cert_in_clock_tick`, `workflow_update` |

---

## 8. AI Engine Architecture

### Directory Structure (Phase 2)

```
backend/app/engine/
├── llm/
│   ├── provider.py              # Abstract base + OpenAI/Anthropic/Azure implementations
│   ├── signal_parser.py         # Raw text → ParsedSignal
│   ├── playbook_generator.py    # Risk event → Letter of Concern / Remediation Ticket
│   ├── report_narrator.py       # Data → narrative Board paper text
│   └── prompts/
│       ├── signal_parse.py      # Structured prompt for signal extraction
│       ├── playbook.py          # Templates for different playbook types
│       └── report.py            # Board paper narrative prompts
│
├── ml/
│   ├── scorer.py                # XGBoost: features → per-dimension scores
│   ├── feature_builder.py       # Signals + history → feature vectors
│   ├── altman_zscore.py         # Financial health: Altman Z-Score model
│   ├── correlation_engine.py    # Compound risk detection
│   ├── model_registry.py        # Model versioning (S3 or local)
│   └── training/
│       ├── train_dimension.py   # Train per-dimension XGBoost model
│       └── datasets/            # Historical training data
│
└── rules/
    ├── engine.py                # Policy-as-Code evaluator
    ├── base_rule.py             # Abstract Rule with citation field
    ├── rbi_outsourcing.py       # RBI IT Outsourcing Directions 2023
    ├── cert_in.py               # CERT-In 6-hour clock trigger logic
    ├── dpdp.py                  # DPDP Act breach notification rules
    ├── rbi_cybersecurity.py     # RBI Cybersecurity Framework thresholds
    └── sebi_mca.py              # SEBI/MCA21 filing anomaly rules
```

### LLM Signal Parser — How It Works

```python
# app/engine/llm/signal_parser.py

class ParsedSignal(BaseModel):
    vendor_match: str | None          # Matched vendor name, if any
    dimension: str                     # Which of the 9 risk dimensions
    severity: int                      # 1-10
    summary: str                       # One-line summary
    regulatory_implication: str | None # 'RBI' | 'CERT-In' | 'DPDP' | None
    recommended_action: str
    confidence: float                  # 0.0-1.0

async def parse_signal(raw_text: str, source: str, provider: LLMProvider) -> ParsedSignal:
    """
    Takes raw text (news article, dark web alert, regulatory notice)
    and extracts a structured risk signal using the configured LLM.
    """
    prompt = SIGNAL_PARSE_PROMPT.format(
        text=raw_text,
        source=source,
        vendor_list=await get_active_vendor_names(),
        dimensions=DIMENSION_DESCRIPTIONS,
    )
    response = await provider.complete(prompt, response_format=ParsedSignal)
    return response
```

### ML Scoring Engine — How It Works

```python
# app/engine/ml/scorer.py

class DimensionScorer:
    """
    One XGBoost model per risk dimension.
    Input: feature vector built from recent signals + historical scores.
    Output: 0-100 score for that dimension.
    """

    def __init__(self, dimension: str, model_path: str):
        self.dimension = dimension
        self.model = xgb.XGBRegressor()
        self.model.load_model(model_path)
        self.model_version = self._get_version(model_path)

    def score(self, features: dict) -> tuple[int, str]:
        """Returns (score, model_version)"""
        X = self._build_feature_vector(features)
        raw = self.model.predict(X)[0]
        return int(max(0, min(100, raw))), self.model_version
```

### Correlation Engine — Compound Risk Detection

```python
# app/engine/ml/correlation_engine.py

class CompoundRiskDetector:
    """
    Detects multi-signal compound risks that no single dimension catches.

    Example compound pattern:
      negative_news + open_shodan_ports + sla_degradation
      = HIGH breach probability (score multiplier: 0.6x)
    """

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
            description="Regulatory cascade: multiple regulatory bodies flagging",
        ),
    ]

    def detect(self, vendor_id: str, recent_signals: list[Signal]) -> list[CompoundRisk]:
        """Check all signals against compound patterns, return matches."""
```

### Altman Z-Score — Financial Health

```python
# app/engine/ml/altman_zscore.py

def calculate_altman_z(financials: VendorFinancials) -> tuple[float, str]:
    """
    Altman Z-Score for predicting vendor bankruptcy risk.

    Z = 1.2*X1 + 1.4*X2 + 3.3*X3 + 0.6*X4 + 1.0*X5

    Where:
      X1 = Working Capital / Total Assets
      X2 = Retained Earnings / Total Assets
      X3 = EBIT / Total Assets
      X4 = Market Value of Equity / Total Liabilities
      X5 = Sales / Total Assets

    Z > 2.99  → Safe zone
    1.81-2.99 → Grey zone
    Z < 1.81  → Distress zone
    """
```

### Composite Score Calculation

```python
# app/services/scoring_service.py

# Dimension weights (must sum to 1.0)
DIMENSION_WEIGHTS = {
    "cybersecurity":    0.20,
    "regulatory":       0.18,
    "operational":      0.15,
    "news_legal":       0.12,
    "financial_health": 0.12,
    "data_privacy":     0.08,
    "concentration":    0.07,
    "esg":              0.04,
    "fourth_party":     0.04,
}

def compute_composite_score(dimensions: dict[str, int]) -> int:
    """Weighted average of all dimension scores."""
    total = sum(
        dimensions[dim] * weight
        for dim, weight in DIMENSION_WEIGHTS.items()
    )
    return int(round(total))

def compute_risk_band(score: int) -> str:
    if score <= 24:  return "critical"
    if score <= 49:  return "high"
    if score <= 74:  return "watch"
    return "stable"
```

### Policy-as-Code Rule Engine

```python
# app/engine/rules/base_rule.py

class BaseRule(ABC):
    """Every rule carries a regulatory citation and version."""
    name: str
    citation: str           # e.g. "CERT-In Directions 2022, Section 4(ii)"
    version: str            # e.g. "1.0.0"

    @abstractmethod
    def evaluate(self, vendor: Vendor, signals: list[Signal]) -> RuleResult:
        """Returns triggered=True/False, action, rationale, citation."""

# app/engine/rules/cert_in.py

class CertInClockRule(BaseRule):
    name = "cert_in_6hr_clock"
    citation = "CERT-In Directions 2022, Section 4(ii)"
    version = "1.0.0"

    def evaluate(self, vendor, signals):
        has_cyber_incident = any(
            s.parsed_dimension == "cybersecurity" and s.parsed_severity >= 8
            for s in signals
        )
        if vendor.composite_score <= 24 and has_cyber_incident:
            return RuleResult(
                triggered=True,
                action="ACTIVATE_CERT_IN_CLOCK",
                rationale="Composite below critical threshold with confirmed cyber incident",
                citation=self.citation,
            )
        return RuleResult(triggered=False)
```

---

## 9. Data Ingestion Pipeline

### Connector Architecture (Phase 2)

```
backend/app/ingest/
├── connectors/
│   ├── base.py                  # Abstract connector interface
│   ├── news_feed.py             # Google News RSS / GDELT / NewsAPI
│   ├── cve_nvd.py               # NVD/CVE API — polls for new CVEs
│   ├── cert_in.py               # CERT-In advisories RSS
│   ├── mca21.py                 # MCA21 company filings (web scraper)
│   ├── rbi_enforcement.py       # RBI enforcement database RSS
│   ├── shodan.py                # Shodan API — open ports/services per vendor
│   ├── hibp.py                  # HaveIBeenPwned — credential leaks
│   └── dark_web_stub.py         # Stub for dark web integration
│
├── normalizer.py                # All connectors → unified RawSignal schema
└── dispatcher.py                # Routes signals to Celery processing tasks
```

### Celery Tasks

```python
# app/workers/score_tasks.py

@celery_app.task(name="tasks.rescore_vendor", queue="scoring")
def rescore_vendor(vendor_id: str):
    """Full AI pipeline: gather signals → LLM parse → ML score → rule check → update DB."""

@celery_app.task(name="tasks.rescore_all_vendors", queue="scoring")
def rescore_all_vendors():
    """Scheduled: every 6 hours via Celery Beat."""

@celery_app.task(name="tasks.take_risk_trend_snapshot", queue="default")
def take_risk_trend_snapshot():
    """Scheduled: daily at midnight IST. Populates risk_trend_snapshots table."""


# app/workers/alert_tasks.py

@celery_app.task(name="tasks.process_score_change", queue="alerts")
def process_score_change(vendor_id: str, old_score: int, new_score: int):
    """Create alert + workflow if band changed. Activate CERT-In clock if critical."""

@celery_app.task(name="tasks.generate_playbook", queue="default")
def generate_playbook(alert_id: str):
    """LLM generates Letter of Concern or Remediation Ticket for this alert."""


# app/workers/ingest_tasks.py

@celery_app.task(name="tasks.ingest_news", queue="default")
def ingest_news():
    """Runs every 15 min. Polls news feeds, creates RawSignal records."""

@celery_app.task(name="tasks.ingest_cve", queue="default")
def ingest_cve():
    """Runs every hour. Polls NVD API for new CVEs."""

@celery_app.task(name="tasks.ingest_shodan", queue="default")
def ingest_shodan():
    """Runs every 6 hours. Checks open ports for vendor domains."""

@celery_app.task(name="tasks.process_signal", queue="scoring")
def process_signal(signal_id: str):
    """LLM parse → match vendor → update dimension → check rules → emit alert if needed."""


# app/workers/compliance_tasks.py

@celery_app.task(name="tasks.run_compliance_rules", queue="default")
def run_compliance_rules():
    """Runs every hour. Evaluates all rules against all vendors, updates compliance_statuses."""


# app/workers/report_tasks.py

@celery_app.task(name="tasks.generate_report", queue="default")
def generate_report(report_type: str):
    """LLM-powered report generation. Produces PDF, stores in S3."""
```

### Celery Beat Schedule

```python
# app/workers/celery_app.py

celery_app.conf.beat_schedule = {
    "ingest-news-every-15m": {
        "task": "tasks.ingest_news",
        "schedule": crontab(minute="*/15"),
    },
    "ingest-cve-hourly": {
        "task": "tasks.ingest_cve",
        "schedule": crontab(minute=0),
    },
    "ingest-shodan-every-6h": {
        "task": "tasks.ingest_shodan",
        "schedule": crontab(hour="*/6", minute=30),
    },
    "rescore-all-vendors-every-6h": {
        "task": "tasks.rescore_all_vendors",
        "schedule": crontab(hour="*/6", minute=0),
    },
    "run-compliance-rules-hourly": {
        "task": "tasks.run_compliance_rules",
        "schedule": crontab(minute=15),
    },
    "daily-risk-trend-snapshot": {
        "task": "tasks.take_risk_trend_snapshot",
        "schedule": crontab(hour=0, minute=5),  # 00:05 IST
    },
}
```

---

## 10. Infrastructure & Deployment

### Production Architecture (AWS Mumbai)

```
AWS ap-south-1 (Mumbai) — RBI data residency mandatory

EKS Cluster (thirdeye-prod namespace):
  ┌─────────────────────────────────────────────────────────┐
  │                                                         │
  │  frontend        (nginx, 2 replicas)                    │
  │  backend          (FastAPI, 3 replicas, HPA on CPU)     │
  │  celery-scoring   (scoring queue, 2 replicas)           │
  │  celery-alerts    (alerts queue, 1 replica)             │
  │  celery-default   (default queue, 1 replica)            │
  │  celery-beat      (singleton, 1 replica)                │
  │                                                         │
  └─────────────────────────────────────────────────────────┘

Managed Services:
  RDS PostgreSQL 16    (Multi-AZ, db.r6g.large)
  ElastiCache Redis 7  (cluster mode, cache.r6g.large)
  MSK (Kafka)          (Phase 3 only)
  S3                   (ML model artifacts, generated PDFs, audit exports)
  Weaviate             (self-hosted on EKS, 1 replica)

Networking:
  Private VPC per bank tenant
  ALB → backend (HTTPS, TLS 1.3 only)
  CloudFront → frontend (static assets)
  VPC endpoints for S3, RDS
  No cross-tenant routing

CI/CD (GitHub Actions):
  on: push to main
  jobs:
    lint-and-test:
      - backend: ruff + pytest
      - frontend: eslint + vitest
    build:
      - Docker image → ECR
    deploy:
      - Helm upgrade → EKS staging
      - Run smoke tests
      - Promote to production (manual gate)
```

### Helm Chart Structure

```
deploy/
├── helm/
│   ├── Chart.yaml
│   ├── values.yaml
│   ├── values-staging.yaml
│   ├── values-production.yaml
│   └── templates/
│       ├── backend-deployment.yaml
│       ├── backend-service.yaml
│       ├── backend-hpa.yaml
│       ├── celery-worker-deployment.yaml
│       ├── celery-beat-deployment.yaml
│       ├── frontend-deployment.yaml
│       ├── frontend-service.yaml
│       ├── ingress.yaml
│       ├── secrets.yaml
│       └── configmap.yaml
```

---

## 11. Testing Strategy

### Backend Tests

```
tests/
├── conftest.py              # async DB fixtures, test client, test user
├── unit/
│   ├── test_scoring.py      # composite score calculation, band mapping
│   ├── test_rules/
│   │   ├── test_cert_in.py  # clock triggers correctly on critical + cyber
│   │   ├── test_rbi.py      # outsourcing rules with citations
│   │   └── test_dpdp.py     # breach notification rules
│   ├── test_altman.py       # Z-score safe/grey/distress zones
│   └── test_correlation.py  # compound risk pattern detection
│
├── api/
│   ├── test_vendors.py      # CRUD + filtering + auth
│   ├── test_alerts.py       # status transitions
│   ├── test_workflows.py    # workflow lifecycle
│   ├── test_dashboard.py    # summary aggregation correctness
│   ├── test_auth.py         # login, JWT, RBAC
│   └── test_websocket.py    # WS connection + message types
│
└── integration/
    ├── test_signal_pipeline.py  # signal → LLM parse → score → alert
    └── test_cert_in_clock.py    # full flow: critical event → clock activation → WS push
```

**Key testing principles:**
- Every rule engine rule has a test that verifies the regulatory citation is present
- Every score audit log entry is verified in integration tests
- CERT-In clock activation is tested end-to-end
- No test touches production LLM APIs — use recorded responses

### Frontend Tests

```
src/test/
├── setup.ts                         # jsdom + testing library
├── hooks/
│   ├── useVendors.test.ts           # MSW mock API, verify query behavior
│   ├── useDashboard.test.ts
│   └── useRealtimeUpdates.test.ts   # WebSocket mock
├── components/
│   ├── CertInClock.test.tsx         # urgent vs normal rendering
│   ├── RiskBadge.test.tsx           # correct colors per band
│   └── ScoreGauge.test.tsx
└── pages/
    └── Dashboard.test.tsx           # renders with mock data, skeleton on loading
```

### E2E Tests (Playwright)

```
e2e/
├── dashboard.spec.ts        # load dashboard, verify vendor counts match
├── vendor-detail.spec.ts    # click vendor → detail page → radar chart renders
├── alert-triage.spec.ts     # change alert status, verify update
└── workflow-kanban.spec.ts  # drag workflow item between columns
```

---

## 12. Environment Variables

### Backend (`.env`)

```env
# ─── Database ───
DATABASE_URL=postgresql+asyncpg://thirdeye:password@localhost:5432/thirdeye
DATABASE_ECHO=false

# ─── Redis ───
REDIS_URL=redis://localhost:6379/0

# ─── Auth ───
SECRET_KEY=<generate-32-byte-random>
ACCESS_TOKEN_EXPIRE_MINUTES=480
ALGORITHM=HS256

# ─── CORS ───
CORS_ORIGINS=http://localhost:8080,http://localhost:5173

# ─── LLM Provider (Phase 2) ───
LLM_PROVIDER=anthropic                # or: openai | azure_openai
ANTHROPIC_API_KEY=
OPENAI_API_KEY=
AZURE_OPENAI_ENDPOINT=
AZURE_OPENAI_API_KEY=

# ─── Weaviate (Phase 2) ───
WEAVIATE_URL=http://localhost:8081

# ─── Signal Sources (Phase 2) ───
NEWS_API_KEY=
SHODAN_API_KEY=
HIBP_API_KEY=
NVD_API_KEY=

# ─── AWS (Production) ───
AWS_REGION=ap-south-1
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
S3_BUCKET_REPORTS=thirdeye-reports
S3_BUCKET_MODELS=thirdeye-models

# ─── Consortium (Phase 3) ───
FABRIC_NETWORK_ENABLED=false
FABRIC_PEER_ENDPOINT=grpcs://peer0.bank.thirdeye.network:7051
FABRIC_CHANNEL_NAME=vendor-risk-consortium
FABRIC_CHAINCODE_NAME=risk-agent

# ─── Encryption ───
ENCRYPTION_KEY=<aes-256-key>
```

### Frontend (`.env.local`)

```env
VITE_API_URL=http://localhost:8000/api/v1
VITE_WS_URL=ws://localhost:8000
```

---

## Delivery Milestones

### Phase 1 — Backend Foundation (Weeks 1–6)

| Week | Deliverable |
|---|---|
| 1 | Project scaffold, Docker Compose running, Alembic migrations, DB schema created |
| 2 | User model + JWT auth, RBAC middleware, login endpoint |
| 3 | Vendor CRUD, Alert CRUD, Workflow CRUD, Compliance endpoints — all returning seeded mock data from DB |
| 4 | Dashboard summary endpoint (aggregation), Risk trend endpoint, WebSocket skeleton |
| 5 | Frontend integration: create `src/lib/api.ts`, all TanStack Query hooks, replace `mockData.ts` imports in all 9 pages |
| 6 | WebSocket real-time updates working, CERT-In clock push, auth flow in frontend, `mockData.ts` deleted |

**Phase 1 exit criteria:** Every page loads data from the API. WebSocket pushes score updates live. Auth works. `mockData.ts` no longer imported anywhere.

### Phase 2 — AI Engine & Signals (Weeks 7–14)

| Week | Deliverable |
|---|---|
| 7 | LLM provider abstraction (Anthropic + OpenAI), signal parser with structured output |
| 8 | News feed connector, CVE/NVD connector, signals table populated |
| 9 | XGBoost dimension scorers (initial models), Altman Z-Score for financial health |
| 10 | Correlation engine — compound risk detection patterns |
| 11 | Policy-as-Code rule engine — CERT-In clock, RBI outsourcing, DPDP rules — all with regulatory citations |
| 12 | Full scoring pipeline: signal → LLM parse → ML score → correlation check → rule engine → alert → WebSocket push |
| 13 | Playbook generator (auto-draft Letters of Concern, Remediation Tickets), Weaviate integration |
| 14 | Report generator (LLM-powered narrative Board papers), PDF export, Shodan + HIBP connectors |

**Phase 2 exit criteria:** Scores are computed by AI from real signals. Rules fire with citations. Playbooks auto-generate. Reports export as PDF.

### Phase 3 — Streaming & Consortium (Weeks 15–20)

| Week | Deliverable |
|---|---|
| 15 | Apache Kafka setup, Avro schemas, replace Celery Beat polling with Kafka consumers |
| 16 | Kafka → WebSocket bridge for true real-time push |
| 17 | Hyperledger Fabric network setup, chaincode for anonymized signal broadcast |
| 18 | Autonomous on-chain agent: broadcast rules, severity threshold, disclosure policy |
| 19 | Digital Twin simulation UI, smart contract circuit breaker + escrow logic |
| 20 | EKS production deployment, Helm charts, GitHub Actions CI/CD, smoke tests |

**Phase 3 exit criteria:** Kafka streaming operational. Consortium DLT node broadcasting signals. Production Kubernetes cluster running in AWS Mumbai.

---

## Quick Start — Getting Phase 1 Running

```bash
# 1. Start infrastructure
docker-compose up -d postgres redis

# 2. Set up backend
cd backend
cp .env.example .env                # edit with your values
pip install -e ".[dev]"
alembic upgrade head
python scripts/seed.py              # loads mockData equivalent into DB
uvicorn app.main:app --reload --port 8000

# 3. Start Celery worker (separate terminal)
cd backend
celery -A app.workers.celery_app worker -l info

# 4. Set up frontend
cd vendor-guardian
echo "VITE_API_URL=http://localhost:8000/api/v1" > .env.local
echo "VITE_WS_URL=ws://localhost:8000" >> .env.local
npm install
npm run dev

# 5. Open http://localhost:8080
# Login with seeded user: admin@thirdeye.io / thirdeye_admin
```
