from fastapi import APIRouter, Depends, File, UploadFile, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from auth.clerk_auth import clerk_auth
from config.database import get_db
from app.services.user_service import UserService
from app.services.document_service import DocumentService
from app.services.file_service import file_storage_service
from app.schemas.document import (
    DocumentUploadResponse, 
    DocumentListResponse,
    FileUploadValidation
)

router = APIRouter(prefix="/documents", tags=["Documents"])

@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    current_user: Dict[str, Any] = Depends(clerk_auth.get_current_user),
    db: Session = Depends(get_db)
):
    """
    Upload a document with validation
    
    Supported file types:
    - PDF (.pdf)
    - Microsoft Word (.docx)
    - Microsoft PowerPoint (.pptx)
    
    Maximum file size: 50MB
    """
    
    # Get or create user in database
    # Note: Clerk JWT may not include email/name by default
    user_data = {
        "clerk_user_id": current_user.get("user_id"),
        "email": current_user.get("email") or "",
        "first_name": current_user.get("first_name") or "",
        "last_name": current_user.get("last_name") or "",
    }
    
    try:
        user = UserService.get_or_create_user(db, user_data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"User service error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error during user setup: {str(e)}")
    
    # Validate and save file
    try:
        file_path, unique_filename, file_size = file_storage_service.save_file(file, user.id)
    except HTTPException:
        raise  # Re-raise validation errors
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File save failed: {str(e)}")
    
    # Create document record in database
    try:
        document = DocumentService.create_document(
            db=db,
            user_id=user.id,
            filename=unique_filename,
            original_filename=file.filename,
            file_path=file_path,
            file_size=file_size,
            mime_type=file.content_type
        )
        
        return DocumentUploadResponse.from_orm(document)
        
    except Exception as e:
        # Clean up file if database operation fails
        file_storage_service.delete_file(file_path)
        raise HTTPException(status_code=500, detail=f"Document creation failed: {str(e)}")

@router.get("/", response_model=List[DocumentListResponse])
async def list_documents(
    skip: int = Query(0, ge=0, description="Number of documents to skip"),
    limit: int = Query(10, ge=1, le=100, description="Number of documents to return"),
    current_user: Dict[str, Any] = Depends(clerk_auth.get_current_user),
    db: Session = Depends(get_db)
):
    """Get list of user's documents with pagination"""
    
    # Get user from database
    user = UserService.get_user_by_clerk_id(db, current_user.get("user_id"))
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    documents = DocumentService.get_user_documents(db, user.id, skip, limit)
    return [DocumentListResponse.from_orm(doc) for doc in documents]

@router.get("/{document_id}", response_model=DocumentUploadResponse)
async def get_document(
    document_id: int,
    current_user: Dict[str, Any] = Depends(clerk_auth.get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific document by ID"""
    
    # Get user from database
    user = UserService.get_user_by_clerk_id(db, current_user.get("user_id"))
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    document = DocumentService.get_document_by_id(db, document_id, user.id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    return DocumentUploadResponse.from_orm(document)

@router.delete("/{document_id}")
async def delete_document(
    document_id: int,
    current_user: Dict[str, Any] = Depends(clerk_auth.get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a document and its associated file"""
    
    # Get user from database
    user = UserService.get_user_by_clerk_id(db, current_user.get("user_id"))
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get document first to retrieve file path
    document = DocumentService.get_document_by_id(db, document_id, user.id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Delete file from storage
    file_deleted = file_storage_service.delete_file(document.file_path)
    
    # Delete document from database
    db_deleted = DocumentService.delete_document(db, document_id, user.id)
    
    if db_deleted:
        return {
            "message": "Document deleted successfully",
            "file_deleted": file_deleted,
            "document_id": document_id
        }
    else:
        raise HTTPException(status_code=500, detail="Failed to delete document")

@router.get("/stats/summary")
async def get_document_stats(
    current_user: Dict[str, Any] = Depends(clerk_auth.get_current_user),
    db: Session = Depends(get_db)
):
    """Get document statistics for the user"""
    
    # Get user from database
    user = UserService.get_user_by_clerk_id(db, current_user.get("user_id"))
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    stats = DocumentService.get_document_stats(db, user.id)
    return stats

@router.get("/search/")
async def search_documents(
    q: str = Query(..., min_length=1, description="Search query"),
    file_type: Optional[str] = Query(None, description="Filter by file type (pdf, docx, pptx)"),
    current_user: Dict[str, Any] = Depends(clerk_auth.get_current_user),
    db: Session = Depends(get_db)
):
    """Search documents by filename or content"""
    
    # Get user from database
    user = UserService.get_user_by_clerk_id(db, current_user.get("user_id"))
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Validate file_type if provided
    if file_type and file_type not in ["pdf", "docx", "pptx"]:
        raise HTTPException(status_code=400, detail="Invalid file type. Allowed: pdf, docx, pptx")
    
    documents = DocumentService.search_documents(db, user.id, q, file_type)
    return [DocumentListResponse.from_orm(doc) for doc in documents]

@router.get("/validate/file-types")
async def get_supported_file_types():
    """Get information about supported file types and limits"""
    return {
        "supported_types": {
            "PDF": {
                "mime_type": "application/pdf",
                "extension": "pdf",
                "description": "Portable Document Format"
            },
            "DOCX": {
                "mime_type": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                "extension": "docx",
                "description": "Microsoft Word Document"
            },
            "PPTX": {
                "mime_type": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
                "extension": "pptx",
                "description": "Microsoft PowerPoint Presentation"
            }
        },
        "limits": {
            "max_file_size_bytes": FileUploadValidation.MAX_FILE_SIZE,
            "max_file_size_mb": FileUploadValidation.MAX_FILE_SIZE / (1024 * 1024)
        }
    } 