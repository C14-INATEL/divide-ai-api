import os

import boto3

from app.config import settings


class R2Storage:
    def __init__(self):
        self._client = boto3.client(
            "s3",
            endpoint_url=settings.R2_ENDPOINT_URL,
            aws_access_key_id=settings.R2_ACCESS_KEY_ID,
            aws_secret_access_key=settings.R2_SECRET_ACCESS_KEY,
            region_name="auto",
        )

    def upload(self, content: bytes, key: str, content_type: str) -> str:
        self._client.put_object(
            Bucket=settings.R2_BUCKET,
            Key=key,
            Body=content,
            ContentType=content_type,
        )
        return f"{settings.R2_PUBLIC_URL.rstrip('/')}/{key}"


class LocalStorage:
    """Filesystem-backed storage for local development.

    Writes the file under ``settings.LOCAL_STORAGE_DIR`` and returns the path
    to the saved file, which is later served back by ``DebtService.get_proof``.
    """

    def upload(self, content: bytes, key: str, content_type: str) -> str:
        path = os.path.join(settings.LOCAL_STORAGE_DIR, key)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "wb") as f:
            f.write(content)
        return path


def get_storage():
    """Pick the storage backend based on configuration.

    Uses R2 when an endpoint is configured, otherwise falls back to the local
    filesystem so the app works out of the box in development.
    """
    if settings.R2_ENDPOINT_URL:
        return R2Storage()
    return LocalStorage()
