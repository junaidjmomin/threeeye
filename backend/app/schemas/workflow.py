from pydantic import BaseModel, ConfigDict, Field


class WorkflowResponse(BaseModel):
    """Matches frontend WorkflowItem type exactly."""

    id: str
    vendorId: str
    vendorName: str
    title: str
    priority: str
    status: str
    assignedTo: str | None = None
    assignedRole: str | None = None
    createdAt: str
    dueDate: str | None
    resolution: str | None = None
    auditTrailId: str


class WorkflowCreateRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    vendor_id: str = Field(alias="vendorId")
    title: str
    priority: str = "medium"
    assigned_to: str | None = Field(default=None, alias="assignedTo")
    assigned_role: str | None = Field(default=None, alias="assignedRole")
    due_date: str | None = Field(default=None, alias="dueDate")


class WorkflowUpdateRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    status: str | None = None
    resolution: str | None = None
    assigned_to: str | None = Field(default=None, alias="assignedTo")
