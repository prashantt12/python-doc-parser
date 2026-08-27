#!/bin/sh
set -e

cd /app
.venv/bin/alembic upgrade head
exec .venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
