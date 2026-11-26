from catalog.storage import StorageService, assignment_upload_key, lesson_asset_key


def test_lesson_asset_key_shape():
    key = lesson_asset_key(3, 9, "Week 1.pdf")
    assert key.startswith("lessons/3/9/")
    assert key.endswith(".pdf")


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