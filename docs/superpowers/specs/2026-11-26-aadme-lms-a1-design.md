# AADME Learning Platform (A1): Design

- Date: 2026-11-26
- Status: Approved in brainstorming (2026-11-26); awaiting written-spec review
- Source: brainstorming for Steps A1 / B1, grounded in
  `2026-10-22-aadme-crm-design.md` (CRM + learning, source of truth) and
  `2026-10-24-aadme-crm-admissions-design.md` (admissions spine; reconciled into Oct 22 §22)
- Scope of this document: **A1 only** (thin student slice). B1 decisions that affect A1 seams are recorded; B1 behaviour is not specified in full here.

How to read this: **[Owner]** = decided with AADME in this session. **[Proposed]** = designer/builder call; stands unless AADME changes it.

## 1. Intent

AADME needs a learning product where enrolled students can open courses (programs → modules → lessons), use lesson materials, and mark lessons done. Admissions and counselling stay in the CRM. This repo is the **standalone learning app**: same Django/React family as the CRM, **separate deploy and database**, with enrolled students synced from the CRM later.

A1 is the first usable slice of that learning app. It maps to the spirit of Oct 22 §19 phase 10 (content + student login/portal) without requiring CRM phases 1–9 to exist in this repository.

## 2. Decisions locked in brainstorming [Owner]

| # | Topic | Decision |
|---|---|---|
| 1 | Where it fits | Standalone learning app: same Django stack, different deploy/repo. Sync enrolled students from CRM later. Not a phase inside the CRM process; not a merge into the CRM codebase for A1. |
| 2 | Admitted lead → student | `User` (login) + `Student` (learning profile) + `Enrollment` (program/batch access). Optional `crm_person_id` / `crm_enrollment_id` for later sync. |
| 3 | File storage | Supabase Storage via S3-compatible API (Mumbai-aligned with CRM hosting notes). |
| 4 | Live class (B1) | Provider-agnostic `LiveSessionProvider` connector; **Zoom first** when B1 ships. A1 only reserves the seam. |
| — | A1 delivery shape | **Thin student slice** (see §4). Not full Oct 22 phase 10 (no video CDN/transcoding, no timed release). |

## 3. Relation to the CRM design

- Oct 22 §13–§14 and §19 phases 10–11 describe learning inside one product. **This LMS deliberately diverges on deployment:** separate app and DB, CRM sync later. [Owner]
- Oct 22 identity rule (“lead and student are the same person record”) applied to a unified product. Here, CRM remains source of truth for *who enrolled*; the LMS owns learning profile and progress, joined by CRM IDs when sync exists. [Owner]
- Oct 22 stack (Django/DRF, React/Vite, Celery, plain Postgres, S3-compatible files, no Supabase Auth) still applies to this app. [Proposed: A1 sends invite email synchronously (or Django’s email backend); introduce Celery when B1 or sync jobs need it.]
- Admissions stage ladder and handover packets (§22) stay in the CRM. A1 does not implement admissions UI.

## 4. Goals, non-goals, anti-goals

### Goals (A1)

1. Staff can create a program with modules and lessons, attach files, and enroll a student.
2. A student can accept an invite, set a password, log in, open enrolled courses, and mark lessons done.
3. Progress is visible to staff per enrollment (completed / total).
4. Seams exist for B1 (live sessions, assignment uploads) and for CRM ID mapping without requiring those systems at runtime.

### Non-goals (A1)

- Zoom/Meet scheduling, attendance, or recordings UI
- Assignment upload and grading
- Video streaming host (Bunny/Mux), transcoding, signed stream URLs
- Timed lesson release, quizzes, certificates, at-risk dashboards
- Payments, GST, WhatsApp, CRM follow-up lists
- Live CRM sync worker (IDs only)

### Anti-goals

1. **Railway disk as durable file storage** — lesson and (later) assignment files must use Supabase Storage.
2. **Students seeing other students’ data** — object-level checks on every API.
3. **CRM required to enroll locally** — admin enroll works without sync; CRM IDs are optional.
4. **Building B1 inside A1** — no Zoom OAuth or assignment flows in this slice.

