from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List, Optional, Dict, Any
from fastapi import HTTPException
from app.models.document import Document, DocumentChunk
from app.models.user import User
from app.schemas.document import DocumentProcessingStatus, FileUploadValidation

class DocumentService:
    
    @staticmethod
    def create_document(
        db: Session,
        user_id: int,
        filename: str,
        original_filename: str,
        file_path: str,
        file_size: int,
        mime_type: str
    ) -> Document:
        """Create a new document record"""
        try:
            # Get file type from MIME type
            file_type = FileUploadValidation.get_file_extension(mime_type)
            
            document = Document(
                user_id=user_id,
                filename=filename,
                original_filename=original_filename,
                file_path=file_path,
                file_type=file_type,
                file_size=file_size,
                mime_type=mime_type,
                processing_status=DocumentProcessingStatus.PENDING.value
            )
            
            db.add(document)
            db.commit()
            db.refresh(document)
            return document
            
        except IntegrityError as e:
            db.rollback()
            raise HTTPException(status_code=400, detail="Failed to create document record")
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    
    @staticmethod
    def get_document_by_id(db: Session, document_id: int, user_id: int) -> Optional[Document]:
        """Get document by ID, ensuring it belongs to the user"""
        return db.query(Document).filter(
            Document.id == document_id,
            Document.user_id == user_id
        ).first()
    
    @staticmethod
    def get_user_documents(
        db: Session, 
        user_id: int, 
        skip: int = 0, 
        limit: int = 10
    ) -> List[Document]:
        """Get all documents for a user with pagination"""
        return db.query(Document).filter(
            Document.user_id == user_id
        ).order_by(Document.created_at.desc()).offset(skip).limit(limit).all()
    
    @staticmethod
    def update_document_status(
        db: Session,
        document_id: int,
        status: str,
        error_message: Optional[str] = None
    ) -> Optional[Document]:
        """Update document processing status"""
        document = db.query(Document).filter(Document.id == document_id).first()
        if document:
            document.processing_status = status
            if error_message:
                document.processing_error = error_message
            
            if status == DocumentProcessingStatus.COMPLETED.value:
                from datetime import datetime
                document.processed_at = datetime.utcnow()
            
            db.commit()
            db.refresh(document)
        return document
    
    @staticmethod
    def update_document_content(
        db: Session,
        document_id: int,
        text_content: str,
        chunk_count: int = 0
    ) -> Optional[Document]:
        """Update document with extracted content"""
        document = db.query(Document).filter(Document.id == document_id).first()
        if document:
            document.text_content = text_content
            document.chunk_count = chunk_count
            document.is_processed = True
            db.commit()
            db.refresh(document)
        return document
    
    @staticmethod
    def delete_document(db: Session, document_id: int, user_id: int) -> bool:
        """Delete a document and its associated data"""
        document = DocumentService.get_document_by_id(db, document_id, user_id)
        if document:
            try:
                # Delete associated chunks and questions (cascade should handle this)
                db.delete(document)
                db.commit()
                return True
            except Exception as e:
                db.rollback()
                raise HTTPException(status_code=500, detail=f"Failed to delete document: {str(e)}")
        return False
    
    @staticmethod
    def get_document_stats(db: Session, user_id: int) -> Dict[str, Any]:
        """Get document statistics for a user"""
        documents = db.query(Document).filter(Document.user_id == user_id).all()
        
        total_count = len(documents)
        processed_count = len([d for d in documents if d.is_processed])
        pending_count = len([d for d in documents if d.processing_status == DocumentProcessingStatus.PENDING.value])
        failed_count = len([d for d in documents if d.processing_status == DocumentProcessingStatus.FAILED.value])
        
        total_size = sum(d.file_size for d in documents)
        
        file_types = {}
        for doc in documents:
            file_types[doc.file_type] = file_types.get(doc.file_type, 0) + 1
        
        return {
            "total_documents": total_count,
            "processed_documents": processed_count,
            "pending_documents": pending_count,
            "failed_documents": failed_count,
            "total_size_bytes": total_size,
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "file_types": file_types
        }
    
    @staticmethod
    def search_documents(
        db: Session,
        user_id: int,
        query: str,
        file_type: Optional[str] = None
    ) -> List[Document]:
        """Search documents by filename or content"""
        filters = [Document.user_id == user_id]
        
        # Add text search filter
        if query:
            search_filter = (
                Document.original_filename.ilike(f"%{query}%") |
                Document.text_content.ilike(f"%{query}%")
            )
            filters.append(search_filter)
        
        # Add file type filter
        if file_type:
            filters.append(Document.file_type == file_type)
        
        return db.query(Document).filter(*filters).order_by(
            Document.created_at.desc()
        ).all() 