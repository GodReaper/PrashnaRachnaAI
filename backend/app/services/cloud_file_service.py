"""
Cloud-based file storage service for production deployment
Supports AWS S3, Google Cloud Storage, Azure Blob Storage
"""

import os
import uuid
from pathlib import Path
from typing import Tuple, Optional
from fastapi import UploadFile, HTTPException
from app.schemas.document import FileUploadValidation

try:
    import boto3
    from botocore.exceptions import ClientError
    AWS_AVAILABLE = True
except ImportError:
    AWS_AVAILABLE = False

try:
    from google.cloud import storage as gcs
    GCP_AVAILABLE = True
except ImportError:
    GCP_AVAILABLE = False

class CloudFileStorageService:
    """Cloud-based file storage service for production"""
    
    def __init__(self, storage_type: str = "aws_s3", **config):
        self.storage_type = storage_type.lower()
        self.config = config
        
        if self.storage_type == "aws_s3":
            self._init_aws_s3()
        elif self.storage_type == "gcp":
            self._init_gcp()
        elif self.storage_type == "azure":
            self._init_azure()
        else:
            raise ValueError(f"Unsupported storage type: {storage_type}")
    
    def _init_aws_s3(self):
        """Initialize AWS S3 client"""
        if not AWS_AVAILABLE:
            raise ImportError("boto3 not installed. Run: pip install boto3")
        
        self.bucket_name = self.config.get("bucket_name") or os.getenv("AWS_S3_BUCKET")
        if not self.bucket_name:
            raise ValueError("AWS S3 bucket name not provided")
        
        # Initialize S3 client
        aws_access_key = os.getenv("AWS_ACCESS_KEY_ID")
        aws_secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")
        aws_region = os.getenv("AWS_DEFAULT_REGION", "us-east-1")
        
        if aws_access_key and aws_secret_key:
            self.s3_client = boto3.client(
                's3',
                aws_access_key_id=aws_access_key,
                aws_secret_access_key=aws_secret_key,
                region_name=aws_region
            )
        else:
            # Use IAM roles if keys not provided
            self.s3_client = boto3.client('s3', region_name=aws_region)
    
    def _init_gcp(self):
        """Initialize Google Cloud Storage client"""
        if not GCP_AVAILABLE:
            raise ImportError("google-cloud-storage not installed. Run: pip install google-cloud-storage")
        
        self.bucket_name = self.config.get("bucket_name") or os.getenv("GCP_STORAGE_BUCKET")
        if not self.bucket_name:
            raise ValueError("GCP Storage bucket name not provided")
        
        # Initialize GCS client
        credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
        if credentials_path:
            self.gcs_client = gcs.Client.from_service_account_json(credentials_path)
        else:
            self.gcs_client = gcs.Client()  # Use default credentials
        
        self.bucket = self.gcs_client.bucket(self.bucket_name)
    
    def _init_azure(self):
        """Initialize Azure Blob Storage client"""
        try:
            from azure.storage.blob import BlobServiceClient
        except ImportError:
            raise ImportError("azure-storage-blob not installed. Run: pip install azure-storage-blob")
        
        connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
        account_name = os.getenv("AZURE_STORAGE_ACCOUNT_NAME")
        account_key = os.getenv("AZURE_STORAGE_ACCOUNT_KEY")
        
        if connection_string:
            self.blob_client = BlobServiceClient.from_connection_string(connection_string)
        elif account_name and account_key:
            self.blob_client = BlobServiceClient(
                account_url=f"https://{account_name}.blob.core.windows.net",
                credential=account_key
            )
        else:
            raise ValueError("Azure storage credentials not provided")
        
        self.container_name = self.config.get("container_name") or os.getenv("AZURE_CONTAINER_NAME", "documents")
    
    def validate_file(self, file: UploadFile) -> Tuple[bool, str]:
        """Validate uploaded file - same as local service"""
        if not file.filename:
            return False, "No file provided"
        
        if not FileUploadValidation.validate_file_type(file.content_type):
            allowed_types = ", ".join(FileUploadValidation.ALLOWED_MIME_TYPES)
            return False, f"Invalid file type. Allowed types: {allowed_types}"
        
        # Check file size
        file.file.seek(0, 2)
        file_size = file.file.tell()
        file.file.seek(0)
        
        if not FileUploadValidation.validate_file_size(file_size):
            max_size_mb = FileUploadValidation.MAX_FILE_SIZE / (1024 * 1024)
            return False, f"File too large. Maximum size: {max_size_mb}MB"
        
        return True, ""
    
    def generate_cloud_path(self, user_id: int, filename: str, content_type: str) -> str:
        """Generate cloud storage path"""
        file_extension = FileUploadValidation.get_file_extension(content_type)
        unique_id = str(uuid.uuid4())
        unique_filename = f"{unique_id}.{file_extension}"
        
        # Path: documents/{file_type}/{user_id}/{filename}
        return f"documents/{file_extension}/{user_id}/{unique_filename}"
    
    def save_file(self, file: UploadFile, user_id: int) -> Tuple[str, str, int]:
        """Save file to cloud storage"""
        # Validate file
        is_valid, error_message = self.validate_file(file)
        if not is_valid:
            raise HTTPException(status_code=400, detail=error_message)
        
        # Generate cloud path
        cloud_path = self.generate_cloud_path(user_id, file.filename, file.content_type)
        
        # Get file content
        file.file.seek(0)
        file_content = file.file.read()
        file_size = len(file_content)
        
        try:
            if self.storage_type == "aws_s3":
                self._upload_to_s3(cloud_path, file_content, file.content_type)
            elif self.storage_type == "gcp":
                self._upload_to_gcs(cloud_path, file_content, file.content_type)
            elif self.storage_type == "azure":
                self._upload_to_azure(cloud_path, file_content, file.content_type)
            
            # Return cloud path as file_path, extract filename from path
            filename = Path(cloud_path).name
            return cloud_path, filename, file_size
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to upload file: {str(e)}")
    
    def _upload_to_s3(self, key: str, content: bytes, content_type: str):
        """Upload file to AWS S3"""
        try:
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=key,
                Body=content,
                ContentType=content_type,
                ServerSideEncryption='AES256'  # Encrypt at rest
            )
        except ClientError as e:
            raise Exception(f"S3 upload failed: {e}")
    
    def _upload_to_gcs(self, path: str, content: bytes, content_type: str):
        """Upload file to Google Cloud Storage"""
        try:
            blob = self.bucket.blob(path)
            blob.upload_from_string(content, content_type=content_type)
        except Exception as e:
            raise Exception(f"GCS upload failed: {e}")
    
    def _upload_to_azure(self, path: str, content: bytes, content_type: str):
        """Upload file to Azure Blob Storage"""
        try:
            blob_client = self.blob_client.get_blob_client(
                container=self.container_name, 
                blob=path
            )
            blob_client.upload_blob(
                content, 
                content_type=content_type,
                overwrite=True
            )
        except Exception as e:
            raise Exception(f"Azure upload failed: {e}")
    
    def delete_file(self, file_path: str) -> bool:
        """Delete file from cloud storage"""
        try:
            if self.storage_type == "aws_s3":
                self.s3_client.delete_object(Bucket=self.bucket_name, Key=file_path)
            elif self.storage_type == "gcp":
                blob = self.bucket.blob(file_path)
                blob.delete()
            elif self.storage_type == "azure":
                blob_client = self.blob_client.get_blob_client(
                    container=self.container_name, 
                    blob=file_path
                )
                blob_client.delete_blob()
            
            return True
        except Exception:
            return False
    
    def get_file_url(self, file_path: str, expiry_seconds: int = 3600) -> str:
        """Generate signed URL for file access"""
        try:
            if self.storage_type == "aws_s3":
                return self.s3_client.generate_presigned_url(
                    'get_object',
                    Params={'Bucket': self.bucket_name, 'Key': file_path},
                    ExpiresIn=expiry_seconds
                )
            elif self.storage_type == "gcp":
                blob = self.bucket.blob(file_path)
                return blob.generate_signed_url(
                    expiration=expiry_seconds,
                    method="GET"
                )
            elif self.storage_type == "azure":
                # Azure Blob signed URL implementation
                # Would need additional setup for SAS tokens
                return f"https://{self.blob_client.account_name}.blob.core.windows.net/{self.container_name}/{file_path}"
            
        except Exception as e:
            raise Exception(f"Failed to generate file URL: {e}")
    
    def download_file(self, file_path: str) -> bytes:
        """Download file content for processing"""
        try:
            if self.storage_type == "aws_s3":
                response = self.s3_client.get_object(Bucket=self.bucket_name, Key=file_path)
                return response['Body'].read()
            elif self.storage_type == "gcp":
                blob = self.bucket.blob(file_path)
                return blob.download_as_bytes()
            elif self.storage_type == "azure":
                blob_client = self.blob_client.get_blob_client(
                    container=self.container_name, 
                    blob=file_path
                )
                return blob_client.download_blob().readall()
            
        except Exception as e:
            raise Exception(f"Failed to download file: {e}")

# Factory function to create appropriate storage service
def create_file_storage_service():
    """Create file storage service based on environment"""
    storage_type = os.getenv("FILE_STORAGE_TYPE", "local").lower()
    
    if storage_type == "local":
        from app.services.file_service import FileStorageService
        return FileStorageService()
    elif storage_type in ["aws_s3", "s3"]:
        return CloudFileStorageService("aws_s3")
    elif storage_type in ["gcp", "google"]:
        return CloudFileStorageService("gcp")
    elif storage_type in ["azure", "azure_blob"]:
        return CloudFileStorageService("azure")
    else:
        raise ValueError(f"Unknown storage type: {storage_type}")

# Global service instance - will be local for dev, cloud for production
file_storage_service = create_file_storage_service() 