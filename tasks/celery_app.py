from celery import Celery
from celery.schedules import crontab
import os
from dotenv import load_dotenv

load_dotenv()

redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")

celery_app = Celery(
    "emploi_tasks",
    broker=redis_url,
    backend=redis_url,
    include=['tasks.tasks']
)

celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='Africa/Abidjan',
    enable_utc=True,
)

# Planification automatique intégrée
celery_app.conf.beat_schedule = {
    'actualisation-marche-emploi-hebdomadaire': {
        'task': 'run_scraping_pipeline',
        'schedule': crontab(hour=2, minute=0, day_of_week='monday'),
        'args': ()
    },
}

