# AADME LMS — single Railway service: API + built SPA
FROM node:22-bookworm AS frontend
WORKDIR /app/frontend
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

FROM python:3.12-slim-bookworm
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends libpq5 \
    && rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt /app/requirements.txt
RUN pip install --upgrade pip && pip install -r /app/requirements.txt

COPY backend/ /app/
COPY --from=frontend /app/frontend/dist /app/frontend_dist

# Collect static at build time; runtime migrate + collectstatic also run on start
ENV DJANGO_SETTINGS_MODULE=config.settings \
    DJANGO_DEBUG=0 \
    LMS_USE_LOCAL_STORAGE=1 \
    FRONTEND_DIST_DIR=/app/frontend_dist

RUN DJANGO_SECRET_KEY=build-only python manage.py collectstatic --noinput

COPY scripts/railway-start.sh /app/railway-start.sh
RUN chmod +x /app/railway-start.sh

EXPOSE 8000
CMD ["/app/railway-start.sh"]
