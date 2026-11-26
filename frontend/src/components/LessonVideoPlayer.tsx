import { useEffect, useState } from "react";
import type { StudentLessonAsset } from "../api/student";

type Props = {
  asset: StudentLessonAsset;
  token: string;
};

/**
 * mp4_signed → use presigned URL directly.
 * mp4_proxy → fetch with Token auth into a blob URL (<video> cannot send Authorization).
 */
export function LessonVideoPlayer({ asset, token }: Props) {
  const [src, setSrc] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    let objectUrl: string | null = null;

    async function load() {
      setError(null);
      setSrc(null);
      const url = asset.playback_url;
      if (!url) {
        setError("No playback URL.");
        return;
      }
      if (url.startsWith("http://") || url.startsWith("https://")) {
        if (!cancelled) setSrc(url);
        return;
      }
      try {
        const res = await fetch(url, {
          headers: { Authorization: `Token ${token}` },
        });
        if (!res.ok) {
          throw new Error(`Playback failed (${res.status})`);
        }
        const blob = await res.blob();
        objectUrl = URL.createObjectURL(blob);
        if (!cancelled) setSrc(objectUrl);
      } catch (err) {
        if (!cancelled) {
          setError(err instanceof Error ? err.message : "Could not load video.");
        }
      }
    }

    void load();
    return () => {
      cancelled = true;
      if (objectUrl) URL.revokeObjectURL(objectUrl);
    };
  }, [asset.playback_url, asset.id, token]);

  return (
    <li className="video-item">
      <p className="video-label">{asset.filename}</p>
      {error && (
        <div className="alert alert-error alert-compact" role="alert">
          {error}
        </div>
      )}
      {!error && !src && <p className="muted">Loading video…</p>}
      {src && (
        <video className="lesson-video" controls playsInline preload="metadata" src={src} />
      )}
      <p className="muted list-meta">
        Temporary MP4 playback
        {asset.delivery === "mp4_signed" ? " (signed URL)" : ""}. HLS migration planned.
      </p>
    </li>
  );
}
