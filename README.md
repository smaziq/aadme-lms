# AADME LMS (A1)

Thin learning management app for AADME: Django REST API (`backend/`) and React + Vite student/admin UI (`frontend/`). Students browse enrolled programs, open lessons, download assets, and mark lessons complete. Admins manage catalog content, enrollments, and progress.

**Out of scope for A1:** CRM enrollment sync (nullable `crm_person_id` seams only), live Zoom sessions (`LiveSessionProvider` stub in `backend/providers/live_session.py`), quizzes, certificates, and assignment submission UI. See `docs/superpowers/specs/2026-11-26-aadme-lms-a1-design.md`.

## Prerequisites

- Python 3.12+
- Node.js 20+ (for the frontend)

## Backend setup

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # optional; defaults work for local dev
python manage.py migrate
```

### Run API (port 8765)

Vite proxies `/api` to this port (see `frontend/vite.config.ts`).

```bash
cd backend && source .venv/bin/activate
python manage.py runserver 8765
```

Create a staff user for the admin UI:

```bash
python manage.py createsuperuser
```

## Frontend setup

```bash
cd frontend
npm install
cp .env.example .env   # optional when using the Vite dev proxy
npm run dev
```

Open http://localhost:5173 (default Vite port). With the dev server running, API calls under `/api` proxy to `http://127.0.0.1:8765`.

Production builds: `npm run build` then serve `frontend/dist/` behind your web server; set `VITE_API_BASE` to the public API origin if it differs from the SPA host.

## Tests

```bash
cd backend && source .venv/bin/activate && pytest -v
```

Tests use SQLite and local filesystem storage (`LMS_USE_LOCAL_STORAGE`); they do not require Postgres or Supabase.

### Production checklist

**App / Django**

- [ ] `DJANGO_DEBUG=0` and a strong `DJANGO_SECRET_KEY`
- [ ] `DATABASE_URL` pointing at Postgres (`psycopg` is in `requirements.txt`)
- [ ] `LMS_USE_LOCAL_STORAGE=0` with Supabase S3-compatible `AWS_*` vars (see below)
- [ ] `AWS_S3_ADDRESSING_STYLE=path` for Supabase Storage
- [ ] `DJANGO_ALLOWED_HOSTS` includes your Railway hostname (auto-added when `RAILWAY_PUBLIC_DOMAIN` is set)
- [ ] `CSRF_TRUSTED_ORIGINS` / `CORS_ALLOWED_ORIGINS` include `https://<your-railway-domain>` (same-origin SPA can omit CORS; set for extra origins)
- [ ] `FRONTEND_BASE_URL=https://<your-railway-domain>` so invite links point at production
- [ ] Leave `VITE_API_BASE` empty so the SPA calls same-origin `/api`
- [ ] Single Docker service builds the Vite SPA + runs gunicorn (see `Dockerfile` / `railway.toml`)
- [ ] Start command runs migrations: `scripts/railway-start.sh` (`migrate` → `collectstatic` → gunicorn)
- [ ] Health check: `GET /api/health/` → `{"status":"ok"}`

**Railway**

1. Create a project and add a **Postgres** plugin (sets `DATABASE_URL`).
2. Create a service from this repo (Docker builder; `railway.toml` points at the Dockerfile).
3. Generate a public domain for the service.
4. Set the variables in the table below (at minimum Django + Supabase Storage).
5. Deploy; confirm `/api/health/` and the login page load.
6. Create a staff user: `railway run python manage.py createsuperuser` (or Railway shell).

**Supabase Storage (S3-compatible)**

1. In Supabase → Storage, create a private bucket (e.g. `aadme-lms`).
2. Project Settings → API / Storage: note the project URL and create an S3 access key (Settings → Storage → S3 access keys), or use the project’s S3 credentials.
3. Set on Railway:
   - `AWS_ACCESS_KEY_ID` / `AWS_SECRET_ACCESS_KEY` — S3 access key pair
   - `AWS_STORAGE_BUCKET_NAME` — bucket name
   - `AWS_S3_ENDPOINT_URL` — `https://<project-ref>.supabase.co/storage/v1/s3`
   - `AWS_S3_REGION_NAME` — your Supabase region (e.g. `ap-south-1`)
   - `AWS_S3_ADDRESSING_STYLE=path`
   - `LMS_USE_LOCAL_STORAGE=0`

### Student asset downloads

Lesson files are streamed from `GET /api/me/assets/{id}/download/` with the student token (works for local storage and S3). The student UI uses this endpoint instead of raw `local://` URLs.

## Deploy on Railway

```bash
# From repo root (requires Railway CLI login)
railway login
railway init          # or link an existing project
railway add --database postgres
railway up
railway domain        # generate https://*.up.railway.app
```

Set production env vars in the Railway dashboard (or `railway variables set KEY=value`). After the first deploy, open `https://<domain>/api/health/` and `https://<domain>/` (SPA login).

## Environment variables

Copy examples from the repo root, `backend/.env.example`, and `frontend/.env.example`.

| Variable | Where | Purpose |
|----------|-------|---------|
| `DJANGO_SECRET_KEY` | backend | Django secret; required in production |
| `DJANGO_DEBUG` | backend | `0` in production |
| `DATABASE_URL` | backend | Postgres URL; unset → SQLite at `backend/db.sqlite3` |
| `LMS_USE_LOCAL_STORAGE` | backend | Defaults to `1` when `DJANGO_DEBUG=1`, else `0`. `1` = local disk; `0` = S3-compatible (required in production) |
| `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_STORAGE_BUCKET_NAME`, `AWS_S3_ENDPOINT_URL`, `AWS_S3_REGION_NAME` | backend | Supabase Storage (S3-compatible) when `LMS_USE_LOCAL_STORAGE=0` |
| `AWS_S3_ADDRESSING_STYLE` | backend | Use `path` for Supabase |
| `FRONTEND_BASE_URL` | backend | Base URL for invite/set-password links (production: your Railway HTTPS URL) |
| `CORS_ALLOWED_ORIGINS` | backend | Comma-separated browser origins; same-origin SPA may leave default unused |
| `CSRF_TRUSTED_ORIGINS` | backend | Comma-separated HTTPS origins; Railway domain auto-added from `RAILWAY_PUBLIC_DOMAIN` |
| `DJANGO_ALLOWED_HOSTS` | backend | Hostnames; Railway public domain auto-added |
| `VITE_API_BASE` | frontend | Optional API origin; leave empty for same-origin (Railway) or Vite proxy (dev) |

Other backend knobs: `EMAIL_BACKEND`, `DEFAULT_FROM_EMAIL`, `SECURE_SSL_REDIRECT`, `FRONTEND_DIST_DIR`.

## Auth

DRF **Token** authentication: `POST /api/auth/login/` returns a token; send `Authorization: Token <key>` on subsequent requests.

## Project layout

- `backend/accounts` — users, invites, students
- `backend/catalog` — programs, modules, lessons, assets, storage
- `backend/learning` — enrollments, completions, student/admin APIs
- `frontend/src` — login, admin console, student portal