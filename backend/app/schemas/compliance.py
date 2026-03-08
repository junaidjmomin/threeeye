from pydantic import BaseModel


class ComplianceResponse(BaseModel):
    """Matches frontend ComplianceStatus type exactly."""

    regulation: str
    category: str
    score: int
    status: str
    lastChecked: str | None
    gaps: list[str]
