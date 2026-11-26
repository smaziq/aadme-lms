import re
from pathlib import Path

from django.conf import settings


def _safe_name(filename: str) -> str:
    name = Path(filename).name
    return re.sub(r"[^A-Za-z0-9._-]+", "_", name) or "file"


def lesson_asset_key(program_id: int, lesson_id: int, filename: str) -> str:
    return f"lessons/{program_id}/{lesson_id}/{_safe_name(filename)}"


def assignment_upload_key(enrollment_id: int, filename: str) -> str:
    return f"assignments/{enrollment_id}/{_safe_name(filename)}"


class StorageService:
    def __init__(self):
        self.local = settings.LMS_USE_LOCAL_STORAGE

    def _local_path(self, key: str) -> Path:
        path = Path(settings.MEDIA_ROOT) / key
        path.parent.mkdir(parents=True, exist_ok=True)
        return path

    def _s3_client(self):
        import boto3

        return boto3.client(
            "s3",
            endpoint_url=settings.AWS_S3_ENDPOINT_URL or None,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_S3_REGION_NAME,
        )

    def put_bytes(self, key: str, data: bytes, content_type: str) -> None:
        if self.local:
            self._local_path(key).write_bytes(data)
            return
        client = self._s3_client()
        client.put_object(
            Bucket=settings.AWS_STORAGE_BUCKET_NAME,
            Key=key,
            Body=data,
            ContentType=content_type,
        )

    def get_bytes(self, key: str) -> bytes:
        if self.local:
            return self._local_path(key).read_bytes()
        client = self._s3_client()
        obj = client.get_object(Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=key)
        return obj["Body"].read()

    def presign_upload(self, key: str, content_type: str, expires_in: int = 600) -> str:
        if self.local:
            return f"local://upload/{key}"
        client = self._s3_client()
        return client.generate_presigned_url(
            "put_object",
            Params={
                "Bucket": settings.AWS_STORAGE_BUCKET_NAME,
                "Key": key,
                "ContentType": content_type,
            },
            ExpiresIn=expires_in,
        )

    def presign_download(self, key: str, expires_in: int = 600) -> str:
        if self.local:
            return f"local://download/{key}"
        client = self._s3_client()
        return client.generate_presigned_url(
            "get_object",
            Params={"Bucket": settings.AWS_STORAGE_BUCKET_NAME, "Key": key},
            ExpiresIn=expires_in,
        )