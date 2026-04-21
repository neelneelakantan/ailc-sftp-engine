import boto3
from botocore.client import Config
from storage.s3_storage import S3Storage
from storage.storage_interface import BaseStorage
from core.observability.logger import logger

class S3Storage(BaseStorage):
    def __init__(self, endpoint_url, access_key, secret_key, bucket_name):
        self.bucket_name = bucket_name
        # The 'secret' sauce: endpoint_url points to your laptop (MinIO)
        self.s3 = boto3.client(
            's3',
            endpoint_url=endpoint_url,
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            config=Config(signature_version='s3v4')
        )
        # Ensure the bucket exists
        try:
            self.s3.create_bucket(Bucket=bucket_name)
        except self.s3.exceptions.BucketAlreadyOwnedByYou:
            pass

    def save(self, file_name: str, data: bytes) -> bool:
        try:
            self.s3.put_object(Bucket=self.bucket_name, Key=file_name, Body=data)
            logger.info(f"File saved to S3/MinIO: {file_name}")
            return True
        except Exception as e:
            logger.error(f"S3 Upload Failed: {str(e)}")
            return False

    def exists(self, file_name: str) -> bool:
        try:
            self.s3.head_object(Bucket=self.bucket_name, Key=file_name)
            return True
        except:
            return False
        

