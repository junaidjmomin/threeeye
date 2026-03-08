from pydantic import BaseModel


class ConsortiumNodeResponse(BaseModel):
    id: str
    bank: str
    status: str
    lastSignal: str | None
    vendorsMonitored: int


class ConsortiumSignalResponse(BaseModel):
    id: str
    type: str
    dimension: str | None
    vendorHash: str
    timestamp: str
    certInRelevant: bool
