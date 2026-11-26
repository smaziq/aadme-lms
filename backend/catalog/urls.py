from django.urls import path

from .views import (
    AdminLessonAssetComplete,
    AdminLessonAssetPresign,
    AdminLessonAssetUpload,
    AdminLessonDetail,
    AdminModuleLessonListCreate,
    AdminProgramDetail,
    AdminProgramListCreate,
    AdminProgramModuleListCreate,
)

urlpatterns = [
    path("programs/", AdminProgramListCreate.as_view()),
    path("programs/<int:pk>/", AdminProgramDetail.as_view()),
    path("programs/<int:program_id>/modules/", AdminProgramModuleListCreate.as_view()),
    path("modules/<int:module_id>/lessons/", AdminModuleLessonListCreate.as_view()),
    path("lessons/<int:pk>/", AdminLessonDetail.as_view()),
    path("lessons/<int:lesson_id>/assets/presign/", AdminLessonAssetPresign.as_view()),
    path("lessons/<int:lesson_id>/assets/complete/", AdminLessonAssetComplete.as_view()),
    path("lessons/<int:lesson_id>/assets/upload/", AdminLessonAssetUpload.as_view()),
]