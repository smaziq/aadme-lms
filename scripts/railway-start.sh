#!/usr/bin/env bash
set -euo pipefail

cd /app

python manage.py migrate --noinput
python manage.py collectstatic --noinput

PORT="${PORT:-8000}"
exec gunicorn config.wsgi:application \
  --bind "0.0.0.0:${PORT}" \
  --workers "${WEB_CONCURRENCY:-2}" \
  --timeout 120 \
  --access-logfile - \
  --error-logfile -
