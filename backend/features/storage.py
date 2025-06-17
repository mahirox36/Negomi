from __future__ import annotations

from typing import Optional, Tuple, BinaryIO
from fastapi import HTTPException, UploadFile
import boto3
import logging
import uuid
from mypy_boto3_s3.client import S3Client
from concurrent.futures import ThreadPoolExecutor
import asyncio
from botocore.config import Config

class StorageConfig:
    def __init__(
        self,
        endpoint: str,
        access_key: str,
        secret_key: str,
        bucket_name: str,
        public_url: str,
    ) -> None:
        if not endpoint.startswith(("http://", "https://")):
            raise ValueError(
                "Invalid endpoint URL. Must start with http:// or https://"
            )
        self.endpoint = endpoint.rstrip("/")
        self.access_key = access_key
        self.secret_key = secret_key
        self.bucket_name = bucket_name
        self.public_url = public_url.rstrip("/")


class StorageManager:
    """Manages file storage operations using S3-compatible storage"""

    def __init__(self, config: StorageConfig) -> None:
        self.logger = logging.getLogger(__name__)
        self.config = config
        self.s3_client: Optional[S3Client] = None
        self._initialize_client()

    def _initialize_client(self) -> None:
        """Initialize the S3 client with optimized settings"""
        try:
            

            config = Config(
                retries={
                    'max_attempts': 3,
                    'mode': 'adaptive'
                },
                max_pool_connections=50,
                connect_timeout=10,
                read_timeout=30
            )

            self.s3_client = boto3.client(
                "s3",
                endpoint_url=self.config.endpoint,
                aws_access_key_id=self.config.access_key,
                aws_secret_access_key=self.config.secret_key,
                region_name="auto",
                config=config
            ) # type: ignore
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
            
            # Reset file position to beginning
            await file.seek(0)
            
            # Upload file directly without reading into memory
            await self._upload_fileobj(file.file, unique_filename)
            
            # Return public and internal URLs
            return (
                f"{self.config.public_url}/{unique_filename}",
                f"{self.config.endpoint}/{self.config.bucket_name}/{unique_filename}",
            )
        except Exception as e:
            self.logger.error(f"Failed to upload file: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to upload file")
    
    async def _upload_fileobj(self, file: BinaryIO, key: str) -> None:
        """Upload a file object to storage with better async handling"""
        if not self.s3_client:
            raise HTTPException(status_code=500, detail="Storage not initialized")
        
        # Use a dedicated thread pool for I/O operations
        if not hasattr(self, '_upload_executor'):
            self._upload_executor = ThreadPoolExecutor(max_workers=4, thread_name_prefix="s3-upload")
        
        loop = asyncio.get_event_loop()
        try:
            await loop.run_in_executor(
                self._upload_executor,
                self._sync_upload,
                file,
                key
            )
        except Exception as e:
            self.logger.error(f"S3 upload failed: {str(e)}")
            raise
        
    def _sync_upload(self, file: BinaryIO, key: str) -> None:
        """Synchronous upload method"""
        try:
            if not self.s3_client:
                raise Exception("s3_client isn't `initialized`")
            self.s3_client.upload_fileobj(
                file,
                self.config.bucket_name,
                key,
                ExtraArgs={
                    'ContentType': self._get_content_type(key),
                    'ACL': 'public-read'  # Adjust based on your needs
                }
            )
        except Exception as e:
            self.logger.error(f"Direct S3 upload failed: {str(e)}")
            raise
        
    def _get_content_type(self, filename: str) -> str:
        """Get content type based on file extension"""
        extension = filename.lower().split('.')[-1]
        content_types = {
            'jpg': 'image/jpeg',
            'jpeg': 'image/jpeg',
            'png': 'image/png',
            'gif': 'image/gif',
            'webp': 'image/webp'
        }
        return content_types.get(extension, 'application/octet-stream')

    async def delete_file(self, filename: str) -> None:
        """Delete a file from storage"""
        if not self.s3_client:
            raise HTTPException(status_code=500, detail="Storage not initialized")

        try:
            self.s3_client.delete_object(Bucket=self.config.bucket_name, Key=filename)
        except Exception as e:
            self.logger.error(f"Failed to delete file: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to delete file")

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        # Explicitly clean up the S3 client reference
        if self.s3_client:
            self.s3_client.close()
            self.s3_client = None
