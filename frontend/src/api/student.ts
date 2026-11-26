import { apiRequest } from "./client";
import type { EnrollmentProgress } from "./admin";

export type StudentProgramSummary = {
  id: number;
  title: string;
  slug: string;
  description: string;
};

export type StudentEnrollment = {
  id: number;
  status: string;
  created_at: string;
  program: StudentProgramSummary;
  progress: EnrollmentProgress;
};

export type StudentLessonSummary = {
  id: number;
  title: string;
  order: number;
};

export type StudentModuleTree = {
  id: number;
  title: string;
  order: number;
  lessons: StudentLessonSummary[];
};

export type StudentProgramTree = {
  id: number;
  title: string;
  slug: string;
  description: string;
  modules: StudentModuleTree[];
};

export type StudentLessonAsset = {
  id: number;
  filename: string;
  content_type: string;
  size: number;
  download_url: string;
  kind: "video" | "file";
  delivery: "mp4_signed" | "mp4_proxy" | "download" | "hls";
  playback_url: string | null;
  playback_expires_at: string | null;
};

export type LessonLink = {
  url?: string;
  label?: string;
  title?: string;
};

export type StudentLessonDetail = {
  id: number;
  title: string;
  order: number;
  body: string;
  links: LessonLink[];
  assets: StudentLessonAsset[];
  is_completed: boolean;
};

export type LessonCompletion = {
  id: number;
  lesson: number;
  completed_at: string;
};

export function listMyEnrollments(token: string) {
  return apiRequest<StudentEnrollment[]>("/api/me/enrollments/", { token });
}

export function getMyProgram(token: string, programId: number) {
  return apiRequest<StudentProgramTree>(`/api/me/programs/${programId}/`, { token });
}

export function getMyLesson(token: string, lessonId: number) {
  return apiRequest<StudentLessonDetail>(`/api/me/lessons/${lessonId}/`, { token });
}

export function completeLesson(token: string, lessonId: number) {
  return apiRequest<LessonCompletion>(`/api/me/lessons/${lessonId}/complete/`, {
    method: "POST",
    token,
  });
}