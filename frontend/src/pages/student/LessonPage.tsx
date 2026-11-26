import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import {
  completeLesson,
  getMyLesson,
  type LessonCompletion,
  type StudentLessonDetail,
} from "../../api/student";
import { formatApiError, useAuth } from "../../auth/AuthContext";
import { StudentShell } from "../../components/StudentShell";

function isNotFoundError(err: unknown): boolean {
  const message = formatApiError(err).toLowerCase();
  return message.includes("not found") || message.includes("404");
}

export function LessonPage() {
  const { programId, lessonId } = useParams<{ programId: string; lessonId: string }>();
  const programIdNum = Number(programId);
  const lessonIdNum = Number(lessonId);
  const { token } = useAuth();
  const [lesson, setLesson] = useState<StudentLessonDetail | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [notFound, setNotFound] = useState(false);
  const [completion, setCompletion] = useState<LessonCompletion | null>(null);
  const [completed, setCompleted] = useState(false);
  const [completing, setCompleting] = useState(false);
  const [completeError, setCompleteError] = useState<string | null>(null);

  useEffect(() => {
    if (!token || Number.isNaN(lessonIdNum)) return;

    let cancelled = false;
    async function load(activeToken: string, lid: number) {
      setError(null);
      setNotFound(false);
      setLesson(null);
      setCompletion(null);
      setCompleted(false);
      try {
        const data = await getMyLesson(activeToken, lid);
        if (cancelled) return;
        setLesson(data);
        if (data.is_completed) setCompleted(true);
      } catch (err) {
        if (cancelled) return;
        if (isNotFoundError(err)) {
          setNotFound(true);
        } else {
          setError(formatApiError(err));
        }
      }
    }
    void load(token, lessonIdNum);
    return () => {
      cancelled = true;
    };
  }, [token, lessonIdNum]);

  async function handleMarkDone() {
    if (!token || completed) return;
    setCompleteError(null);
    setCompleting(true);
    try {
      const result = await completeLesson(token, lessonIdNum);
      setCompletion(result);
      setCompleted(true);
    } catch (err) {
      setCompleteError(formatApiError(err));
    } finally {
      setCompleting(false);
    }
  }

  const title = lesson?.title ?? (notFound ? "Lesson not found" : "Lesson");
  const backHref = Number.isNaN(programIdNum) ? "/courses" : `/courses/${programIdNum}`;

  return (
    <StudentShell title={title}>
      <p className="breadcrumb">
        <Link to="/courses">My courses</Link>
        {!Number.isNaN(programIdNum) && (
          <>
            {" "}
            · <Link to={backHref}>Course</Link>
          </>
        )}
        {lesson && <> · {lesson.title}</>}
      </p>

      {error && (
        <div className="alert alert-error" role="alert">
          {error}
        </div>
      )}

      {notFound && (
        <div className="alert alert-error" role="alert">
          This lesson is not available or you do not have access.
        </div>
      )}

      {lesson === null && !error && !notFound && <p className="muted">Loading lesson…</p>}

      {lesson && (
        <article className="admin-card">
          {completed && (
            <p className="completion-badge" role="status">
              Completed
              {completion?.completed_at
                ? ` · ${new Date(completion.completed_at).toLocaleString()}`
                : ""}
            </p>
          )}

          {lesson.body ? (
            <div className="lesson-body lesson-content">{lesson.body}</div>
          ) : (
            <p className="muted">No lesson content.</p>
          )}

          {lesson.links.length > 0 && (
            <section className="admin-section">
              <h2 className="section-title">Links</h2>
              <ul className="asset-list">
                {lesson.links.map((link, idx) => {
                  const href = link.url ?? "#";
                  const label = link.label ?? link.title ?? href;
                  return (
                    <li key={`${href}-${idx}`}>
                      <a href={href} target="_blank" rel="noreferrer noopener">
                        {label}
                      </a>
                    </li>
                  );
                })}
              </ul>
            </section>
          )}

          {lesson.assets.length > 0 && (
            <section className="admin-section">
              <h2 className="section-title">Downloads</h2>
              <ul className="asset-list">
                {lesson.assets.map((asset) => (
                  <li key={asset.id}>
                    <a
                      href={asset.download_url}
                      download={asset.filename}
                      target="_blank"
                      rel="noreferrer"
                    >
                      {asset.filename}
                    </a>
                    <span className="muted list-meta">
                      {" "}
                      ({asset.content_type}, {asset.size} bytes)
                    </span>
                  </li>
                ))}
              </ul>
            </section>
          )}

          {completeError && (
            <div className="alert alert-error alert-compact" role="alert">
              {completeError}
            </div>
          )}

          <div className="admin-section">
            {completed ? (
              <p className="muted">You have marked this lesson as done.</p>
            ) : (
              <button
                type="button"
                className="btn-primary"
                onClick={() => void handleMarkDone()}
                disabled={completing}
              >
                {completing ? "Saving…" : "Mark done"}
              </button>
            )}
          </div>
        </article>
      )}
    </StudentShell>
  );
}