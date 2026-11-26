import { useEffect, useState, type FormEvent } from "react";
import { Link } from "react-router-dom";
import {
  createProgram,
  listPrograms,
  patchProgram,
  type Program,
} from "../../api/admin";
import { formatApiError, useAuth } from "../../auth/AuthContext";
import { AdminShell } from "../../components/AdminShell";

function slugify(text: string): string {
  return text
    .trim()
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-|-$/g, "");
}

export function ProgramsPage() {
  const { token } = useAuth();
  const [programs, setPrograms] = useState<Program[] | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [title, setTitle] = useState("");
  const [slug, setSlug] = useState("");
  const [slugTouched, setSlugTouched] = useState(false);
  const [description, setDescription] = useState("");
  const [creating, setCreating] = useState(false);
  const [createError, setCreateError] = useState<string | null>(null);

  async function load() {
    if (!token) return;
    setError(null);
    try {
      const data = await listPrograms(token);
      setPrograms(data);
    } catch (err) {
      setError(formatApiError(err));
      setPrograms([]);
    }
  }

  useEffect(() => {
    void load();
  }, [token]);

  async function handleCreate(e: FormEvent) {
    e.preventDefault();
    if (!token) return;
    setCreateError(null);
    setCreating(true);
    try {
      const created = await createProgram(token, {
        title: title.trim(),
        slug: slug.trim() || slugify(title),
        description: description.trim(),
        is_published: false,
      });
      setPrograms((prev) => (prev ? [created, ...prev] : [created]));
      setTitle("");
      setSlug("");
      setSlugTouched(false);
      setDescription("");
    } catch (err) {
      setCreateError(formatApiError(err));
    } finally {
      setCreating(false);
    }
  }

  return (
    <AdminShell title="Programs">
      {error && (
        <div className="alert alert-error" role="alert">
          {error}
        </div>
      )}

      <section className="admin-section">
        <h2 className="section-title">New program</h2>
        {createError && (
          <div className="alert alert-error" role="alert">
            {createError}
          </div>
        )}
        <form className="admin-form admin-form-grid" onSubmit={handleCreate}>
          <label>
            Title
            <input
              value={title}
              onChange={(e) => {
                const v = e.target.value;
                setTitle(v);
                if (!slugTouched) setSlug(slugify(v));
              }}
              required
              disabled={creating}
            />
          </label>
          <label>
            Slug
            <input
              value={slug}
              onChange={(e) => {
                setSlugTouched(true);
                setSlug(e.target.value);
              }}
              required
              disabled={creating}
            />
          </label>
          <label className="span-2">
            Description
            <textarea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              rows={2}
              disabled={creating}
            />
          </label>
          <div>
            <button type="submit" className="btn-primary" disabled={creating}>
              {creating ? "Creating…" : "Create program"}
            </button>
          </div>
        </form>
      </section>

      <section className="admin-section">
        <h2 className="section-title">All programs</h2>
        {programs === null && <p className="muted">Loading programs…</p>}
        {programs !== null && programs.length === 0 && !error && (
          <p className="muted">No programs yet. Create one above.</p>
        )}
        {programs !== null && programs.length > 0 && (
          <ul className="admin-list">
            {programs.map((p) => (
              <li key={p.id} className="admin-list-item">
                <div>
                  <Link to={`/admin/programs/${p.id}`}>{p.title}</Link>
                  <span className="muted list-meta">
                    {" "}
                    · /{p.slug} · {p.is_published ? "published" : "draft"}
                  </span>
                </div>
                <div className="row-actions">
                  <button
                    type="button"
                    className="btn-secondary btn-small"
                    onClick={() =>
                      void patchProgram(token!, p.id, { is_published: !p.is_published }).then(
                        (updated) =>
                          setPrograms((prev) =>
                            prev?.map((row) => (row.id === updated.id ? updated : row)) ?? prev,
                          ),
                      )
                    }
                  >
                    {p.is_published ? "Unpublish" : "Publish"}
                  </button>
                  <Link className="btn-secondary btn-small" to={`/admin/programs/${p.id}`}>
                    Manage
                  </Link>
                </div>
              </li>
            ))}
          </ul>
        )}
      </section>
    </AdminShell>
  );
}