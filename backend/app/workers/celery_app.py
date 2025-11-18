"""
Celery application configuration
"""
from celery import Celery
from celery.schedules import crontab
from app.core.config import settings

# Create Celery app
celery_app = Celery(
    "knowledge_graph_workers",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=["app.workers.tasks"]
)

# Celery configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600,  # 1 hour
    task_soft_time_limit=3000,  # 50 minutes
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
)

# Periodic tasks schedule
celery_app.conf.beat_schedule = {
    # Background sync for all integrations
    "sync-all-integrations": {
        "task": "app.workers.tasks.sync_all_integrations",
        "schedule": settings.BACKGROUND_SYNC_INTERVAL,
    },
    # Discover new connections
    "discover-connections": {
        "task": "app.workers.tasks.discover_connections_task",
        "schedule": settings.CONNECTION_DISCOVERY_INTERVAL,
    },
    # Generate daily digest
    "daily-digest": {
        "task": "app.workers.tasks.generate_digest_task",
        "schedule": crontab(hour=8, minute=0),  # 8 AM daily
        "kwargs": {"days": 1}
    },
    # Weekly comprehensive analysis
    "weekly-analysis": {
        "task": "app.workers.tasks.weekly_comprehensive_analysis",
        "schedule": crontab(day_of_week=1, hour=9, minute=0),  # Monday 9 AM
    },
}

if __name__ == "__main__":
    celery_app.start()
