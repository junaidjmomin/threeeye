from pydantic import BaseModel


class CertInClockSchema(BaseModel):
    active: bool
    remaining: str
    startedAt: str


class DimensionsSchema(BaseModel):
    cybersecurity: int
    regulatory: int
    operational: int
    newsLegal: int
    financialHealth: int
    dataPrivacy: int
    concentration: int
    esg: int
    fourthParty: int


class VendorResponse(BaseModel):
    """Matches frontend Vendor type exactly."""

    id: str
    name: str
    category: str
    compositeScore: int
    previousScore: int | None
    riskBand: str
    tier: str
    contractExpiry: str | None
    lastAssessed: str | None
    dimensions: DimensionsSchema
    triggers: list[str]
    certInClock: CertInClockSchema | None = None


class VendorCreateRequest(BaseModel):
    name: str
    category: str
    tier: str = "standard"
    contract_expiry: str | None = None


class VendorUpdateRequest(BaseModel):
    name: str | None = None
    category: str | None = None
    tier: str | None = None
    contract_expiry: str | None = None
    triggers: list[str] | None = None
