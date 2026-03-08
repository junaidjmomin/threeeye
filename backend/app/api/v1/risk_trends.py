from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.risk_trend import RiskTrendSnapshot
from app.models.user import User
from app.schemas.dashboard import RiskTrendPoint

router = APIRouter()


@router.get("", response_model=list[RiskTrendPoint])
async def get_risk_trends(
    days: int = 30,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(RiskTrendSnapshot)
        .order_by(RiskTrendSnapshot.snapshot_date.desc())
        .limit(days)
    )
    snapshots = list(reversed(result.scalars().all()))
    return [
        RiskTrendPoint(
            date=s.snapshot_date.strftime("%b %d"),
            score=s.aggregate_score,
            critical=s.critical_count,
            high=s.high_count,
            watch=s.watch_count,
        )
        for s in snapshots
    ]
