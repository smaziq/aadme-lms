from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.models import Student
from accounts.permissions import IsAdminRole
from accounts.services import create_and_send_invite
from catalog.models import Lesson
from learning.models import Enrollment, LessonCompletion
from learning.serializers import AdminCreateStudentSerializer, AdminEnrollmentCreateSerializer


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