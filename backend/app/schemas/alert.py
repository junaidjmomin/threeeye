from typing import Literal

from pydantic import BaseModel

AlertStatus = Literal["new", "acknowledged", "assigned", "resolved", "dismissed"]


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
    status: AlertStatus
    assigned_to: str | None = None
