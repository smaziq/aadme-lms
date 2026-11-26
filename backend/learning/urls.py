from django.urls import path

from .views import (
    AdminEnrollmentCreate,
    AdminEnrollmentProgress,
    AdminStudentCreate,
    AdminStudentResendInvite,
)

urlpatterns = [
    path("students/", AdminStudentCreate.as_view()),
    path("students/<int:pk>/resend-invite/", AdminStudentResendInvite.as_view()),
    path("enrollments/", AdminEnrollmentCreate.as_view()),
    path("enrollments/<int:enrollment_id>/progress/", AdminEnrollmentProgress.as_view()),
]