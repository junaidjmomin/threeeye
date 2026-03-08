import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.workflow import WorkflowItem
from app.models.vendor import Vendor
from app.models.user import User
from app.schemas.workflow import WorkflowResponse, WorkflowCreateRequest, WorkflowUpdateRequest

router = APIRouter()


def workflow_to_response(w: WorkflowItem) -> WorkflowResponse:
    return WorkflowResponse(
        id=w.id,
        vendorId=w.vendor_id,
        vendorName=w.vendor_name,
        title=w.title,
        priority=w.priority,
        status=w.status,
        assignedTo=w.assigned_to,
        assignedRole=w.assigned_role,
        createdAt=w.created_at.isoformat(),
        dueDate=w.due_date.isoformat() if w.due_date else None,
        resolution=w.resolution,
        auditTrailId=w.audit_trail_id,
    )


@router.get("", response_model=list[WorkflowResponse])
async def list_workflows(
    status_filter: str | None = None,
    priority: str | None = None,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    query = select(WorkflowItem).order_by(WorkflowItem.created_at.desc())
    if status_filter:
        query = query.where(WorkflowItem.status == status_filter)
    if priority:
        query = query.where(WorkflowItem.priority == priority)
    result = await db.execute(query)
    return [workflow_to_response(w) for w in result.scalars().all()]


@router.get("/{workflow_id}", response_model=WorkflowResponse)
async def get_workflow(
    workflow_id: str,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    result = await db.execute(select(WorkflowItem).where(WorkflowItem.id == workflow_id))
    w = result.scalar_one_or_none()
    if w is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workflow not found")
    return workflow_to_response(w)


@router.post("", response_model=WorkflowResponse, status_code=status.HTTP_201_CREATED)
async def create_workflow(
    body: WorkflowCreateRequest,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    # Look up vendor name for denormalization
    result = await db.execute(select(Vendor).where(Vendor.id == body.vendor_id))
    vendor = result.scalar_one_or_none()
    if vendor is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vendor not found")

    audit_id = f"AUD-{uuid.uuid4().hex[:8].upper()}"
    w = WorkflowItem(
        vendor_id=body.vendor_id,
        vendor_name=vendor.name,
        title=body.title,
        priority=body.priority,
        assigned_to=body.assigned_to,
        assigned_role=body.assigned_role,
        audit_trail_id=audit_id,
    )
    db.add(w)
    await db.flush()
    await db.refresh(w)
    return workflow_to_response(w)


@router.patch("/{workflow_id}", response_model=WorkflowResponse)
async def update_workflow(
    workflow_id: str,
    body: WorkflowUpdateRequest,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    result = await db.execute(select(WorkflowItem).where(WorkflowItem.id == workflow_id))
    w = result.scalar_one_or_none()
    if w is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workflow not found")

    update_data = body.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(w, key, value)
    await db.flush()
    await db.refresh(w)
    return workflow_to_response(w)
