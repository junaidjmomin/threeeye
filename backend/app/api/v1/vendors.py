from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.score_audit_log import ScoreAuditLog
from app.models.user import User
from app.models.vendor import Vendor
from app.schemas.vendor import VendorCreateRequest, VendorResponse, VendorUpdateRequest
from app.services.vendor_service import get_all_vendors, get_vendor_by_id, vendor_to_response

router = APIRouter()


@router.get("", response_model=list[VendorResponse])
async def list_vendors(
    band: str | None = None,
    tier: str | None = None,
    search: str | None = None,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    return await get_all_vendors(db, band=band, tier=tier, search=search)


@router.get("/{vendor_id}", response_model=VendorResponse)
async def get_vendor(
    vendor_id: str,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    vendor = await get_vendor_by_id(db, vendor_id)
    if vendor is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vendor not found")
    return vendor


@router.post("", response_model=VendorResponse, status_code=status.HTTP_201_CREATED)
async def create_vendor(
    body: VendorCreateRequest,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    vendor = Vendor(
        name=body.name,
        category=body.category,
        tier=body.tier,
    )
    db.add(vendor)
    await db.flush()
    await db.refresh(vendor)
    return vendor_to_response(vendor)


@router.patch("/{vendor_id}", response_model=VendorResponse)
async def update_vendor(
    vendor_id: str,
    body: VendorUpdateRequest,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    result = await db.execute(select(Vendor).where(Vendor.id == vendor_id))
    vendor = result.scalar_one_or_none()
    if vendor is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vendor not found")

    update_data = body.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(vendor, key, value)
    await db.flush()
    await db.refresh(vendor)
    return vendor_to_response(vendor)


@router.get("/{vendor_id}/history")
async def get_vendor_history(
    vendor_id: str,
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(ScoreAuditLog)
        .where(ScoreAuditLog.vendor_id == vendor_id)
        .order_by(ScoreAuditLog.created_at.desc())
        .limit(limit)
    )
    logs = result.scalars().all()
    return [
        {
            "id": log.id,
            "oldComposite": log.old_composite,
            "newComposite": log.new_composite,
            "oldBand": log.old_band,
            "newBand": log.new_band,
            "dimensionAffected": log.dimension_affected,
            "triggerSignal": log.trigger_signal,
            "modelVersion": log.model_version,
            "ruleActivated": log.rule_activated,
            "regulatoryCitation": log.regulatory_citation,
            "recommendedAction": log.recommended_action,
            "actor": log.actor,
            "timestamp": log.created_at.isoformat(),
        }
        for log in logs
    ]
