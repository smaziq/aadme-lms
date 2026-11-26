import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { getMyProgram, type StudentProgramTree } from "../../api/student";
import { formatApiError, useAuth } from "../../auth/AuthContext";
import { StudentShell } from "../../components/StudentShell";

function isNotFoundError(err: unknown): boolean {
  const message = formatApiError(err).toLowerCase();
  return message.includes("not found") || message.includes("404");
}

export function CourseDetailPage() {
  const { programId } = useParams<{ programId: string }>();
  const id = Number(programId);
  const { token } = useAuth();
  const [program, setProgram] = useState<StudentProgramTree | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [notFound, setNotFound] = useState(false);

  useEffect(() => {
    if (!token || Number.isNaN(id)) return;
    let cancelled = false;
    async function load(activeToken: string, programId: number) {
      setError(null);
      setNotFound(false);
      setProgram(null);
      try {
        const data = await getMyProgram(activeToken, programId);
        if (!cancelled) setProgram(data);
      } catch (err) {
        if (cancelled) return;
        if (isNotFoundError(err)) {
          setNotFound(true);
        } else {
          setError(formatApiError(err));
        }
        setProgram(null);
      }
    }
    void load(token, id);
    return () => {
      cancelled = true;
    };
  }, [token, id]);

  const title = program?.title ?? (notFound ? "Course not found" : "Course");

  return (
    <StudentShell title={title}>
      <p className="breadcrumb">
        <Link to="/courses">My courses</Link>
        {program && <> · {program.title}</>}
      </p>

      {error && (
        <div className="alert alert-error" role="alert">
          {error}
        </div>
      )}

      {notFound && (
        <div className="alert alert-error" role="alert">
          This course is not available or you are not enrolled.
        </div>
      )}

      {program === null && !error && !notFound && (
        <p className="muted">Loading course content…</p>
      )}

      {program && program.modules.length === 0 && (
        <p className="muted">No modules have been published for this course yet.</p>
      )}

      {program &&
        program.modules
          .slice()
          .sort((a, b) => a.order - b.order)
          .map((mod) => (
            <section key={mod.id} className="admin-section admin-card">
              <h2 className="section-title">{mod.title}</h2>
              {mod.lessons.length === 0 ? (
                <p className="muted list-meta">No lessons in this module yet.</p>
              ) : (
                <ul className="lesson-tree">
                  {mod.lessons
                    .slice()
                    .sort((a, b) => a.order - b.order)
                    .map((lesson) => (
                      <li key={lesson.id} className="lesson-row">
                        <div className="lesson-head">
                          <Link to={`/courses/${program.id}/lessons/${lesson.id}`}>
                            {lesson.title}
                          </Link>
                        </div>
                      </li>
                    ))}
                </ul>
              )}
            </section>
          ))}
    </StudentShell>
  );
}