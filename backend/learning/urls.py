from django.urls import path

from .views import (
    AdminEnrollmentListCreate,
    AdminEnrollmentProgress,
    AdminStudentCreate,
    AdminStudentResendInvite,
)

urlpatterns = [
    path("students/", AdminStudentCreate.as_view()),
    path("students/<int:pk>/resend-invite/", AdminStudentResendInvite.as_view()),
    path("enrollments/", AdminEnrollmentListCreate.as_view()),
    path("enrollments/<int:enrollment_id>/progress/", AdminEnrollmentProgress.as_view()),
]