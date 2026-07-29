#!/bin/bash
# Start Celery worker in the background
celery -A backend.core.celery_app worker --loglevel=info &

# Start Uvicorn FastAPI server in the foreground
uvicorn backend.api.main:app --host 0.0.0.0 --port 8000
