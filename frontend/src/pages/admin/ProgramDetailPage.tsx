import { useCallback, useEffect, useState, type FormEvent } from "react";
import { Link, useParams } from "react-router-dom";
import {
  createLesson,
  createModule,
  listLessons,
  patchLesson,
  patchProgram,
  listModules,
  listPrograms,
  uploadLessonAsset,
  type Lesson,
  type LessonAsset,
  type Module,
  type Program,
} from "../../api/admin";
import { formatApiError, useAuth } from "../../auth/AuthContext";
import { AdminShell } from "../../components/AdminShell";

type ModuleWithLessons = Module & { lessons: Lesson[]; loadingLessons?: boolean };

export function ProgramDetailPage() {
  const { programId } = useParams<{ programId: string }>();
  const id = Number(programId);
  const { token } = useAuth();

  const [program, setProgram] = useState<Program | null>(null);
  const [modules, setModules] = useState<ModuleWithLessons[] | null>(null);
  const [pageError, setPageError] = useState<string | null>(null);
  const [notFound, setNotFound] = useState(false);

  const [moduleTitle, setModuleTitle] = useState("");
  const [moduleOrder, setModuleOrder] = useState(1);
  const [moduleSaving, setModuleSaving] = useState(false);
  const [moduleError, setModuleError] = useState<string | null>(null);

  const [lessonDrafts, setLessonDrafts] = useState<
    Record<number, { title: string; order: number; body: string }>
  >({});
  const [lessonSaving, setLessonSaving] = useState<number | null>(null);
  const [lessonErrors, setLessonErrors] = useState<Record<number, string>>({});

  const [uploadingLesson, setUploadingLesson] = useState<number | null>(null);
  const [uploadErrors, setUploadErrors] = useState<Record<number, string>>({});
  const [assetsByLesson, setAssetsByLesson] = useState<Record<number, LessonAsset[]>>({});

  const loadLessonsForModule = useCallback(
    async (moduleId: number) => {
      if (!token) return;
      setModules((prev) =>
        prev?.map((m) => (m.id === moduleId ? { ...m, loadingLessons: true } : m)) ?? prev,
      );
      try {
        const lessons = await listLessons(token, moduleId);
        setModules((prev) =>
          prev?.map((m) =>
            m.id === moduleId ? { ...m, lessons, loadingLessons: false } : m,
          ) ?? prev,
        );
      } catch (err) {
        setModules((prev) =>
          prev?.map((m) => (m.id === moduleId ? { ...m, loadingLessons: false } : m)) ?? prev,
        );
        setPageError(formatApiError(err));
      }
    },
    [token],
  );

  const loadAll = useCallback(async () => {
    if (!token || Number.isNaN(id)) return;
    setPageError(null);
    setNotFound(false);
    try {
      const programs = await listPrograms(token);
      const found = programs.find((p) => p.id === id);
      if (!found) {
        setNotFound(true);
        setProgram(null);
        setModules([]);
        return;
      }
      setProgram(found);
      const mods = await listModules(token, id);
      const withLessons: ModuleWithLessons[] = mods.map((m) => ({
        ...m,
        lessons: [],
        loadingLessons: true,
      }));
      setModules(withLessons);
      await Promise.all(mods.map((m) => loadLessonsForModule(m.id)));
    } catch (err) {
      setPageError(formatApiError(err));
      setModules([]);
    }
  }, [token, id, loadLessonsForModule]);

  useEffect(() => {
    void loadAll();
  }, [loadAll]);

  function lessonDraft(moduleId: number) {
    const existing = modules?.find((m) => m.id === moduleId);
    const nextOrder = (existing?.lessons.length ?? 0) + 1;
    return (
      lessonDrafts[moduleId] ?? { title: "", order: nextOrder, body: "" }
    );
  }

  function setLessonDraft(
    moduleId: number,
    patch: Partial<{ title: string; order: number; body: string }>,
  ) {
    setLessonDrafts((prev) => ({
      ...prev,
      [moduleId]: { ...lessonDraft(moduleId), ...patch },
    }));
  }

  async function handleAddModule(e: FormEvent) {
    e.preventDefault();
    if (!token) return;
    setModuleError(null);
    setModuleSaving(true);
    try {
      const mod = await createModule(token, id, {
        title: moduleTitle.trim(),
        order: moduleOrder,
      });
      setModules((prev) => [...(prev ?? []), { ...mod, lessons: [] }]);
      setLessonDrafts((prev) => ({
        ...prev,
        [mod.id]: { title: "", order: 1, body: "" },
      }));
      setModuleTitle("");
      setModuleOrder((modules?.length ?? 0) + 2);
    } catch (err) {
      setModuleError(formatApiError(err));
    } finally {
      setModuleSaving(false);
    }
  }

  async function handleAddLesson(moduleId: number) {
    if (!token) return;
    const draft = lessonDraft(moduleId);
    setLessonErrors((prev) => {
      const next = { ...prev };
      delete next[moduleId];
      return next;
    });
    setLessonSaving(moduleId);
    try {
      const lesson = await createLesson(token, moduleId, {
        title: draft.title.trim(),
        order: draft.order,
        body: draft.body,
        links: [],
        is_published: false,
      });
      setModules((prev) =>
        prev?.map((m) =>
          m.id === moduleId ? { ...m, lessons: [...m.lessons, lesson] } : m,
        ) ?? prev,
      );
      setLessonDraft(moduleId, {
        title: "",
        order: draft.order + 1,
        body: "",
      });
    } catch (err) {
      setLessonErrors((prev) => ({ ...prev, [moduleId]: formatApiError(err) }));
    } finally {
      setLessonSaving(null);
    }
  }

  async function handleUpload(lessonId: number, file: File | undefined) {
    if (!token || !file) return;
    setUploadErrors((prev) => {
      const next = { ...prev };
      delete next[lessonId];
      return next;
    });
    setUploadingLesson(lessonId);
    try {
      const asset = await uploadLessonAsset(token, lessonId, file);
      setAssetsByLesson((prev) => ({
        ...prev,
        [lessonId]: [...(prev[lessonId] ?? []), asset],
      }));
    } catch (err) {
      setUploadErrors((prev) => ({ ...prev, [lessonId]: formatApiError(err) }));
    } finally {
      setUploadingLesson(null);
    }
  }

  if (Number.isNaN(id)) {
    return (
      <AdminShell title="Program">
        <p className="muted">Invalid program id.</p>
        <Link to="/admin/programs">Back to programs</Link>
      </AdminShell>
    );
  }

  return (
    <AdminShell title={program?.title ?? "Program"}>
      <p className="breadcrumb muted">
        <Link to="/admin/programs">Programs</Link>
        {program && <> / {program.slug}</>}
      </p>

      {pageError && (
        <div className="alert alert-error" role="alert">
          {pageError}
        </div>
      )}

      {notFound && (
        <p className="muted">
          Program not found.{" "}
          <Link to="/admin/programs">Return to the list</Link>.
        </p>
      )}

      {program && modules === null && !notFound && <p className="muted">Loading content…</p>}

      {program && modules !== null && (
        <>
          <section className="admin-section admin-card">
            <p className="muted">
              Status:{" "}
              <strong>{program.is_published ? "Published" : "Draft"}</strong>
            </p>
            <button
              type="button"
              className="btn-secondary btn-small"
              onClick={() =>
                void patchProgram(token!, program.id, {
                  is_published: !program.is_published,
                }).then((updated) => setProgram(updated))
              }
            >
              {program.is_published ? "Unpublish program" : "Publish program"}
            </button>
          </section>

          <section className="admin-section">
            <h2 className="section-title">Add module</h2>
            {moduleError && (
              <div className="alert alert-error" role="alert">
                {moduleError}
              </div>
            )}
            <form className="admin-form admin-form-inline" onSubmit={handleAddModule}>
              <label>
                Title
                <input
                  value={moduleTitle}
                  onChange={(e) => setModuleTitle(e.target.value)}
                  required
                  disabled={moduleSaving}
                />
              </label>
              <label>
                Order
                <input
                  type="number"
                  min={1}
                  value={moduleOrder}
                  onChange={(e) => setModuleOrder(Number(e.target.value))}
                  disabled={moduleSaving}
                />
              </label>
              <button type="submit" className="btn-primary" disabled={moduleSaving}>
                {moduleSaving ? "Adding…" : "Add module"}
              </button>
            </form>
          </section>

          {modules.length === 0 && (
            <p className="muted">No modules yet. Add one to start building lessons.</p>
          )}

          {modules.map((mod) => {
            const draft = lessonDraft(mod.id);
            return (
              <section key={mod.id} className="admin-section admin-card">
                <h2 className="section-title">
                  Module {mod.order}: {mod.title}
                </h2>
                {mod.loadingLessons && <p className="muted">Loading lessons…</p>}
                {!mod.loadingLessons && mod.lessons.length === 0 && (
                  <p className="muted">No lessons in this module.</p>
                )}
                <ul className="lesson-tree">
                  {mod.lessons.map((lesson) => (
                    <li key={lesson.id} className="lesson-row">
                      <LessonRow
                        title={lesson.title}
                        body={lesson.body}
                        id={lesson.id}
                        isPublished={lesson.is_published}
                        assets={assetsByLesson[lesson.id] ?? []}
                        uploading={uploadingLesson === lesson.id}
                        uploadError={uploadErrors[lesson.id]}
                        onUpload={(file) => void handleUpload(lesson.id, file)}
                        onTogglePublish={() => {
                          if (!token) return;
                          void patchLesson(token, lesson.id, {
                            is_published: !lesson.is_published,
                          }).then((updated) => {
                            setModules(
                              (prev) =>
                                prev?.map((m) =>
                                  m.id === mod.id
                                    ? {
                                        ...m,
                                        lessons: m.lessons.map((l) =>
                                          l.id === updated.id ? updated : l,
                                        ),
                                      }
                                    : m,
                                ) ?? prev,
                            );
                          });
                        }}
                      />
                    </li>
                  ))}
                </ul>
                {lessonErrors[mod.id] && (
                  <div className="alert alert-error" role="alert">
                    {lessonErrors[mod.id]}
                  </div>
                )}
                <AddLessonForm
                  draft={draft}
                  saving={lessonSaving === mod.id}
                  onChange={(patch) => setLessonDraft(mod.id, patch)}
                  onAdd={() => void handleAddLesson(mod.id)}
                />
              </section>
            );
          })}
        </>
      )}
    </AdminShell>
  );
}

