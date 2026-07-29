#!/bin/bash
# Start Uvicorn FastAPI server in the foreground
uvicorn backend.api.main:app --host 0.0.0.0 --port 8000
