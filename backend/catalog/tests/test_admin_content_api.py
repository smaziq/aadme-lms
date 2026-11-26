import pytest
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient
from catalog.models import LessonAsset
from catalog.storage import StorageService, lesson_asset_key

User = get_user_model()


@pytest.fixture
def admin_api():
    user = User.objects.create_user(email="admin@example.com", password="x", role="admin", is_staff=True)
    api = APIClient()
    api.credentials(HTTP_AUTHORIZATION=f"Token {Token.objects.create(user=user).key}")
    return api


@pytest.mark.django_db
def test_admin_creates_program_tree(admin_api):
    res = admin_api.post("/api/admin/programs/", {"title": "P", "slug": "p", "description": "", "is_published": True}, format="json")
    assert res.status_code == 201
    pid = res.data["id"]
    m = admin_api.post(f"/api/admin/programs/{pid}/modules/", {"title": "M1", "order": 1}, format="json")
    assert m.status_code == 201
    mid = m.data["id"]
    lesson = admin_api.post(f"/api/admin/modules/{mid}/lessons/", {"title": "L1", "order": 1, "body": "Hi", "links": [], "is_published": True}, format="json")
    assert lesson.status_code == 201


@pytest.mark.django_db
def test_student_cannot_create_program():
    user = User.objects.create_user(email="s@example.com", password="x", role="student")
    api = APIClient()
    api.credentials(HTTP_AUTHORIZATION=f"Token {Token.objects.create(user=user).key}")
    res = api.post("/api/admin/programs/", {"title": "P", "slug": "p"}, format="json")
    assert res.status_code == 403


@pytest.mark.django_db
def test_asset_complete_after_upload(admin_api, tmp_path, settings):
    settings.LMS_USE_LOCAL_STORAGE = True
    settings.MEDIA_ROOT = tmp_path
    prog = admin_api.post("/api/admin/programs/", {"title": "P", "slug": "p", "is_published": True}, format="json").data
    mod = admin_api.post(f"/api/admin/programs/{prog['id']}/modules/", {"title": "M", "order": 1}, format="json").data
    lesson = admin_api.post(f"/api/admin/modules/{mod['id']}/lessons/", {"title": "L", "order": 1, "body": "", "is_published": True}, format="json").data
    prep = admin_api.post(
        f"/api/admin/lessons/{lesson['id']}/assets/presign/",
        {"filename": "notes.pdf", "content_type": "application/pdf"},
        format="json",
    )
    assert prep.status_code == 200
    key = prep.data["storage_key"]
    StorageService().put_bytes(key, b"%PDF", "application/pdf")
    done = admin_api.post(
        f"/api/admin/lessons/{lesson['id']}/assets/complete/",
        {"storage_key": key, "filename": "notes.pdf", "content_type": "application/pdf", "size": 4},
        format="json",
    )
    assert done.status_code == 201
    assert LessonAsset.objects.filter(lesson_id=lesson["id"], storage_key=key).exists()


def _lesson_tree(admin_api):
    prog = admin_api.post(
        "/api/admin/programs/", {"title": "P", "slug": "p", "is_published": True}, format="json"
    ).data
    mod = admin_api.post(
        f"/api/admin/programs/{prog['id']}/modules/", {"title": "M", "order": 1}, format="json"
    ).data
    lesson = admin_api.post(
        f"/api/admin/modules/{mod['id']}/lessons/",
        {"title": "L", "order": 1, "body": "", "is_published": True},
        format="json",
    ).data
    return prog, lesson


@pytest.mark.django_db
def test_asset_complete_without_upload_returns_400(admin_api, tmp_path, settings):
    settings.LMS_USE_LOCAL_STORAGE = True
    settings.MEDIA_ROOT = tmp_path
    prog, lesson = _lesson_tree(admin_api)
    key = lesson_asset_key(prog["id"], lesson["id"], "missing.pdf")
    assert LessonAsset.objects.count() == 0
    res = admin_api.post(
        f"/api/admin/lessons/{lesson['id']}/assets/complete/",
        {
            "storage_key": key,
            "filename": "missing.pdf",
            "content_type": "application/pdf",
            "size": 0,
        },
        format="json",
    )
    assert res.status_code == 400
    assert LessonAsset.objects.count() == 0


@pytest.mark.django_db
def test_asset_complete_mismatched_storage_key_returns_400(admin_api, tmp_path, settings):
    settings.LMS_USE_LOCAL_STORAGE = True
    settings.MEDIA_ROOT = tmp_path
    prog, lesson = _lesson_tree(admin_api)
    wrong_key = lesson_asset_key(prog["id"], lesson["id"] + 999, "notes.pdf")
    StorageService().put_bytes(wrong_key, b"%PDF", "application/pdf")
    res = admin_api.post(
        f"/api/admin/lessons/{lesson['id']}/assets/complete/",
        {
            "storage_key": wrong_key,
            "filename": "notes.pdf",
            "content_type": "application/pdf",
            "size": 4,
        },
        format="json",
    )
    assert res.status_code == 400
    assert not LessonAsset.objects.filter(lesson_id=lesson["id"]).exists()


@pytest.mark.django_db
def test_asset_multipart_upload(admin_api, tmp_path, settings):
    settings.LMS_USE_LOCAL_STORAGE = True
    settings.MEDIA_ROOT = tmp_path
    prog, lesson = _lesson_tree(admin_api)
    res = admin_api.post(
        f"/api/admin/lessons/{lesson['id']}/assets/upload/",
        {
            "file": SimpleUploadedFile(
                "slide.pdf", b"%PDF-1.4", content_type="application/pdf"
            )
        },
        format="multipart",
    )
    assert res.status_code == 201
    assert res.data["filename"] == "slide.pdf"
    assert res.data["size"] == 8
    assert LessonAsset.objects.filter(lesson_id=lesson["id"], filename="slide.pdf").exists()


@pytest.mark.django_db
def test_asset_multipart_upload_requires_file(admin_api, tmp_path, settings):
    settings.LMS_USE_LOCAL_STORAGE = True
    settings.MEDIA_ROOT = tmp_path
    _prog, lesson = _lesson_tree(admin_api)
    res = admin_api.post(
        f"/api/admin/lessons/{lesson['id']}/assets/upload/",
        {},
        format="multipart",
    )
    assert res.status_code == 400