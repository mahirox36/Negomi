from __future__ import annotations

from typing import Optional, Tuple, BinaryIO
from fastapi import HTTPException, UploadFile
import boto3
import logging
import uuid
from mypy_boto3_s3.client import S3Client

class StorageConfig:
    def __init__(
        self,
        endpoint: str,
        access_key: str,
        secret_key: str,
        bucket_name: str,
        public_url: str
    ) -> None:
        if not endpoint.startswith(('http://', 'https://')):
            raise ValueError("Invalid endpoint URL. Must start with http:// or https://")
        self.endpoint = endpoint.rstrip('/')
        self.access_key = access_key
        self.secret_key = secret_key
        self.bucket_name = bucket_name
        self.public_url = public_url.rstrip('/')

class StorageManager:
    """Manages file storage operations using S3-compatible storage"""

    def __init__(self, config: StorageConfig) -> None:
        self.logger = logging.getLogger("bot")
        self.config = config
        self.s3_client: Optional[S3Client] = None
        self._initialize_client()

    def _initialize_client(self) -> None:
        """Initialize the S3 client"""
        try:
            self.s3_client = boto3.client(
                "s3",
                endpoint_url=self.config.endpoint,
                aws_access_key_id=self.config.access_key,
                aws_secret_access_key=self.config.secret_key,
                region_name="auto"
            )
        except Exception as e:
            self.logger.error(f"Failed to initialize S3 client: {str(e)}")
            self.s3_client = None

    async def upload_file(self, file: UploadFile, prefix: str = "") -> Tuple[str, str]:
        """
        Upload a file to storage
        
        Parameters
        ----------
        file: UploadFile
            The file to upload
        prefix: str
            Optional prefix for the filename
            
        Returns
        -------
        Tuple[str, str]
            (public_url, internal_url)
        """
        if not self.s3_client:
            raise HTTPException(status_code=500, detail="Storage not initialized")

        try:
            # Generate unique filename
            unique_filename = f"{prefix}{uuid.uuid4()}-{file.filename}"
            
            # Upload file
            await self._upload_fileobj(file.file, unique_filename)
            
            # Return public and internal URLs
            return (
                f"{self.config.public_url}/{unique_filename}",
                f"{self.config.endpoint}/{self.config.bucket_name}/{unique_filename}"
            )

        except Exception as e:
            self.logger.error(f"Failed to upload file: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to upload file")

    async def _upload_fileobj(self, file: BinaryIO, key: str) -> None:
        """Upload a file object to storage"""
        if not self.s3_client:
            raise HTTPException(status_code=500, detail="Storage not initialized")

        self.s3_client.upload_fileobj(
            file,
            self.config.bucket_name,
            key,
            ExtraArgs={"ACL": "public-read"}
        )

    async def delete_file(self, filename: str) -> None:
        """Delete a file from storage"""
        if not self.s3_client:
            raise HTTPException(status_code=500, detail="Storage not initialized")

        try:
            self.s3_client.delete_object(
                Bucket=self.config.bucket_name,
                Key=filename
            )
        except Exception as e:
            self.logger.error(f"Failed to delete file: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to delete file")