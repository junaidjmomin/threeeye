from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.consortium import ConsortiumNode, ConsortiumSignal
from app.models.user import User
from app.schemas.consortium import ConsortiumNodeResponse, ConsortiumSignalResponse

router = APIRouter()


@router.get("/nodes", response_model=list[ConsortiumNodeResponse])
async def list_consortium_nodes(
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    result = await db.execute(select(ConsortiumNode))
    return [
        ConsortiumNodeResponse(
            id=n.id,
            bank=n.bank_name,
            status=n.node_status,
            lastSignal=n.last_signal_at.isoformat() if n.last_signal_at else None,
            vendorsMonitored=n.vendors_monitored,
        )
        for n in result.scalars().all()
    ]


@router.get("/signals", response_model=list[ConsortiumSignalResponse])
async def list_consortium_signals(
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(ConsortiumSignal).order_by(ConsortiumSignal.received_at.desc()).limit(50)
    )
    return [
        ConsortiumSignalResponse(
            id=s.id,
            type=s.signal_type,
            dimension=s.dimension,
            vendorHash=s.vendor_hash,
            timestamp=s.received_at.isoformat(),
            certInRelevant=s.cert_in_relevant,
        )
        for s in result.scalars().all()
    ]
