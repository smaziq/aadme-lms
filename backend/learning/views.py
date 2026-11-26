from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.models import Student
from accounts.permissions import IsAdminRole, IsStudentRole
from accounts.services import create_and_send_invite
from catalog.models import Lesson, Program
from learning.models import Enrollment, LessonCompletion
from learning.serializers import (
    AdminCreateStudentSerializer,
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


class AdminEnrollmentCreate(AdminPermissionMixin, generics.CreateAPIView):
    serializer_class = AdminEnrollmentCreateSerializer


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
    if _active_enrollment(student, lesson.module.program_id) is None:
        return None
    return lesson


class StudentEnrollmentList(StudentPermissionMixin, generics.ListAPIView):
    serializer_class = StudentEnrollmentSerializer

    def get_queryset(self):
        student = _student_profile(self.request)
        return (
            Enrollment.objects.filter(student=student, status=Enrollment.Status.ACTIVE)
            .select_related("program")
            .order_by("-created_at")
        )


class StudentProgramDetail(StudentPermissionMixin, APIView):
    def get(self, request, program_id):
        student = _student_profile(request)
        if _active_enrollment(student, program_id) is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        program = get_object_or_404(
            Program.objects.prefetch_related("modules__lessons"), pk=program_id
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