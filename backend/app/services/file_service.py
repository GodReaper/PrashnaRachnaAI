import os
import uuid
import shutil
from pathlib import Path
from typing import Tuple, Optional
from fastapi import UploadFile, HTTPException
from app.schemas.document import FileUploadValidation

class FileStorageService:
    """Service for handling file storage operations"""
    
    def __init__(self, upload_directory: str = "uploads"):
        self.upload_directory = Path(upload_directory)
        self.upload_directory.mkdir(exist_ok=True)
        
        # Create subdirectories for different file types
        for file_type in ["pdf", "docx", "pptx"]:
            (self.upload_directory / file_type).mkdir(exist_ok=True)
    
    def validate_file(self, file: UploadFile) -> Tuple[bool, str]:
        """
        Validate uploaded file
        Returns: (is_valid, error_message)
        """
        # Check if file exists
        if not file.filename:
            return False, "No file provided"
        
        # Check MIME type
        if not FileUploadValidation.validate_file_type(file.content_type):
            allowed_types = ", ".join(FileUploadValidation.ALLOWED_MIME_TYPES)
            return False, f"Invalid file type. Allowed types: {allowed_types}"
        
        # Check file size (read file to get actual size)
        file.file.seek(0, 2)  # Seek to end
        file_size = file.file.tell()
        file.file.seek(0)  # Reset to beginning
        
        if not FileUploadValidation.validate_file_size(file_size):
            max_size_mb = FileUploadValidation.MAX_FILE_SIZE / (1024 * 1024)
            return False, f"File too large. Maximum size: {max_size_mb}MB"
        
        return True, ""
    
    def generate_unique_filename(self, original_filename: str, content_type: str) -> str:
        """Generate a unique filename while preserving the extension"""
        file_extension = FileUploadValidation.get_file_extension(content_type)
        unique_id = str(uuid.uuid4())
        return f"{unique_id}.{file_extension}"
    
    def save_file(self, file: UploadFile, user_id: int) -> Tuple[str, str, int]:
        """
        Save uploaded file to disk
        Returns: (file_path, unique_filename, file_size)
        """
        # Validate file first
        is_valid, error_message = self.validate_file(file)
        if not is_valid:
            raise HTTPException(status_code=400, detail=error_message)
        
        # Generate unique filename
        unique_filename = self.generate_unique_filename(file.filename, file.content_type)
        
        # Determine subdirectory based on file type
        file_extension = FileUploadValidation.get_file_extension(file.content_type)
        subdirectory = self.upload_directory / file_extension
        
        # Create user-specific subdirectory
        user_directory = subdirectory / str(user_id)
        user_directory.mkdir(exist_ok=True)
        
        # Full file path
        file_path = user_directory / unique_filename
        
        try:
            # Save file
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            
            # Get file size
            file_size = file_path.stat().st_size
            
            return str(file_path), unique_filename, file_size
            
        except Exception as e:
            # Clean up on error
            if file_path.exists():
                file_path.unlink()
            raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")
    
    def delete_file(self, file_path: str) -> bool:
        """Delete a file from storage"""
        try:
            path = Path(file_path)
            if path.exists():
                path.unlink()
                return True
            return False
        except Exception:
            return False
    
    def get_file_info(self, file_path: str) -> Optional[dict]:
        """Get file information"""
        try:
            path = Path(file_path)
            if path.exists():
                stat = path.stat()
                return {
                    "size": stat.st_size,
                    "created": stat.st_ctime,
                    "modified": stat.st_mtime,
                    "exists": True
                }
            return {"exists": False}
        except Exception:
            return {"exists": False}
    
    def cleanup_user_files(self, user_id: int) -> int:
        """Clean up all files for a user"""
        deleted_count = 0
        user_pattern = f"*/{user_id}/*"
        
        for file_path in self.upload_directory.glob(user_pattern):
            if file_path.is_file():
                try:
                    file_path.unlink()
                    deleted_count += 1
                except Exception:
                    pass
        
        return deleted_count

# Global file storage service instance
file_storage_service = FileStorageService() 