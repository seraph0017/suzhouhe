"""
MinIO / S3 Storage Service

File upload and storage management with presigned URL support.
"""

import boto3
from botocore.client import Config
from botocore.exceptions import ClientError
from typing import Optional, Dict, Any, List
from datetime import timedelta
import logging
from io import BytesIO

from app.config import settings

logger = logging.getLogger(__name__)


class MinIOService:
    """MinIO/S3 storage service"""

    def __init__(self):
        self.endpoint_url = f"http://{settings.MINIO_ENDPOINT}"
        self.access_key = settings.MINIO_ACCESS_KEY
        self.secret_key = settings.MINIO_SECRET_KEY
        self.bucket = settings.MINIO_BUCKET
        self.secure = settings.MINIO_SECURE

        self.client = boto3.client(
            's3',
            endpoint_url=self.endpoint_url,
            aws_access_key_id=self.access_key,
            aws_secret_access_key=self.secret_key,
            config=Config(signature_version='s3v4'),
            use_ssl=self.secure,
        )

    def ensure_bucket_exists(self):
        """Ensure the bucket exists, create if not"""
        try:
            self.client.head_bucket(Bucket=self.bucket)
        except ClientError as e:
            if e.response['Error']['Code'] == '404':
                self.client.create_bucket(Bucket=self.bucket)
            else:
                raise

    def upload_file(
        self,
        file_bytes: bytes,
        object_name: str,
        content_type: str = "application/octet-stream",
        extra_metadata: Optional[Dict] = None,
    ) -> str:
        """
        Upload file to MinIO

        Args:
            file_bytes: File content as bytes
            object_name: Object name in bucket
            content_type: MIME type
            extra_metadata: Additional metadata

        Returns:
            Object URL
        """
        try:
            self.ensure_bucket_exists()

            # Upload
            self.client.upload_fileobj(
                BytesIO(file_bytes),
                self.bucket,
                object_name,
                ExtraArgs={
                    'ContentType': content_type,
                    'Metadata': extra_metadata or {},
                }
            )

            # Return presigned URL for access
            return self.get_presigned_url(object_name, http_method="GET")

        except ClientError as e:
            logger.error(f"Upload failed: {e}")
            raise

    def upload_from_bytes(
        self,
        object_name: str,
        file_bytes: bytes,
        content_type: str = "application/octet-stream",
    ) -> str:
        """
        Upload file from bytes (alias for upload_file)

        Args:
            object_name: Object name in bucket
            file_bytes: File content as bytes
            content_type: MIME type

        Returns:
            Presigned URL for access
        """
        return self.upload_file(file_bytes, object_name, content_type)

    def upload_file_large(
        self,
        file_path: str,
        object_name: str,
        content_type: str = "application/octet-stream",
    ) -> str:
        """Upload large file using multipart upload"""
        try:
            self.ensure_bucket_exists()

            self.client.upload_file(
                file_path,
                self.bucket,
                object_name,
                ExtraArgs={
                    'ContentType': content_type,
                }
            )

            return f"{self.endpoint_url}/{self.bucket}/{object_name}"

        except ClientError as e:
            logger.error(f"Upload failed: {e}")
            raise

    def get_presigned_url(
        self,
        object_name: str,
        expiration: int = 3600,
        http_method: str = "PUT",
    ) -> str:
        """
        Generate presigned URL for upload/download

        Args:
            object_name: Object name in bucket
            expiration: URL expiration in seconds
            http_method: HTTP method (PUT for upload, GET for download)

        Returns:
            Presigned URL
        """
        try:
            url = self.client.generate_presigned_url(
                'put_object' if http_method == 'PUT' else 'get_object',
                Params={
                    'Bucket': self.bucket,
                    'Key': object_name,
                },
                ExpiresIn=expiration,
            )
            return url

        except ClientError as e:
            logger.error(f"Presigned URL generation failed: {e}")
            raise

    def download_file(self, object_name: str) -> bytes:
        """Download file from MinIO"""
        try:
            response = self.client.get_object(
                Bucket=self.bucket,
                Key=object_name,
            )
            return response['Body'].read()

        except ClientError as e:
            logger.error(f"Download failed: {e}")
            raise

    def delete_file(self, object_name: str) -> bool:
        """Delete file from MinIO"""
        try:
            self.client.delete_object(
                Bucket=self.bucket,
                Key=object_name,
            )
            return True

        except ClientError as e:
            logger.error(f"Delete failed: {e}")
            return False

    def list_files(self, prefix: str = "") -> List[Dict[str, Any]]:
        """List files in bucket"""
        try:
            response = self.client.list_objects_v2(
                Bucket=self.bucket,
                Prefix=prefix,
            )

            files = []
            for obj in response.get('Contents', []):
                files.append({
                    'key': obj['Key'],
                    'size': obj['Size'],
                    'last_modified': obj['LastModified'],
                    'etag': obj['ETag'],
                })
            return files

        except ClientError as e:
            logger.error(f"List files failed: {e}")
            raise

    def get_file_info(self, object_name: str) -> Optional[Dict[str, Any]]:
        """Get file metadata"""
        try:
            response = self.client.head_object(
                Bucket=self.bucket,
                Key=object_name,
            )
            return {
                'key': object_name,
                'size': response['ContentLength'],
                'content_type': response.get('ContentType'),
                'metadata': response.get('Metadata', {}),
                'last_modified': response['LastModified'],
            }

        except ClientError as e:
            if e.response['Error']['Code'] == '404':
                return None
            logger.error(f"Get file info failed: {e}")
            raise


# Global service instance
minio_service = MinIOService()


# Alias for compatibility
MinIOStorage = MinIOService


def get_minio() -> MinIOService:
    """Get MinIO service instance"""
    return minio_service
