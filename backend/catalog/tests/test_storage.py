from catalog.storage import (
    StorageService,
    assignment_upload_key,
    is_video_content_type,
    lesson_asset_key,
    lesson_video_key,
)


def test_lesson_asset_key_shape():
    key = lesson_asset_key(3, 9, "Week 1.pdf")
    assert key.startswith("lessons/3/9/")
    assert key.endswith(".pdf")


def test_lesson_video_key_and_mime():
    key = lesson_video_key(3, 9, "Lecture 1.mp4")
    assert key == "lessons/3/9/videos/Lecture_1.mp4"
    assert is_video_content_type("video/mp4")
    assert not is_video_content_type("application/pdf")


def test_assignment_prefix_reserved():
    key = assignment_upload_key(12, "hw.zip")
    assert key.startswith("assignments/12/")


def test_local_presign_roundtrip(tmp_path, settings):
    settings.LMS_USE_LOCAL_STORAGE = True
    settings.MEDIA_ROOT = tmp_path
    svc = StorageService()
    key = "lessons/1/2/a.txt"
    upload_url = svc.presign_upload(key, "text/plain")
    assert upload_url
    svc.put_bytes(key, b"hello", "text/plain")
    download_url = svc.presign_download(key)
    assert download_url
    assert svc.get_bytes(key) == b"hello"