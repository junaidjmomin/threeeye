from celery import Celery
from celery.schedules import crontab

from app.core.config import settings

celery_app = Celery(
    "thirdeye",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Kolkata",
    enable_utc=True,
    task_routes={
        "tasks.rescore_*": {"queue": "scoring"},
        "tasks.process_score_change": {"queue": "alerts"},
        "tasks.*": {"queue": "default"},
    },
)

celery_app.conf.beat_schedule = {
    # Scoring
    "rescore-all-vendors-every-6h": {
        "task": "tasks.rescore_all_vendors",
        "schedule": crontab(hour="*/6", minute=0),
    },
    "daily-risk-trend-snapshot": {
        "task": "tasks.take_risk_trend_snapshot",
        "schedule": crontab(hour=0, minute=5),
    },
    # Compliance
    "run-compliance-rules-hourly": {
        "task": "tasks.run_compliance_rules",
        "schedule": crontab(minute=15),
    },
    # Ingestion
    "ingest-news-every-15m": {
        "task": "tasks.ingest_news",
        "schedule": crontab(minute="*/15"),
    },
    "ingest-cve-hourly": {
        "task": "tasks.ingest_cve",
        "schedule": crontab(minute=30),
    },
    "ingest-cert-in-hourly": {
        "task": "tasks.ingest_cert_in",
        "schedule": crontab(minute=45),
    },
    "ingest-rbi-enforcement-every-6h": {
        "task": "tasks.ingest_rbi_enforcement",
        "schedule": crontab(hour="*/6", minute=10),
    },
    "ingest-shodan-every-6h": {
        "task": "tasks.ingest_shodan",
        "schedule": crontab(hour="*/6", minute=20),
    },
    "ingest-hibp-daily": {
        "task": "tasks.ingest_hibp",
        "schedule": crontab(hour=1, minute=0),
    },
}

# Auto-discover tasks
celery_app.autodiscover_tasks(["app.workers"])
