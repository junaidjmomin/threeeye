from pydantic import BaseModel


class WorkflowResponse(BaseModel):
    """Matches frontend WorkflowItem type exactly."""

    id: str
    vendorId: str
    vendorName: str
    title: str
    priority: str
    status: str
    assignedTo: str
    assignedRole: str
    createdAt: str
    dueDate: str | None
    resolution: str | None = None
    auditTrailId: str


class WorkflowCreateRequest(BaseModel):
    vendor_id: str
    title: str
    priority: str = "medium"
    assigned_to: str
    assigned_role: str
    due_date: str | None = None


class WorkflowUpdateRequest(BaseModel):
    status: str | None = None
    resolution: str | None = None
    assigned_to: str | None = None
