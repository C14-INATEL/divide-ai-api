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
