from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.vendor import Vendor
from app.schemas.vendor import VendorResponse, DimensionsSchema


def vendor_to_response(v: Vendor) -> VendorResponse:
    """Convert ORM Vendor to the exact response shape the frontend expects."""
    return VendorResponse(
        id=v.id,
        name=v.name,
        category=v.category,
        compositeScore=v.composite_score,
        previousScore=v.previous_score,
        riskBand=v.risk_band,
        tier=v.tier,
        contractExpiry=str(v.contract_expiry) if v.contract_expiry else None,
        lastAssessed=v.last_assessed.isoformat() if v.last_assessed else None,
        dimensions=DimensionsSchema(
            cybersecurity=v.score_cybersecurity,
            regulatory=v.score_regulatory,
            operational=v.score_operational,
            newsLegal=v.score_news_legal,
            financialHealth=v.score_financial_health,
            dataPrivacy=v.score_data_privacy,
            concentration=v.score_concentration,
            esg=v.score_esg,
            fourthParty=v.score_fourth_party,
        ),
        triggers=v.triggers or [],
        certInClock=v.cert_in_clock_dict(),
    )


async def get_all_vendors(
    db: AsyncSession,
    band: str | None = None,
    tier: str | None = None,
    search: str | None = None,
) -> list[VendorResponse]:
    query = select(Vendor)
    if band:
        query = query.where(Vendor.risk_band == band)
    if tier:
        query = query.where(Vendor.tier == tier)
    if search:
        query = query.where(Vendor.name.ilike(f"%{search}%"))
    query = query.order_by(Vendor.composite_score.asc())
    result = await db.execute(query)
    return [vendor_to_response(v) for v in result.scalars().all()]


async def get_vendor_by_id(db: AsyncSession, vendor_id: str) -> VendorResponse | None:
    result = await db.execute(select(Vendor).where(Vendor.id == vendor_id))
    v = result.scalar_one_or_none()
    if v is None:
        return None
    return vendor_to_response(v)
