from fastapi import APIRouter

from app.api.v1 import auth, dashboard, vendors, alerts, workflows, compliance, reports, consortium, risk_trends

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])
api_router.include_router(vendors.router, prefix="/vendors", tags=["vendors"])
api_router.include_router(alerts.router, prefix="/alerts", tags=["alerts"])
api_router.include_router(workflows.router, prefix="/workflows", tags=["workflows"])
api_router.include_router(compliance.router, prefix="/compliance", tags=["compliance"])
api_router.include_router(reports.router, prefix="/reports", tags=["reports"])
api_router.include_router(consortium.router, prefix="/consortium", tags=["consortium"])
api_router.include_router(risk_trends.router, prefix="/risk-trends", tags=["risk-trends"])
