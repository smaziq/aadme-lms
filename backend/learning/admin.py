from django.contrib import admin

from catalog.models import LessonAsset

from .models import Enrollment, LessonCompletion


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ("id", "student", "program", "status", "created_at")
    list_filter = ("status", "program")
    search_fields = ("student__full_name", "student__user__email", "program__title")


@admin.register(LessonCompletion)
class LessonCompletionAdmin(admin.ModelAdmin):
    list_display = ("id", "student", "lesson", "completed_at")
    list_filter = ("lesson__module__program",)


@admin.register(LessonAsset)
class LessonAssetAdmin(admin.ModelAdmin):
    list_display = ("id", "lesson", "filename", "content_type", "size", "created_at")
    search_fields = ("filename", "storage_key")