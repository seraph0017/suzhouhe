"""
ARQ Worker Settings
"""

from arq import cron
from app.services.worker import WorkerSettings

# ARQ worker configuration
redis_host = "localhost"
redis_port = 6379

# Worker settings
worker_settings = WorkerSettings

# Cron jobs
cron_jobs = [
    cron("app.services.worker.cleanup_old_jobs", second=0, minute=0),  # Daily at midnight
    cron("app.services.worker.health_check_providers", second=0, minute=5),  # Every 5 minutes
]