## 5. Users and roles [Proposed]

| Role | A1 capabilities |
|---|---|
| Admin | CRUD programs/modules/lessons/assets; create users/students; enroll; invite/resend; view progress |
| Mentor | Role enum exists for B1; **no A1 UI or API capabilities** beyond authenticating |
| Student | Own enrollments, lesson content, mark own lessons done |

Staff and students are Users in this app. One login per person in the LMS. Permissions enforced server-side per object, not only in the UI.

## 6. Architecture

### Services

| Piece | Choice |
|---|---|
| API | Django + Django REST Framework on Railway |
| Web | React + TypeScript + Vite SPA (separate Railway service or static host) |
| Database | Postgres owned by this LMS (Supabase Postgres or Railway Postgres) — **not** the CRM database |
| Files | Supabase Storage (S3-compatible); django-storages / boto3; signed upload and download URLs |
| Email | Transactional invite/set-password (Resend or Django email backend) [Proposed] |

### Auth

- Django’s own authentication (portable; no Supabase Auth).
- DRF session and/or token auth for the SPA. [Proposed: token or session with CSRF; pick one in implementation plan and stick to it.]
- Students: email + password after invite. Staff: email + password (2FA deferred unless already trivial).

### Boundaries

```text
┌─────────────┐     later sync      ┌──────────────────┐
│  AADME CRM  │ ─────────────────►  │  AADME Learning  │
│ (admissions)│  crm_* IDs          │  (this repo)     │
└─────────────┘                     │  api + web + db  │
                                    │       │          │
                                    │       ▼          │
                                    │ Supabase Storage │
                                    └──────────────────┘
```

## 7. Data model

### Identity and access

- **User** — email (unique), password, role (`admin` | `mentor` | `student`), `is_active`.
- **Student** — OneToOne to User (when role is student). Display name, optional phone. `crm_person_id` nullable, unique when set.
- **Enrollment** — ForeignKey to Student and Program; optional ForeignKey to Batch. Status: `active` | `paused` | `withdrawn`. `crm_enrollment_id` nullable, unique when set. Enforce **at most one `active` enrollment per student per program** (partial unique constraint). A student may have historical `paused`/`withdrawn` rows for the same program. [Proposed]

### Content

- **Program** — title, slug, description, `is_published`.
- **Module** — program, title, `order`.
- **Lesson** — module, title, `order`, body (text/markdown), optional links (JSON or related rows), `is_published`.
- **LessonAsset** — lesson, storage key, filename, content type, size. Files in Supabase Storage; DB holds metadata only.

### Progress

- **LessonCompletion** — student, lesson, `completed_at`. Unique (student, lesson). Mark-done is idempotent.

### Batch (light)

- **Batch** — program, name, optional `start_date`. Enrollment may reference a batch so B1 release/attendance can attach later without redesign.

### Reserved for B1 (no A1 UI)

- Storage key prefix convention for assignment submissions (same bucket layout).
- `LiveSessionProvider` interface; optional empty/minimal `LiveSession` table if useful for FK planning — not required to ship A1 screens.
- Mentor review queue is out of scope.

## 8. Key flows

### Admin: content

1. Create program → modules → lessons (ordered).
2. Upload lesson assets via presigned URL to Supabase Storage; API persists `LessonAsset` after successful upload metadata is confirmed.
3. Publish program/lessons when ready for enrolled students.

### Admin: enroll and invite

1. Create User (role student) + Student, or select existing Student.
2. Create Enrollment (program, optional batch, status `active`).
3. Send invite email with one-time set-password token.
4. Resend invite if token expired or unused.

Until CRM sync exists, this is how an “admitted lead” becomes a student in the LMS: staff enroll after admission/payment is known outside this app (or from CRM manually).

### Student: learn

1. Open invite link → set password → log in.
2. **My courses** lists active enrollments only.
3. Open program → module/lesson tree (published content only).
4. Lesson view: body, links, signed download URLs for assets.
5. **Mark done** creates `LessonCompletion` (idempotent). Course progress updates.

### CRM sync (later, not A1 runtime)

