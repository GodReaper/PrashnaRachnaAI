from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey, BigInteger
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from config.database import Base

class Document(Base):
    __tablename__ = "documents"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    filename = Column(String, nullable=False)
    original_filename = Column(String, nullable=False)
    file_path = Column(String, nullable=False)  # Path where file is stored
    file_type = Column(String, nullable=False)  # pdf, docx, pptx
    file_size = Column(BigInteger, nullable=False)  # File size in bytes
    mime_type = Column(String, nullable=False)
    
    # Processing status
    is_processed = Column(Boolean, default=False)
    processing_status = Column(String, default="pending")  # pending, processing, completed, failed
    processing_error = Column(Text, nullable=True)
    
    # Document content
    text_content = Column(Text, nullable=True)  # Extracted text
    chunk_count = Column(Integer, default=0)  # Number of chunks created
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    processed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="documents")
    questions = relationship("Question", back_populates="document", cascade="all, delete-orphan")
    chunks = relationship("DocumentChunk", back_populates="document", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Document(id={self.id}, filename='{self.filename}', type='{self.file_type}')>"

class DocumentChunk(Base):
    __tablename__ = "document_chunks"
    
    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False)
    chunk_index = Column(Integer, nullable=False)  # Order of chunk in document
    content = Column(Text, nullable=False)  # Chunk text content
    word_count = Column(Integer, nullable=False)
    character_count = Column(Integer, nullable=False)
    
    # Vector store reference
    vector_id = Column(String, nullable=True)  # Reference to ChromaDB vector
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    document = relationship("Document", back_populates="chunks")
    
    def __repr__(self):
        return f"<DocumentChunk(id={self.id}, doc_id={self.document_id}, index={self.chunk_index})>" 