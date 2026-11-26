from django.urls import path

from .views import (
    StudentAssetDownload,
    StudentAssetPlayback,
    StudentAssetStream,
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
    path("assets/<int:asset_id>/download/", StudentAssetDownload.as_view()),
    path("assets/<int:asset_id>/stream/", StudentAssetStream.as_view()),
    path("assets/<int:asset_id>/playback/", StudentAssetPlayback.as_view()),
]
