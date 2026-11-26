import pytest
from django.db import IntegrityError
from django.contrib.auth import get_user_model
from accounts.models import Student
from catalog.models import Program, Module, Lesson
from learning.models import Enrollment, LessonCompletion

User = get_user_model()


def _student(email="s@example.com"):
    u = User.objects.create_user(email=email, password="x", role="student")
    return Student.objects.create(user=u, full_name="Stu")


@pytest.mark.django_db
def test_one_active_enrollment_per_student_program():
    student = _student()
    program = Program.objects.create(title="P", slug="p")
    Enrollment.objects.create(student=student, program=program, status=Enrollment.Status.ACTIVE)
    with pytest.raises(IntegrityError):
        Enrollment.objects.create(student=student, program=program, status=Enrollment.Status.ACTIVE)


@pytest.mark.django_db
def test_paused_allows_new_active():
    student = _student()
    program = Program.objects.create(title="P", slug="p")
    Enrollment.objects.create(student=student, program=program, status=Enrollment.Status.PAUSED)
    second = Enrollment.objects.create(student=student, program=program, status=Enrollment.Status.ACTIVE)
    assert second.status == "active"


@pytest.mark.django_db
def test_completion_unique_and_idempotent_create():
    student = _student()
    program = Program.objects.create(title="P", slug="p", is_published=True)
    module = Module.objects.create(program=program, title="M", order=1)
    lesson = Lesson.objects.create(module=module, title="L", order=1, is_published=True)
    LessonCompletion.objects.create(student=student, lesson=lesson)
    with pytest.raises(IntegrityError):
        LessonCompletion.objects.create(student=student, lesson=lesson)