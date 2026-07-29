import os

from celery import Celery
from dotenv import load_dotenv


load_dotenv()


def get_env_var(name, default=""):
    val = os.getenv(name)
    if val is not None:
        val = val.strip()
    return val if val else default


REDIS_URL = get_env_var(
    "REDIS_URL",
    "redis://localhost:6379/0"
)

# Automatically add ssl_cert_reqs=none for rediss:// URLs
if REDIS_URL.startswith("rediss://") and "ssl_cert_reqs" not in REDIS_URL:
    if "?" in REDIS_URL:
        REDIS_URL += "&ssl_cert_reqs=none"
    else:
        REDIS_URL += "?ssl_cert_reqs=none"

CELERY_BROKER_URL = get_env_var(
    "CELERY_BROKER_URL",
    REDIS_URL
)

if CELERY_BROKER_URL.startswith("rediss://") and "ssl_cert_reqs" not in CELERY_BROKER_URL:
    if "?" in CELERY_BROKER_URL:
        CELERY_BROKER_URL += "&ssl_cert_reqs=none"
    else:
        CELERY_BROKER_URL += "?ssl_cert_reqs=none"

CELERY_RESULT_BACKEND = get_env_var(
    "CELERY_RESULT_BACKEND",
    REDIS_URL
)

if CELERY_RESULT_BACKEND.startswith("rediss://") and "ssl_cert_reqs" not in CELERY_RESULT_BACKEND:
    if "?" in CELERY_RESULT_BACKEND:
        CELERY_RESULT_BACKEND += "&ssl_cert_reqs=none"
    else:
        CELERY_RESULT_BACKEND += "?ssl_cert_reqs=none"


celery_app = Celery(
    "resume_processing",
    broker=CELERY_BROKER_URL,
    backend=CELERY_RESULT_BACKEND,
    include=[
        "backend.tasks.resume_tasks"
    ]
)


celery_app.conf.update(
    accept_content=[
        "json"
    ],
    task_serializer="json",
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    worker_prefetch_multiplier=1
)