- Upsert Student by `crm_person_id` and Enrollment by `crm_enrollment_id`.
- Local admin enroll remains valid; sync must not wipe LMS-only progress.

## 9. API surface (sketch) [Proposed]

**Auth:** login, logout, set-password (token).

**Admin:** CRUD programs, modules, lessons, assets; create/list enrollments; invite/resend; progress by enrollment.

**Student:** `GET` current user/student; `GET` my enrollments; `GET` program tree (enrollment-scoped); `POST` mark lesson complete; `GET` signed asset download URL when enrolled.

All list/detail endpoints filter by role and enrollment. Unpublished lessons are admin-only unless explicitly allowed. [Proposed: students see published only.]

## 10. UI [Proposed]

- **Staff:** functional admin — content tree, asset upload, enroll + invite, progress counts. Not a marketing site.
- **Student:** course list → modules → lesson reader + Mark done.
- States: empty (no enrollments / no lessons), loading, error (fetch/complete/upload failures).
- Responsive web; no native apps.

Out of A1 UI: live schedule, attendance, assignments, certificates, payments.

## 11. Storage

- Bucket(s) in Supabase Storage, accessed only through S3-compatible credentials held by the API.
- Lesson assets under a stable prefix, e.g. `lessons/{program_id}/{lesson_id}/…`.
- Assignment uploads later under e.g. `assignments/{enrollment_id}/…` (B1).
- Downloads via short-lived signed URLs; students refresh the lesson to renew.
- Portability: no Supabase-only auth or non-S3 APIs in app code paths. [Proposed]

## 12. B1 seams (recorded, not built)

| Seam | A1 obligation | B1 will add |
|---|---|---|
| `LiveSessionProvider` | Interface + Zoom-first adapter planned | Schedule, join links, attendance pull, optional recordings → lessons |
| Assignments | Storage prefix reserved | Upload, mentor grade, resubmit |
| Mentor role | On User | Review queue |
| CRM sync | Nullable unique CRM IDs | Automated upsert from CRM enrollments |

Google Meet remains a possible later adapter behind the same provider interface; Zoom is first. [Owner]

## 13. Errors and edge cases

- Invite token expired or already used → message + admin resend.
- Mark done without active enrollment, or for missing/unpublished lesson → 403/404; no row.
- Duplicate mark done → success, same completion (idempotent).
- Upload failure → no orphan `LessonAsset` without a valid storage key.
- `paused` / `withdrawn` enrollment → hidden from student course list; completions retained.
- Signed URL expired → client requests a new URL by reloading lesson assets.

## 14. Testing (A1)

- API tests: role permissions; enrollment scoping; idempotent complete; invite and set-password.
- Model/constraint tests: one active enrollment per student per program; CRM ID uniqueness when set.
- Smoke path: admin content → enroll → student login → mark lesson done.
- No Zoom or assignment E2E in A1.

## 15. Build order for A1 [Proposed]

1. Repo foundation: Django + DRF, React/Vite, env, CI smoke, Postgres.
2. Users/roles, Student, auth, invite/set-password.
3. Program / Module / Lesson / LessonAsset + Supabase Storage uploads.
4. Enrollment + admin enroll UI.
5. Student portal: my courses, lesson view, mark done, progress.
6. Harden permissions tests and README (run locally + Railway notes).

B1 is a separate design/plan after A1 ships.

## 16. Open items for implementation plan (not blocking this design)

- Exact DRF auth mechanism (session vs token) for the SPA — pick one and document in the plan.
- Email provider wiring (Resend in deployed envs; console/file backend locally).
- Precise Postgres host (Supabase vs Railway) for the LMS DB — files are Supabase Storage regardless.
- Mentor: role enum only in A1 (already decided in §5); no further product choice required.

## 17. Success criteria for A1

- An admin can publish a small program with at least one file-backed lesson and enroll a student by invite.
- That student can log in, open the lesson, download the file via signed URL, and mark the lesson done.
- A second student cannot see the first student’s enrollments or completions.
- CRM and Zoom are unnecessary for the smoke path; CRM ID fields and `LiveSessionProvider` exist as documented seams.
