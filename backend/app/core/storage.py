import boto3

from app.core.config import (
    RUSTFS_ENDPOINT,
    RUSTFS_ACCESS_KEY,
    RUSTFS_SECRET_KEY,
)

BUCKET_NAME = "documentos"

s3_client = boto3.client(
    "s3",
    endpoint_url=f"http://{RUSTFS_ENDPOINT}",
    aws_access_key_id=RUSTFS_ACCESS_KEY,
    aws_secret_access_key=RUSTFS_SECRET_KEY,
)


def ensure_bucket():

    buckets = s3_client.list_buckets()

    nombres = [
        bucket["Name"]
        for bucket in buckets["Buckets"]
    ]

    if BUCKET_NAME not in nombres:

        s3_client.create_bucket(
            Bucket=BUCKET_NAME
        )