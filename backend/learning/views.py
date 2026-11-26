import io
import mimetypes

from django.db.models import Prefetch
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.models import Student
from accounts.permissions import IsAdminRole, IsStudentRole
from accounts.services import create_and_send_invite
from catalog.models import Lesson, LessonAsset, Module, Program
from catalog.storage import StorageService
from learning.models import Enrollment, LessonCompletion
from learning.serializers import (
    AdminCreateStudentSerializer,
    AdminEnrollmentListSerializer,
    AdminEnrollmentCreateSerializer,
    LessonCompletionSerializer,
    StudentEnrollmentSerializer,
    StudentLessonDetailSerializer,
    StudentProgramTreeSerializer,
)


class AdminPermissionMixin:
    permission_classes = [IsAuthenticated, IsAdminRole]


class AdminStudentCreate(AdminPermissionMixin, generics.CreateAPIView):
    serializer_class = AdminCreateStudentSerializer


class AdminStudentResendInvite(AdminPermissionMixin, APIView):
    def post(self, request, pk):
        student = get_object_or_404(Student, pk=pk)
        create_and_send_invite(student.user)
        return Response({"detail": "Invite sent."})


class AdminEnrollmentListCreate(AdminPermissionMixin, generics.ListCreateAPIView):
    serializer_class = AdminEnrollmentCreateSerializer

    def get_serializer_class(self):
        if self.request.method == "GET":
            return AdminEnrollmentListSerializer
        return AdminEnrollmentCreateSerializer

    def get_queryset(self):
        return (
            Enrollment.objects.select_related("student__user", "program")
            .order_by("-created_at")
        )


class AdminEnrollmentProgress(AdminPermissionMixin, APIView):
    def get(self, request, enrollment_id):
        enrollment = get_object_or_404(
            Enrollment.objects.select_related("student", "program"), pk=enrollment_id
        )
        published_lessons = Lesson.objects.filter(
            module__program_id=enrollment.program_id, is_published=True
        )
        total = published_lessons.count()
        completed = LessonCompletion.objects.filter(
            student=enrollment.student, lesson__in=published_lessons
        ).count()
        percent = round((completed / total) * 100, 2) if total else 0
        return Response({"completed": completed, "total": total, "percent": percent})


class StudentPermissionMixin:
    permission_classes = [IsAuthenticated, IsStudentRole]


def _student_profile(request):
    return request.user.student_profile


def _active_enrollment(student, program_id: int):
    return Enrollment.objects.filter(
        student=student, program_id=program_id, status=Enrollment.Status.ACTIVE
    ).first()


def _lesson_for_student(student, lesson_id: int):
    lesson = (
        Lesson.objects.select_related("module__program")
        .prefetch_related("assets")
        .filter(pk=lesson_id)
        .first()
    )
    if lesson is None or not lesson.is_published:
        return None
    program = lesson.module.program
    if not program.is_published:
        return None
    if _active_enrollment(student, program.id) is None:
        return None
    return lesson


def _asset_for_student(student, asset_id: int):
    asset = (
        LessonAsset.objects.select_related("lesson__module__program")
        .filter(pk=asset_id)
        .first()
    )
    if asset is None:
        return None
    lesson = asset.lesson
    if not lesson.is_published or not lesson.module.program.is_published:
        return None
    if _active_enrollment(student, lesson.module.program_id) is None:
        return None
    return asset


class StudentEnrollmentList(StudentPermissionMixin, generics.ListAPIView):
    serializer_class = StudentEnrollmentSerializer

    def get_queryset(self):
        student = _student_profile(self.request)
        return (
            Enrollment.objects.filter(
                student=student,
                status=Enrollment.Status.ACTIVE,
                program__is_published=True,
            )
            .select_related("program")
            .order_by("-created_at")
        )


class StudentProgramDetail(StudentPermissionMixin, APIView):
    def get(self, request, program_id):
        student = _student_profile(request)
        if _active_enrollment(student, program_id) is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        published_lessons = Lesson.objects.filter(is_published=True).order_by("order")
        program = get_object_or_404(
            Program.objects.prefetch_related(
                Prefetch(
                    "modules",
                    queryset=Module.objects.order_by("order").prefetch_related(
                        Prefetch("lessons", queryset=published_lessons)
                    ),
                )
            ),
            pk=program_id,
            is_published=True,
        )
        return Response(StudentProgramTreeSerializer(program).data)


class StudentLessonDetail(StudentPermissionMixin, APIView):
    def get(self, request, lesson_id):
        student = _student_profile(request)
        lesson = _lesson_for_student(student, lesson_id)
        if lesson is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(
            StudentLessonDetailSerializer(lesson, context={"student": student}).data
        )


class StudentLessonComplete(StudentPermissionMixin, APIView):
    def post(self, request, lesson_id):
        student = _student_profile(request)
        lesson = _lesson_for_student(student, lesson_id)
        if lesson is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        completion, _created = LessonCompletion.objects.get_or_create(
            student=student, lesson=lesson
        )
        return Response(LessonCompletionSerializer(completion).data)


class StudentAssetDownload(StudentPermissionMixin, APIView):
    def get(self, request, asset_id):
        student = _student_profile(request)
        asset = _asset_for_student(student, asset_id)
        if asset is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        try:
            data = StorageService().get_bytes(asset.storage_key)
        except (FileNotFoundError, OSError):
            return Response(status=status.HTTP_404_NOT_FOUND)
        content_type = asset.content_type or mimetypes.guess_type(asset.filename)[0] or "application/octet-stream"
        return FileResponse(
            io.BytesIO(data),
            content_type=content_type,
            as_attachment=True,
            filename=asset.filename,
        )


class StudentAssetStream(StudentPermissionMixin, APIView):
    """Inline byte stream for local/dev video playback (`delivery: mp4_proxy`)."""

    def get(self, request, asset_id):
        from pathlib import Path

        from django.conf import settings

        student = _student_profile(request)
        asset = _asset_for_student(student, asset_id)
        if asset is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        content_type = (
            asset.content_type
            or mimetypes.guess_type(asset.filename)[0]
            or "application/octet-stream"
        )
        if settings.LMS_USE_LOCAL_STORAGE:
            path = Path(settings.MEDIA_ROOT) / asset.storage_key
            if not path.is_file():
                return Response(status=status.HTTP_404_NOT_FOUND)
            return FileResponse(path.open("rb"), content_type=content_type, as_attachment=False)
        try:
            data = StorageService().get_bytes(asset.storage_key)
        except (FileNotFoundError, OSError):
            return Response(status=status.HTTP_404_NOT_FOUND)
        return FileResponse(
            io.BytesIO(data),
            content_type=content_type,
            as_attachment=False,
        )


class StudentAssetPlayback(StudentPermissionMixin, APIView):
    """Refresh playback descriptor for a video asset (signed URL or stream path)."""

    def get(self, request, asset_id):
        from learning.serializers import StudentLessonAssetSerializer

        student = _student_profile(request)
        asset = _asset_for_student(student, asset_id)
        if asset is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        data = StudentLessonAssetSerializer(asset, context={"student": student}).data
        if data.get("kind") != "video":
            return Response(
                {"detail": "Asset is not a video."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(
            {
                "id": data["id"],
                "kind": data["kind"],
                "delivery": data["delivery"],
                "playback_url": data["playback_url"],
                "playback_expires_at": data["playback_expires_at"],
                "content_type": data["content_type"],
                "filename": data["filename"],
            }
        )
