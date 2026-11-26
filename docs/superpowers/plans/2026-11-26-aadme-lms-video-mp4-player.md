# Temporary Supabase MP4 Lesson Player Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Enrolled students play lesson video assets in-page via temporary MP4/WebM delivery, with API fields that later swap to DIY HLS.

**Architecture:** Extend `LessonAsset` + student serializers with `kind` / `delivery` / `playback_url`. Production uses S3 presigned GET; local uses `/api/me/assets/{id}/stream/`. React lesson page renders `<video>` for `kind=video`.

**Tech Stack:** Django/DRF, boto3 StorageService, React + Vite (existing)

## Global Constraints

- No ffmpeg/Celery/HLS/CDN in this slice
- Private bucket only; no permanent public URLs
- Keep non-video download behavior unchanged
- Branch: continue on `cursor/railway-deploy-7db9` (or current working branch)

## File map

| File | Responsibility |
|------|----------------|
| `backend/catalog/storage.py` | `lesson_video_key`, video MIME helper |
| `backend/learning/serializers.py` | Student asset playback fields |
| `backend/learning/views.py` + `student_urls.py` | Stream + optional playback refresh |
| `backend/catalog/views.py` | Video key prefix on upload |
| `backend/learning/tests/test_student_api.py` | Playback / stream tests |
| `frontend/src/api/student.ts` | Types |
| `frontend/src/pages/student/LessonPage.tsx` | `<video>` UI |
| `README.md` | Temporary MP4 + HLS note |

---

### Task 1: Storage helpers + student playback fields

**Files:** `catalog/storage.py`, `learning/serializers.py`, tests

- [ ] Add `is_video_content_type(ct)` and `lesson_video_key(...)`
- [ ] Extend `StudentLessonAssetSerializer` with `kind`, `delivery`, `playback_url`, `playback_expires_at`
- [ ] Tests: video asset returns `kind=video` and a playback URL; file asset unchanged download

### Task 2: Stream + playback endpoints; video upload key

**Files:** `learning/views.py`, `learning/student_urls.py`, `catalog/views.py`, tests

- [ ] `GET /api/me/assets/{id}/stream/` inline stream (enrollment-gated)
- [ ] `GET /api/me/assets/{id}/playback/` refresh descriptor
- [ ] Admin upload uses `lesson_video_key` when MIME is video
- [ ] Tests for stream 200 enrolled / 404 unenrolled

### Task 3: Frontend player + README

**Files:** `frontend/src/api/student.ts`, `LessonPage.tsx`, `README.md`

- [ ] Types for new fields
- [ ] Render `<video>` for video assets; keep downloads for files
- [ ] Document temporary MP4 + future HLS in README

### Task 4: Verify + ship

- [ ] `pytest` green; frontend build OK
- [ ] Commit, push, Railway redeploy
