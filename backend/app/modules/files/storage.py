from functools import cache

import boto3
from botocore.config import Config
from mypy_boto3_s3 import S3Client

from app.core.config import settings


def make_client(endpoint_url: str | None) -> S3Client:
    """Make an S3 client for the configured bucket's storage.

    A custom endpoint (MinIO locally) is addressed by path,
    ``http://localhost:9000/colivo/<key>``, because its bucket names aren't
    host names; real AWS S3 picks its own style.

    Args:
        endpoint_url: The storage address, or None for real AWS S3.

    Returns:
        A client signing with Signature Version 4.
    """
    return boto3.client(
        "s3",
        endpoint_url=endpoint_url,
        region_name=settings.s3_region,
        aws_access_key_id=settings.s3_access_key_id,
        aws_secret_access_key=settings.s3_secret_access_key,
        config=Config(
            signature_version="s3v4",
            s3={"addressing_style": "path" if endpoint_url else "auto"},
            connect_timeout=settings.connect_timeout_seconds,
        ),
    )


@cache
def storage_client() -> S3Client:
    """Return the client the backend itself talks to the storage with.

    Returns:
        A client for ``S3_ENDPOINT_URL``, made once.
    """
    return make_client(settings.s3_endpoint_url)


@cache
def signing_client() -> S3Client:
    """Return the client that signs presigned URLs for browsers.

    A presigned URL's signature covers its host, so it is signed for the
    address a browser reaches (``S3_PUBLIC_ENDPOINT_URL``), which differs
    from the backend's inside Compose. Signing makes no request.

    Returns:
        A client for the public storage address, made once.
    """
    return make_client(settings.s3_public_endpoint_url or settings.s3_endpoint_url)
