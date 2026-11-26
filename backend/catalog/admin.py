from django.contrib import admin

from .models import Batch, Lesson, Module, Program


class ModuleInline(admin.TabularInline):
    model = Module
    extra = 0


class BatchInline(admin.TabularInline):
    model = Batch
    extra = 0


@admin.register(Program)
class ProgramAdmin(admin.ModelAdmin):
    list_display = ("title", "slug", "is_published", "created_at")
    prepopulated_fields = {"slug": ("title",)}
    search_fields = ("title", "slug")
    inlines = [ModuleInline, BatchInline]


class LessonInline(admin.TabularInline):
    model = Lesson
    extra = 0


@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ("title", "program", "order")
    list_filter = ("program",)
    inlines = [LessonInline]


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ("title", "module", "order", "is_published")
    list_filter = ("module__program", "is_published")


@admin.register(Batch)
class BatchAdmin(admin.ModelAdmin):
    list_display = ("name", "program", "start_date")
    list_filter = ("program",)