function LessonRow({
  title,
  body,
  id,
  isPublished,
  assets,
  uploading,
  uploadError,
  onUpload,
  onTogglePublish,
}: {
  title: string;
  body: string;
  id: number;
  isPublished: boolean;
  assets: LessonAsset[];
  uploading: boolean;
  uploadError?: string;
  onUpload: (file: File | undefined) => void;
  onTogglePublish: () => void;
}) {
  return (
    <>
      <div className="lesson-head">
        <strong>{title}</strong>
        <span className="muted">
          #{id} · {isPublished ? "published" : "draft"}
        </span>
        <button type="button" className="btn-secondary btn-small" onClick={onTogglePublish}>
          {isPublished ? "Unpublish" : "Publish"}
        </button>
      </div>
      {body && <p className="lesson-body muted">{body}</p>}
      {assets.length > 0 && (
        <ul className="asset-list muted">
          {assets.map((a) => (
            <li key={a.id}>
              {a.filename} ({a.size} bytes)
            </li>
          ))}
        </ul>
      )}
      {uploadError && (
        <div className="alert alert-error alert-compact" role="alert">
          {uploadError}
        </div>
      )}
      <label className="file-upload">
        <span className="btn-secondary btn-small">{uploading ? "Uploading…" : "Upload file"}</span>
        <input
          type="file"
          disabled={uploading}
          onChange={(e) => {
            onUpload(e.target.files?.[0]);
            e.target.value = "";
          }}
        />
      </label>
    </>
  );
}

function AddLessonForm({
  draft,
  saving,
  onChange,
  onAdd,
}: {
  draft: { title: string; order: number; body: string };
  saving: boolean;
  onChange: (patch: Partial<{ title: string; order: number; body: string }>) => void;
  onAdd: () => void;
}) {
  return (
    <div className="admin-form lesson-add">
      <label>
        Lesson title
        <input
          value={draft.title}
          onChange={(e) => onChange({ title: e.target.value })}
          disabled={saving}
        />
      </label>
      <label>
        Order
        <input
          type="number"
          min={1}
          value={draft.order}
          onChange={(e) => onChange({ order: Number(e.target.value) })}
          disabled={saving}
        />
      </label>
      <label className="span-2">
        Body
        <textarea
          value={draft.body}
          onChange={(e) => onChange({ body: e.target.value })}
          rows={2}
          disabled={saving}
        />
      </label>
      <button
        type="button"
        className="btn-primary"
        disabled={saving || !draft.title.trim()}
        onClick={onAdd}
      >
        {saving ? "Adding…" : "Add lesson"}
      </button>
    </div>
  );
}