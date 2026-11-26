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

## Environment variables

Copy examples from the repo root, `backend/.env.example`, and `frontend/.env.example`.

| Variable | Where | Purpose |
|----------|-------|---------|
| `DJANGO_SECRET_KEY` | backend | Django secret; required in production |
| `DATABASE_URL` | backend | Optional Postgres URL (`postgres://...`); unset → SQLite at `backend/db.sqlite3` |
| `LMS_USE_LOCAL_STORAGE` | backend | `1` (default) stores uploads on disk; `0` uses S3-compatible storage |
| `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_STORAGE_BUCKET_NAME`, `AWS_S3_ENDPOINT_URL`, `AWS_S3_REGION_NAME` | backend | Supabase Storage (S3-compatible) when `LMS_USE_LOCAL_STORAGE=0` |
| `FRONTEND_BASE_URL` | backend | Base URL for invite/set-password links (default `http://localhost:5173`) |
| `CORS_ALLOWED_ORIGINS` | backend | Comma-separated browser origins allowed to call the API |
| `VITE_API_BASE` | frontend | Optional API origin; leave empty in dev to use the Vite proxy |

Other backend knobs: `DJANGO_DEBUG`, `DJANGO_ALLOWED_HOSTS`, `EMAIL_BACKEND`, `DEFAULT_FROM_EMAIL`.

## Auth

DRF **Token** authentication: `POST /api/auth/login/` returns a token; send `Authorization: Token <key>` on subsequent requests.

## Project layout

- `backend/accounts` — users, invites, students
- `backend/catalog` — programs, modules, lessons, assets, storage
- `backend/learning` — enrollments, completions, student/admin APIs
- `frontend/src` — login, admin console, student portal