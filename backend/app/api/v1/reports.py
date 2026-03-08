from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.report import Report
from app.models.user import User
from app.schemas.report import ReportResponse

router = APIRouter()


@router.get("", response_model=list[ReportResponse])
async def list_reports(
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    result = await db.execute(select(Report).order_by(Report.created_at.desc()))
    return [
        ReportResponse(
            id=r.id,
            title=r.title,
            reportType=r.report_type,
            regulation=r.regulation,
            status=r.status,
            generatedAt=r.generated_at.isoformat() if r.generated_at else None,
        )
        for r in result.scalars().all()
    ]
