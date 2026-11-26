import { apiRequest, apiUpload } from "./client";

export type Program = {
  id: number;
  title: string;
  slug: string;
  description: string;
  is_published: boolean;
  created_at: string;
};

export type Module = {
  id: number;
  program: number;
  title: string;
  order: number;
};

export type Lesson = {
  id: number;
  module: number;
  title: string;
  order: number;
  body: string;
  links: unknown[];
  is_published: boolean;
};

export type LessonAsset = {
  id: number;
  lesson: number;
  storage_key: string;
  filename: string;
  content_type: string;
  size: number;
  created_at: string;
};

export type AdminStudent = {
  id: number;
  full_name: string;
  phone: string;
  crm_person_id: string;
};

export type Enrollment = {
  id: number;
  student_id: number;
  program_id: number;
  batch_id: number | null;
  status: string;
  created_at: string;
};

export type EnrollmentProgress = {
  completed: number;
  total: number;
  percent: number;
};

export type AdminEnrollmentRow = {
  id: number;
  student_id: number;
  student_name: string;
  student_email: string;
  program_id: number;
  program_title: string;
  status: string;
  created_at: string;
  progress: EnrollmentProgress;
};

export function listPrograms(token: string) {
  return apiRequest<Program[]>("/api/admin/programs/", { token });
}

export function createProgram(
  token: string,
  body: Pick<Program, "title" | "slug" | "description" | "is_published">,
) {
  return apiRequest<Program>("/api/admin/programs/", {
    method: "POST",
    token,
    body,
  });
}

export function patchProgram(
  token: string,
  programId: number,
  body: Partial<Pick<Program, "title" | "is_published" | "description">>,
) {
  return apiRequest<Program>(`/api/admin/programs/${programId}/`, {
    method: "PATCH",
    token,
    body,
  });
}

export function patchLesson(
  token: string,
  lessonId: number,
  body: Partial<Pick<Lesson, "title" | "is_published">>,
) {
  return apiRequest<Lesson>(`/api/admin/lessons/${lessonId}/`, {
    method: "PATCH",
    token,
    body,
  });
}

export function listModules(token: string, programId: number) {
  return apiRequest<Module[]>(`/api/admin/programs/${programId}/modules/`, { token });
}

export function createModule(
  token: string,
  programId: number,
  body: { title: string; order: number },
) {
  return apiRequest<Module>(`/api/admin/programs/${programId}/modules/`, {
    method: "POST",
    token,
    body,
  });
}

export function listLessons(token: string, moduleId: number) {
  return apiRequest<Lesson[]>(`/api/admin/modules/${moduleId}/lessons/`, { token });
}

export function createLesson(
  token: string,
  moduleId: number,
  body: {
    title: string;
    order: number;
    body: string;
    links: unknown[];
    is_published: boolean;
  },
) {
  return apiRequest<Lesson>(`/api/admin/modules/${moduleId}/lessons/`, {
    method: "POST",
    token,
    body,
  });
}

export function uploadLessonAsset(token: string, lessonId: number, file: File) {
  return apiUpload<LessonAsset>(`/api/admin/lessons/${lessonId}/assets/upload/`, file, token);
}

export function createStudent(
  token: string,
  body: { email: string; full_name: string; phone?: string },
) {
  return apiRequest<AdminStudent>("/api/admin/students/", {
    method: "POST",
    token,
    body,
  });
}

export function createEnrollment(
  token: string,
  body: { student_id: number; program_id: number },
) {
  return apiRequest<Enrollment>("/api/admin/enrollments/", {
    method: "POST",
    token,
    body,
  });
}

export function getEnrollmentProgress(token: string, enrollmentId: number) {
  return apiRequest<EnrollmentProgress>(`/api/admin/enrollments/${enrollmentId}/progress/`, {
    token,
  });
}

export function listEnrollments(token: string) {
  return apiRequest<AdminEnrollmentRow[]>("/api/admin/enrollments/", { token });
}

export function resendStudentInvite(token: string, studentId: number) {
  return apiRequest<{ detail: string }>(`/api/admin/students/${studentId}/resend-invite/`, {
    method: "POST",
    token,
  });
}