from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.compliance import ComplianceStatus
from app.models.user import User
from app.schemas.compliance import ComplianceResponse

router = APIRouter()


@router.get("", response_model=list[ComplianceResponse])
async def list_compliance(
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    result = await db.execute(select(ComplianceStatus))
    return [
        ComplianceResponse(
            regulation=c.regulation,
            category=c.category,
            score=c.score,
            status=c.status,
            lastChecked=str(c.last_checked) if c.last_checked else None,
            gaps=c.gaps or [],
        )
        for c in result.scalars().all()
    ]
