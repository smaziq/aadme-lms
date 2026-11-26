import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { listMyEnrollments, type StudentEnrollment } from "../../api/student";
import { formatApiError, useAuth } from "../../auth/AuthContext";
import { StudentShell } from "../../components/StudentShell";

export function CoursesPage() {
  const { token } = useAuth();
  const [enrollments, setEnrollments] = useState<StudentEnrollment[] | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!token) return;
    let cancelled = false;
    async function load(activeToken: string) {
      setError(null);
      setEnrollments(null);
      try {
        const data = await listMyEnrollments(activeToken);
        if (!cancelled) setEnrollments(data);
      } catch (err) {
        if (!cancelled) {
          setError(formatApiError(err));
          setEnrollments([]);
        }
      }
    }
    void load(token);
    return () => {
      cancelled = true;
    };
  }, [token]);

  return (
    <StudentShell title="My courses">
      {error && (
        <div className="alert alert-error" role="alert">
          {error}
        </div>
      )}

      {enrollments === null && !error && <p className="muted">Loading your courses…</p>}

      {enrollments !== null && enrollments.length === 0 && !error && (
        <p className="muted">You are not enrolled in any courses yet. Contact your administrator.</p>
      )}

      {enrollments !== null && enrollments.length > 0 && (
        <ul className="admin-list">
          {enrollments.map((enrollment) => (
            <li key={enrollment.id} className="admin-list-item">
              <div>
                <Link to={`/courses/${enrollment.program.id}`}>
                  <strong>{enrollment.program.title}</strong>
                </Link>
                {enrollment.program.description && (
                  <p className="list-meta muted">{enrollment.program.description}</p>
                )}
                <p className="list-meta">
                  Progress: {enrollment.progress.completed} / {enrollment.progress.total} lessons
                  ({enrollment.progress.percent}%)
                </p>
                <div
                  className="progress-bar"
                  role="progressbar"
                  aria-valuenow={enrollment.progress.percent}
                  aria-valuemin={0}
                  aria-valuemax={100}
                >
                  <div
                    className="progress-bar-fill"
                    style={{ width: `${enrollment.progress.percent}%` }}
                  />
                </div>
              </div>
              <Link className="btn-secondary btn-small" to={`/courses/${enrollment.program.id}`}>
                Open
              </Link>
            </li>
          ))}
        </ul>
      )}
    </StudentShell>
  );
}