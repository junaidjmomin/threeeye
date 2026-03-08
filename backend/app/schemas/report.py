from pydantic import BaseModel


class ReportResponse(BaseModel):
    id: str
    title: str
    reportType: str
    regulation: str | None
    status: str
    generatedAt: str | None
