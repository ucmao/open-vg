"""Celery """
from celery import Celery
import os
from dotenv import load_dotenv

load_dotenv()

# Redis ( Redis, )
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")

# Redis URL,
def get_redis_url_with_db(base_url: str, db_number: int) -> str:
    """ Redis URL"""
    # /()
    if base_url.endswith(('0', '1', '2', '3', '4', '5', '6', '7', '8', '9')):
        #  '/'
        last_slash = base_url.rfind('/')
        if last_slash > 0:
            #  '/'
            db_part = base_url[last_slash + 1:]
            if db_part.isdigit():
                base_url = base_url[:last_slash]
    
    return f"{base_url}/{db_number}"

CELERY_BROKER_URL = get_redis_url_with_db(REDIS_URL, 2)      #  Redis DB 2  broker
CELERY_RESULT_BACKEND = get_redis_url_with_db(REDIS_URL, 3)  #  Redis DB 3

#  Celery
celery_app = Celery(
    "aigc_platform",
    broker=CELERY_BROKER_URL,
    backend=CELERY_RESULT_BACKEND,
    include=[
        "app.tasks.workflow_tasks",  #
    ]
)

# Celery
celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    
    timezone="UTC",
    enable_utc=True,
    
    task_track_started=True,        #
    task_time_limit=3600,           # 1 hour hard time limit
    task_soft_time_limit=3300,      # 55 minutes soft time limit
    
    result_expires=86400,           #  24
    
    # Worker
    worker_prefetch_multiplier=1,  # 1 ()
    worker_max_tasks_per_child=100,  # Worker 100 ()
    
    # task_routes={
    #     "app.tasks.workflow_tasks.execute_workflow_task": {"queue": "workflow"},
    # },
    
    task_acks_late=True,
    task_reject_on_worker_lost=True,  # Worker ()
)
