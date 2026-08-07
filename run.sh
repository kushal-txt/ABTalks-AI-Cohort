#!/bin/bash
# Activate virtual environment
source venv/bin/activate
# Start uvicorn server on port 8000
exec uvicorn server.main:app --host 0.0.0.0 --port 8000 --reload
