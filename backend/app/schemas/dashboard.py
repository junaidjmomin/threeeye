from pydantic import BaseModel


class CertInClockSummary(BaseModel):
    vendorId: str
    vendorName: str
    remaining: str


class CriticalVendorSummary(BaseModel):
    id: str
    name: str
    compositeScore: int
    change: int
    trigger: str
    riskBand: str


class RiskTrendPoint(BaseModel):
    date: str
    score: int
    critical: int
    high: int
    watch: int


class ComplianceSummaryItem(BaseModel):
    regulation: str
    category: str
    score: int
    status: str


class DashboardSummary(BaseModel):
    """Single response for the entire Dashboard page. No waterfall."""

    aggregateScore: int
    vendorCountsByBand: dict[str, int]
    activeCertInClocks: list[CertInClockSummary]
    newAlertsCount: int
    criticalVendors: list[CriticalVendorSummary]
    riskTrendData: list[RiskTrendPoint]
    complianceSummary: list[ComplianceSummaryItem]
