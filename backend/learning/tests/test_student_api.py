import pytest
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

from accounts.models import Student
from catalog.models import Lesson, LessonAsset, Module, Program
from learning.models import Enrollment, LessonCompletion

User = get_user_model()


def student_client(email, name):
    user = User.objects.create_user(email=email, password="secret123", role="student")
    student = Student.objects.create(user=user, full_name=name)
    api = APIClient()
    api.credentials(HTTP_AUTHORIZATION=f"Token {Token.objects.create(user=user).key}")
    return api, student


@pytest.mark.django_db
def test_student_lists_active_enrollments_only():
    api, student = student_client("a@example.com", "A")
    p = Program.objects.create(title="P", slug="p", is_published=True)
    Enrollment.objects.create(student=student, program=p, status="active")
    p2 = Program.objects.create(title="Q", slug="q", is_published=True)
    Enrollment.objects.create(student=student, program=p2, status="paused")
    res = api.get("/api/me/enrollments/")
    assert res.status_code == 200
    assert len(res.data) == 1
    assert res.data[0]["program"]["slug"] == "p"
    assert "progress" in res.data[0]
    assert set(res.data[0]["progress"].keys()) == {"completed", "total", "percent"}


@pytest.mark.django_db
def test_program_tree_requires_active_enrollment():
    api, student = student_client("a@example.com", "A")
    p = Program.objects.create(title="P", slug="p", is_published=True)
    m = Module.objects.create(program=p, title="M", order=1)
    Lesson.objects.create(module=m, title="L", order=1, is_published=True)
    denied = api.get(f"/api/me/programs/{p.id}/")
    assert denied.status_code == 404
    Enrollment.objects.create(student=student, program=p, status="active")
    ok = api.get(f"/api/me/programs/{p.id}/")
    assert ok.status_code == 200
    assert len(ok.data["modules"]) == 1
    assert len(ok.data["modules"][0]["lessons"]) == 1


@pytest.mark.django_db
def test_program_tree_hides_unpublished_lessons():
    api, student = student_client("a@example.com", "A")
    p = Program.objects.create(title="P", slug="p", is_published=True)
    Enrollment.objects.create(student=student, program=p, status="active")
    m = Module.objects.create(program=p, title="M", order=1)
    Lesson.objects.create(module=m, title="Pub", order=1, is_published=True)
    Lesson.objects.create(module=m, title="Draft", order=2, is_published=False)
    res = api.get(f"/api/me/programs/{p.id}/")
    assert res.status_code == 200
    titles = [les["title"] for les in res.data["modules"][0]["lessons"]]
    assert titles == ["Pub"]


@pytest.mark.django_db
def test_lesson_detail_with_asset_download_url(settings, tmp_path):
    settings.LMS_USE_LOCAL_STORAGE = True
    settings.MEDIA_ROOT = tmp_path
    api, student = student_client("a@example.com", "A")
    p = Program.objects.create(title="P", slug="p", is_published=True)
    Enrollment.objects.create(student=student, program=p, status="active")
    m = Module.objects.create(program=p, title="M", order=1)
    lesson = Lesson.objects.create(
        module=m, title="L", order=1, body="hello", links=[{"url": "https://x"}], is_published=True
    )
    LessonAsset.objects.create(
        lesson=lesson,
        storage_key=f"lessons/{p.id}/{lesson.id}/file.pdf",
        filename="file.pdf",
        content_type="application/pdf",
        size=10,
    )
    res = api.get(f"/api/me/lessons/{lesson.id}/")
    assert res.status_code == 200
    assert res.data["body"] == "hello"
    assert res.data["assets"][0]["download_url"]


@pytest.mark.django_db
def test_unpublished_lesson_not_accessible():
    api, student = student_client("a@example.com", "A")
    p = Program.objects.create(title="P", slug="p", is_published=True)
    Enrollment.objects.create(student=student, program=p, status="active")
    m = Module.objects.create(program=p, title="M", order=1)
    lesson = Lesson.objects.create(module=m, title="L", order=1, is_published=False)
    res = api.get(f"/api/me/lessons/{lesson.id}/")
    assert res.status_code == 404


@pytest.mark.django_db
def test_mark_complete_idempotent_and_scoped():
    api, student = student_client("a@example.com", "A")
    other_api, _ = student_client("b@example.com", "B")
    p = Program.objects.create(title="P", slug="p", is_published=True)
    Enrollment.objects.create(student=student, program=p, status="active")
    m = Module.objects.create(program=p, title="M", order=1)
    lesson = Lesson.objects.create(module=m, title="L", order=1, body="x", is_published=True)
    r1 = api.post(f"/api/me/lessons/{lesson.id}/complete/")
    r2 = api.post(f"/api/me/lessons/{lesson.id}/complete/")
    assert r1.status_code == 200
    assert r2.status_code == 200
    assert r1.data["id"] == r2.data["id"]
    assert LessonCompletion.objects.filter(student=student, lesson=lesson).count() == 1
    denied = other_api.post(f"/api/me/lessons/{lesson.id}/complete/")
    assert denied.status_code == 404


@pytest.mark.django_db
def test_cross_student_cannot_read_lesson_without_enrollment():
    api, student = student_client("a@example.com", "A")
    other_api, _ = student_client("b@example.com", "B")
    p = Program.objects.create(title="P", slug="p", is_published=True)
    Enrollment.objects.create(student=student, program=p, status="active")
    m = Module.objects.create(program=p, title="M", order=1)
    lesson = Lesson.objects.create(module=m, title="L", order=1, body="secret", is_published=True)
    assert api.get(f"/api/me/lessons/{lesson.id}/").status_code == 200
    denied = other_api.get(f"/api/me/lessons/{lesson.id}/")
    assert denied.status_code == 404


@pytest.mark.django_db
def test_paused_enrollment_cannot_access_program_or_lesson():
    api, student = student_client("a@example.com", "A")
    p = Program.objects.create(title="P", slug="p", is_published=True)
    Enrollment.objects.create(student=student, program=p, status="paused")
    m = Module.objects.create(program=p, title="M", order=1)
    lesson = Lesson.objects.create(module=m, title="L", order=1, body="x", is_published=True)
    assert api.get(f"/api/me/programs/{p.id}/").status_code == 404
    assert api.get(f"/api/me/lessons/{lesson.id}/").status_code == 404


@pytest.mark.django_db
def test_cross_student_cannot_read_program_tree():
    api, student = student_client("a@example.com", "A")
    other_api, _ = student_client("b@example.com", "B")
    p = Program.objects.create(title="P", slug="p", is_published=True)
    Enrollment.objects.create(student=student, program=p, status="active")
    Module.objects.create(program=p, title="M", order=1)
    assert api.get(f"/api/me/programs/{p.id}/").status_code == 200
    assert other_api.get(f"/api/me/programs/{p.id}/").status_code == 404