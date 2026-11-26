from django.db import models
from django.db.models import Q


class Enrollment(models.Model):
    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        PAUSED = "paused", "Paused"
        WITHDRAWN = "withdrawn", "Withdrawn"

    student = models.ForeignKey("accounts.Student", on_delete=models.CASCADE, related_name="enrollments")
    program = models.ForeignKey("catalog.Program", on_delete=models.CASCADE, related_name="enrollments")
    batch = models.ForeignKey(
        "catalog.Batch", on_delete=models.SET_NULL, null=True, blank=True, related_name="enrollments"
    )
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE)
    crm_enrollment_id = models.CharField(max_length=64, null=True, blank=True, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["student", "program"],
                condition=Q(status="active"),
                name="uniq_active_enrollment_per_student_program",
            )
        ]


class LessonCompletion(models.Model):
    student = models.ForeignKey("accounts.Student", on_delete=models.CASCADE, related_name="completions")
    lesson = models.ForeignKey("catalog.Lesson", on_delete=models.CASCADE, related_name="completions")
    completed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["student", "lesson"], name="uniq_student_lesson_completion")
        ]