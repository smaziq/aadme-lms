from django.urls import path

from .views import (
    StudentEnrollmentList,
    StudentLessonComplete,
    StudentLessonDetail,
    StudentProgramDetail,
)

urlpatterns = [
    path("enrollments/", StudentEnrollmentList.as_view()),
    path("programs/<int:program_id>/", StudentProgramDetail.as_view()),
    path("lessons/<int:lesson_id>/", StudentLessonDetail.as_view()),
    path("lessons/<int:lesson_id>/complete/", StudentLessonComplete.as_view()),
]