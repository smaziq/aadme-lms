import pytest
from django.contrib.auth import get_user_model
from django.core import mail
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

from accounts.models import Student
from catalog.models import Lesson, Module, Program

User = get_user_model()


@pytest.fixture
def admin_api(settings):
    settings.EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
    user = User.objects.create_user(
        email="admin@example.com", password="x", role="admin", is_staff=True
    )
    api = APIClient()
    api.credentials(HTTP_AUTHORIZATION=f"Token {Token.objects.create(user=user).key}")
    return api


@pytest.mark.django_db(transaction=True)
def test_admin_creates_student_and_sends_invite(admin_api):
    res = admin_api.post(
        "/api/admin/students/",
        {"email": "new@example.com", "full_name": "New Student"},
        format="json",
    )
    assert res.status_code == 201
    assert Student.objects.filter(user__email="new@example.com").exists()
    assert len(mail.outbox) == 1


@pytest.mark.django_db
def test_student_cannot_create_student(settings):
    settings.EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
    user = User.objects.create_user(email="s@example.com", password="x", role="student")
    api = APIClient()
    api.credentials(HTTP_AUTHORIZATION=f"Token {Token.objects.create(user=user).key}")
    res = api.post(
        "/api/admin/students/",
        {"email": "other@example.com", "full_name": "Other"},
        format="json",
    )
    assert res.status_code == 403


@pytest.mark.django_db
def test_admin_enrolls_and_reads_progress(admin_api):
    st = admin_api.post(
        "/api/admin/students/", {"email": "n@example.com", "full_name": "N"}, format="json"
    ).data
    program = Program.objects.create(title="P", slug="p", is_published=True)
    module = Module.objects.create(program=program, title="M", order=1)
    Lesson.objects.create(module=module, title="L1", order=1, is_published=True)
    Lesson.objects.create(module=module, title="L2", order=2, is_published=True)
    en = admin_api.post(
        "/api/admin/enrollments/",
        {"student_id": st["id"], "program_id": program.id},
        format="json",
    )
    assert en.status_code == 201
    prog = admin_api.get(f"/api/admin/enrollments/{en.data['id']}/progress/")
    assert prog.status_code == 200
    assert prog.data["total"] == 2
    assert prog.data["completed"] == 0


@pytest.mark.django_db
def test_duplicate_active_enrollment_returns_400(admin_api):
    st = admin_api.post(
        "/api/admin/students/", {"email": "dup@example.com", "full_name": "D"}, format="json"
    ).data
    program = Program.objects.create(title="P2", slug="p2", is_published=True)
    payload = {"student_id": st["id"], "program_id": program.id}
    assert admin_api.post("/api/admin/enrollments/", payload, format="json").status_code == 201
    assert admin_api.post("/api/admin/enrollments/", payload, format="json").status_code == 400


@pytest.mark.django_db
def test_admin_lists_enrollments_with_progress(admin_api):
    st = admin_api.post(
        "/api/admin/students/", {"email": "list@example.com", "full_name": "Lister"}, format="json"
    ).data
    program = Program.objects.create(title="P", slug="p", is_published=True)
    module = Module.objects.create(program=program, title="M", order=1)
    Lesson.objects.create(module=module, title="L1", order=1, is_published=True)
    admin_api.post(
        "/api/admin/enrollments/",
        {"student_id": st["id"], "program_id": program.id},
        format="json",
    )
    res = admin_api.get("/api/admin/enrollments/")
    assert res.status_code == 200
    assert len(res.data) >= 1
    row = next(r for r in res.data if r["student_email"] == "list@example.com")
    assert row["program_title"] == "P"
    assert row["progress"]["total"] == 1


@pytest.mark.django_db
def test_resend_invite_sends_email(admin_api):
    st = admin_api.post(
        "/api/admin/students/",
        {"email": "r@example.com", "full_name": "R"},
        format="json",
    ).data
    mail.outbox.clear()
    res = admin_api.post(f"/api/admin/students/{st['id']}/resend-invite/")
    assert res.status_code == 200
    assert len(mail.outbox) == 1