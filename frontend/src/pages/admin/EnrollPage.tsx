import { useEffect, useState, type FormEvent } from "react";
import { Link } from "react-router-dom";
import {
  createEnrollment,
  createStudent,
  getEnrollmentProgress,
  listPrograms,
  type Enrollment,
  type EnrollmentProgress,
  type Program,
} from "../../api/admin";
import { formatApiError, useAuth } from "../../auth/AuthContext";
import { AdminShell } from "../../components/AdminShell";

export function EnrollPage() {
  const { token } = useAuth();
  const [programs, setPrograms] = useState<Program[] | null>(null);
  const [programsError, setProgramsError] = useState<string | null>(null);

  const [email, setEmail] = useState("");
  const [fullName, setFullName] = useState("");
  const [phone, setPhone] = useState("");
  const [programId, setProgramId] = useState<number | "">("");
  const [existingStudentId, setExistingStudentId] = useState("");
  const [useExistingStudent, setUseExistingStudent] = useState(false);

  const [submitting, setSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState<string | null>(null);
  const [lastEnrollment, setLastEnrollment] = useState<Enrollment | null>(null);
  const [progress, setProgress] = useState<EnrollmentProgress | null>(null);

  useEffect(() => {
    if (!token) return;
    const authToken = token;
    let cancelled = false;
    async function load() {
      setProgramsError(null);
      try {
        const data = await listPrograms(authToken);
        if (!cancelled) {
          setPrograms(data);
          if (data.length > 0) setProgramId(data[0].id);
        }
      } catch (err) {
        if (!cancelled) {
          setProgramsError(formatApiError(err));
          setPrograms([]);
        }
      }
    }
    void load();
    return () => {
      cancelled = true;
    };
  }, [token]);

  async function handleEnroll(e: FormEvent) {
    e.preventDefault();
    if (!token || programId === "") return;
    setSubmitError(null);
    setProgress(null);
    setLastEnrollment(null);
    setSubmitting(true);
    try {
      let studentId: number;
      if (useExistingStudent) {
        const parsed = Number(existingStudentId);
        if (Number.isNaN(parsed) || parsed < 1) {
          throw new Error("Enter a valid student id.");
        }
        studentId = parsed;
      } else {
        const student = await createStudent(token, {
          email: email.trim(),
          full_name: fullName.trim(),
          phone: phone.trim(),
        });
        studentId = student.id;
      }
      const enrollment = await createEnrollment(token, {
        student_id: studentId,
        program_id: programId,
      });
      setLastEnrollment(enrollment);
      const prog = await getEnrollmentProgress(token, enrollment.id);
      setProgress(prog);
      if (!useExistingStudent) {
        setEmail("");
        setFullName("");
        setPhone("");
      }
    } catch (err) {
      setSubmitError(formatApiError(err));
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <AdminShell title="Enroll student">
      {programsError && (
        <div className="alert alert-error" role="alert">
          {programsError}
        </div>
      )}

      {programs === null && !programsError && <p className="muted">Loading programs…</p>}
      {programs !== null && programs.length === 0 && (
        <p className="muted">
          No programs available.{" "}
          <Link to="/admin/programs">Create a program</Link> first.
        </p>
      )}

      {programs !== null && programs.length > 0 && (
        <section className="admin-section">
          {submitError && (
            <div className="alert alert-error" role="alert">
              {submitError}
            </div>
          )}
          <form className="admin-form" onSubmit={handleEnroll}>
            <label className="checkbox-row">
              <input
                type="checkbox"
                checked={useExistingStudent}
                onChange={(e) => setUseExistingStudent(e.target.checked)}
                disabled={submitting}
              />
              Enroll an existing student by id
            </label>

            {useExistingStudent ? (
              <label>
                Student id
                <input
                  type="number"
                  min={1}
                  value={existingStudentId}
                  onChange={(e) => setExistingStudentId(e.target.value)}
                  required
                  disabled={submitting}
                />
              </label>
            ) : (
              <>
                <label>
                  Email
                  <input
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    required
                    disabled={submitting}
                  />
                </label>
                <label>
                  Full name
                  <input
                    value={fullName}
                    onChange={(e) => setFullName(e.target.value)}
                    required
                    disabled={submitting}
                  />
                </label>
                <label>
                  Phone (optional)
                  <input
                    value={phone}
                    onChange={(e) => setPhone(e.target.value)}
                    disabled={submitting}
                  />
                </label>
              </>
            )}

            <label>
              Program
              <select
                value={programId}
                onChange={(e) => setProgramId(Number(e.target.value))}
                disabled={submitting}
              >
                {programs.map((p) => (
                  <option key={p.id} value={p.id}>
                    {p.title}
                  </option>
                ))}
              </select>
            </label>

            <button type="submit" className="btn-primary" disabled={submitting}>
              {submitting ? "Enrolling…" : "Create & enroll"}
            </button>
          </form>
        </section>
      )}

      {lastEnrollment && (
        <section className="admin-section admin-card">
          <h2 className="section-title">Enrollment created</h2>
          <p>
            Enrollment <strong>#{lastEnrollment.id}</strong> — student{" "}
            <strong>{lastEnrollment.student_id}</strong> in program{" "}
            <strong>{lastEnrollment.program_id}</strong> ({lastEnrollment.status}).
          </p>
          {progress && (
            <p className="muted">
              Progress: {progress.completed}/{progress.total} lessons ({progress.percent}%).
            </p>
          )}
        </section>
      )}
    </AdminShell>
  );
}