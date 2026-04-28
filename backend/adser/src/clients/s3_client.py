from abc import ABC, abstractmethod

import boto3
from botocore.config import Config


class S3Client(ABC):
    @abstractmethod
    def generate_presigned_put(self, key: str, content_type: str, expires_in: int = 600) -> str:
        pass


class MinioS3Client(S3Client):
    def __init__(self, endpoint: str, public_endpoint: str, access_key: str, secret_key: str, bucket: str):
        self.bucket = bucket
        # Internal client for server-side operations
        self.client = boto3.client(
            "s3",
            endpoint_url=endpoint,
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
        )
        # Public client for generating presigned URLs accessible from browser
        self.presign_client = boto3.client(
            "s3",
            endpoint_url=public_endpoint,
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            config=Config(signature_version="s3v4"),
        )

    def generate_presigned_put(self, key: str, content_type: str, expires_in: int = 600) -> str:
        return self.presign_client.generate_presigned_url(
            "put_object",
            Params={"Bucket": self.bucket, "Key": key, "ContentType": content_type},
            ExpiresIn=expires_in,
        )
