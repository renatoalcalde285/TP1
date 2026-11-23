import boto3

from app.core.config import (
    RUSTFS_ACCESS_KEY,
    RUSTFS_SECRET_KEY,
)

BUCKET_NAME = "tp1-inen-demo"

s3_client = boto3.client(
    "s3",
    region_name="sa-east-1",
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
            Bucket=BUCKET_NAME,
            CreateBucketConfiguration={
                "LocationConstraint": "sa-east-1"
            }
        )