#!/bin/bash
celery -A backend.core.celery_app worker --loglevel=info -P solo &

# Start Uvicorn FastAPI server in the foreground
uvicorn backend.api.main:app --host 0.0.0.0 --port 8000
