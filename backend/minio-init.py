import boto3
import json

s3 = boto3.client(
    "s3",
    endpoint_url="http://minio:9000",
    aws_access_key_id="minioadmin",
    aws_secret_access_key="minioadmin",
)

try:
    s3.create_bucket(Bucket="ad-photos")
except s3.exceptions.BucketAlreadyOwnedByYou:
    pass

s3.put_bucket_policy(
    Bucket="ad-photos",
    Policy=json.dumps(
        {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": "*",
                    "Action": ["s3:GetObject"],
                    "Resource": ["arn:aws:s3:::ad-photos/*"],
                }
            ],
        }
    ),
)

print("MinIO bucket ready")
