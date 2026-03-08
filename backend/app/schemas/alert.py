from pydantic import BaseModel


class AlertResponse(BaseModel):
    """Matches frontend Alert type exactly."""

    id: str
    vendorId: str
    vendorName: str
    severity: str
    title: str
    description: str | None
    dimension: str | None
    timestamp: str
    status: str
    assignedTo: str | None = None


class AlertStatusUpdate(BaseModel):
    status: str
    assigned_to: str | None = None
