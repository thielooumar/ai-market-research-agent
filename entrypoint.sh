#!/bin/sh
set -e

echo "--- Runtime startup checks ---"
python -c "import os, sys; print('PYTHONPATH:', os.getenv('PYTHONPATH')); import app.tools; print('import app.tools OK'); import frontend.main; print('import frontend.main OK')"

echo "--- Starting Uvicorn ---"
exec uvicorn frontend.main:app --host 0.0.0.0 --port ${PORT:-8080}
