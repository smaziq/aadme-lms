# AADME LMS — Temporary Supabase MP4 player + DIY HLS seam

**Date:** 2026-11-26  
**Status:** Approved for implementation  
**Depends on:** A1 LMS (`2026-11-26-aadme-lms-a1-design.md`)

## 1. Goal

Students watch lesson videos in-page using Supabase-stored MP4/WebM and an HTML5 `<video>` player. Architecture leaves a clean migration path to DIY HLS (Celery/ffmpeg → segments in S3 → CDN signed access → hls.js).

## 2. Decisions

| Topic | Choice |
|-------|--------|
| Near-term delivery | Supabase Storage MP4/WebM + `<video>` |
| Browser fetch (prod) | Short-lived S3/Supabase **presigned GET** (`delivery: mp4_signed`) |
| Local/dev fetch | API **stream** URL (`delivery: mp4_proxy`) so `<video>` works without S3 |
| Long-term | DIY HLS on Supabase/S3 + CDN + hls.js (not in this slice) |
| Live | Still out of scope (B1 `LiveSessionProvider`) |
| django CMS / Mux / Bunny | Not used |

## 3. Non-goals (this slice)

- ffmpeg, Celery, HLS packaging, CDN, signed cookies
- Watch-% completion, DRM, captions pipeline
- Replacing PDF/file downloads
- New `LessonVideo` model (deferred until HLS; playback descriptor is the seam)

## 4. Data model

Reuse **`LessonAsset`**.

- Video MIME: `content_type` starts with `video/`
- Storage key preference: `lessons/{program_id}/{lesson_id}/videos/{safe_filename}` (masters for a future encoder)
- Non-video keys unchanged: `lessons/{program_id}/{lesson_id}/{safe_filename}`

## 5. Student API shape (HLS seam)

Each asset in `GET /api/me/lessons/{id}/` includes:

| Field | Video | Non-video |
|-------|-------|-----------|
| `kind` | `"video"` | `"file"` |
| `delivery` | `"mp4_signed"` or `"mp4_proxy"` | omitted / `"download"` |
| `playback_url` | presigned or `/api/me/assets/{id}/stream/` | null |
| `playback_expires_at` | ISO timestamp when signed; null for proxy | null |
| `download_url` | still available | as today |

Optional: `GET /api/me/assets/{id}/playback/` refreshes signed URL (enrollment-gated).

Later HLS: same fields with `delivery: "hls"` and CDN `master.m3u8` URL; React switches player by `delivery`.

## 6. Backend behavior

- Admin multipart/presign upload: if video MIME → use `videos/` key prefix
- `StorageService.presign_download` for production playback URLs (default expiry ~600–900s)
- `GET /api/me/assets/{id}/stream/`: enrollment check; stream bytes **inline** (not attachment); local filesystem preferred path for Range-friendly `FileResponse`
- Unenrolled → 404 (same as download)

## 7. Frontend

- Student lesson page: video assets → `<video controls playsInline src={playback_url} />`
- On 403 / near expiry → call playback refresh when available
- Non-video → existing download buttons
- Admin: label uploads as Video vs File by MIME; soft guidance for large files

## 8. Migration path (documented only)

1. Add `LessonVideo` (`status`, `master_key`, `hls_prefix`, duration)
2. Worker: ffmpeg → `videos/hls/{id}/…` in bucket
3. CDN + signed cookies/tokens
4. Payload `delivery: "hls"`; mount hls.js
5. Keep `mp4_signed` as fallback while processing

## 9. Success criteria

- Admin can upload an mp4 on a lesson
- Enrolled student sees in-page playback
- Unenrolled student cannot obtain playback
- PDF/other assets unchanged
- README notes temporary MP4 + planned HLS migration

## 10. Spec self-review

- No TBD placeholders
- Aligns with A1 storage (Supabase S3, no Railway disk)
- Seam fields avoid forcing `LessonVideo` before HLS
- Local vs prod delivery modes explicit so tests and Railway both work
