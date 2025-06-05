from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime
from enum import Enum

class FileTypeEnum(str, Enum):
    """Allowed file types for document upload"""
    PDF = "application/pdf"
    DOCX = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    PPTX = "application/vnd.openxmlformats-officedocument.presentationml.presentation"

class DocumentUploadResponse(BaseModel):
    """Response schema for document upload"""
    id: int
    filename: str
    original_filename: str
    file_type: str
    file_size: int
    mime_type: str
    processing_status: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class DocumentListResponse(BaseModel):
    """Response schema for document listing"""
    id: int
    filename: str
    original_filename: str
    file_type: str
    file_size: int
    is_processed: bool
    processing_status: str
    chunk_count: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class FileUploadValidation:
    """File upload validation utilities"""
    
    # Allowed MIME types
    ALLOWED_MIME_TYPES = {
        FileTypeEnum.PDF.value,
        FileTypeEnum.DOCX.value,
        FileTypeEnum.PPTX.value
    }
    
    # File extensions mapping
    MIME_TO_EXTENSION = {
        FileTypeEnum.PDF.value: "pdf",
        FileTypeEnum.DOCX.value: "docx", 
        FileTypeEnum.PPTX.value: "pptx"
    }
    
    # Maximum file size (50MB)
    MAX_FILE_SIZE = 50 * 1024 * 1024
    
    @staticmethod
    def validate_file_type(content_type: str) -> bool:
        """Validate if the file type is allowed"""
        return content_type in FileUploadValidation.ALLOWED_MIME_TYPES
    
    @staticmethod
    def validate_file_size(file_size: int) -> bool:
        """Validate if the file size is within limits"""
        return 0 < file_size <= FileUploadValidation.MAX_FILE_SIZE
    
    @staticmethod
    def get_file_extension(content_type: str) -> str:
        """Get file extension from MIME type"""
        return FileUploadValidation.MIME_TO_EXTENSION.get(content_type, "unknown")

class DocumentProcessingStatus(str, Enum):
    """Document processing status options"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed" 