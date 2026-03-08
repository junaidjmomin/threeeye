from fastapi import APIRouter, Depends
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.vendor import Vendor
from app.models.alert import Alert
from app.models.compliance import ComplianceStatus
from app.models.risk_trend import RiskTrendSnapshot
from app.schemas.dashboard import (
    DashboardSummary,
    CertInClockSummary,
    CriticalVendorSummary,
    RiskTrendPoint,
    ComplianceSummaryItem,
)

router = APIRouter()


@router.get("/summary", response_model=DashboardSummary)
async def get_dashboard_summary(
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    # All vendors
    result = await db.execute(select(Vendor))
    vendors = result.scalars().all()

    if not vendors:
        return DashboardSummary(
            aggregateScore=0,
            vendorCountsByBand={"critical": 0, "high": 0, "watch": 0, "stable": 0},
            activeCertInClocks=[],
            newAlertsCount=0,
            criticalVendors=[],
            riskTrendData=[],
            complianceSummary=[],
        )

    # Aggregate score
    aggregate = round(sum(v.composite_score for v in vendors) / len(vendors))

    # Band counts
    band_counts = {"critical": 0, "high": 0, "watch": 0, "stable": 0}
    for v in vendors:
        if v.risk_band in band_counts:
            band_counts[v.risk_band] += 1

    # Active CERT-In clocks
    clocks = []
    for v in vendors:
        clock = v.cert_in_clock_dict()
        if clock:
            clocks.append(CertInClockSummary(
                vendorId=v.id,
                vendorName=v.name,
                remaining=clock["remaining"],
            ))

    # New alerts count
    alert_result = await db.execute(
        select(func.count(Alert.id)).where(Alert.status == "new")
    )
    new_alerts_count = alert_result.scalar() or 0

    # Critical + high vendors sorted by score
    critical_vendors = []
    for v in sorted(vendors, key=lambda x: x.composite_score):
        if v.risk_band in ("critical", "high"):
            change = (v.composite_score - v.previous_score) if v.previous_score else 0
            trigger = v.triggers[0] if v.triggers else ""
            critical_vendors.append(CriticalVendorSummary(
                id=v.id,
                name=v.name,
                compositeScore=v.composite_score,
                change=change,
                trigger=trigger,
                riskBand=v.risk_band,
            ))

    # Risk trend data
    trend_result = await db.execute(
        select(RiskTrendSnapshot)
        .order_by(RiskTrendSnapshot.snapshot_date.asc())
        .limit(30)
    )
    trend_data = [
        RiskTrendPoint(
            date=t.snapshot_date.strftime("%b %d"),
            score=t.aggregate_score,
            critical=t.critical_count,
            high=t.high_count,
            watch=t.watch_count,
        )
        for t in trend_result.scalars().all()
    ]

    # Compliance summary
    comp_result = await db.execute(select(ComplianceStatus))
    comp_data = [
        ComplianceSummaryItem(
            regulation=c.regulation,
            category=c.category,
            score=c.score,
            status=c.status,
        )
        for c in comp_result.scalars().all()
    ]

    return DashboardSummary(
        aggregateScore=aggregate,
        vendorCountsByBand=band_counts,
        activeCertInClocks=clocks,
        newAlertsCount=new_alerts_count,
        criticalVendors=critical_vendors,
        riskTrendData=trend_data,
        complianceSummary=comp_data,
    )
