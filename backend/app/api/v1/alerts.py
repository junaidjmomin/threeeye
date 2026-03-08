from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.alert import Alert
from app.models.user import User
from app.schemas.alert import AlertResponse, AlertStatusUpdate

router = APIRouter()


def alert_to_response(a: Alert) -> AlertResponse:
    return AlertResponse(
        id=a.id,
        vendorId=a.vendor_id,
        vendorName=a.vendor_name,
        severity=a.severity,
        title=a.title,
        description=a.description,
        dimension=a.dimension,
        timestamp=a.created_at.isoformat(),
        status=a.status,
        assignedTo=a.assigned_to,
    )


@router.get("", response_model=list[AlertResponse])
async def list_alerts(
    severity: str | None = None,
    status_filter: str | None = None,
    vendor_id: str | None = None,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    query = select(Alert).order_by(Alert.created_at.desc())
    if severity:
        query = query.where(Alert.severity == severity)
    if status_filter:
        query = query.where(Alert.status == status_filter)
    if vendor_id:
        query = query.where(Alert.vendor_id == vendor_id)
    result = await db.execute(query)
    return [alert_to_response(a) for a in result.scalars().all()]


@router.get("/{alert_id}", response_model=AlertResponse)
async def get_alert(
    alert_id: str,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    result = await db.execute(select(Alert).where(Alert.id == alert_id))
    alert = result.scalar_one_or_none()
    if alert is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Alert not found")
    return alert_to_response(alert)


@router.patch("/{alert_id}/status", response_model=AlertResponse)
async def update_alert_status(
    alert_id: str,
    body: AlertStatusUpdate,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    result = await db.execute(select(Alert).where(Alert.id == alert_id))
    alert = result.scalar_one_or_none()
    if alert is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Alert not found")

    alert.status = body.status
    if body.assigned_to is not None:
        alert.assigned_to = body.assigned_to
    await db.flush()
    await db.refresh(alert)
    return alert_to_response(alert)
