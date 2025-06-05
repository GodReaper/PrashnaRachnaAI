"""
Document parsing service using LangChain
Handles PDF, DOCX, PPTX files and converts them to semantic chunks
"""

import logging
import os
import tempfile
from typing import List, Dict, Any, Optional
from pathlib import Path

# LangChain imports
from langchain_community.document_loaders import (
    PyPDFLoader,
    Docx2txtLoader,
    UnstructuredPowerPointLoader
)
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.schema import Document

# Internal imports
from app.services.chromadb_service import chromadb_service
from app.services.document_service import DocumentService
from app.services.embedding_service import embedding_service
from config.database import get_db

logger = logging.getLogger(__name__)

class DocumentParsingService:
    """Service for parsing documents and creating semantic chunks"""
    
    def __init__(self):
        """Initialize the document parsing service"""
        # Text splitter configuration
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,  # Characters per chunk
            chunk_overlap=200,  # Overlap between chunks
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )
        
        # Supported file types mapping
        self.loader_mapping = {
            '.pdf': PyPDFLoader,
            '.docx': Docx2txtLoader,
            '.pptx': UnstructuredPowerPointLoader
        }
    
    def parse_document(
        self, 
        file_path: str, 
        document_id: int, 
        user_id: str,
        db_session = None
    ) -> Dict[str, Any]:
        """
        Parse a document and store chunks in ChromaDB
        
        Args:
            file_path: Path to the uploaded document
            document_id: Database document ID
            user_id: User who uploaded the document
        
        Returns:
            Dict with parsing results
        """
        try:
            logger.info(f"Starting document parsing for document_id: {document_id}")
            
            # Get file extension
            file_extension = Path(file_path).suffix.lower()
            
            if file_extension not in self.loader_mapping:
                raise ValueError(f"Unsupported file type: {file_extension}")
            
            # Load document
            documents = self._load_document(file_path, file_extension)
            
            # Split into chunks
            chunks = self._create_chunks(documents)
            
            # Prepare chunk data for ChromaDB
            chunk_data = self._prepare_chunk_data(chunks, document_id, user_id, file_path)
            
            # Generate embeddings for chunks
            chunk_texts = [chunk["text"] for chunk in chunk_data]
            embeddings_data = embedding_service.generate_embeddings(chunk_texts)
            
            # Add embeddings to chunk data
            for i, chunk in enumerate(chunk_data):
                if i < len(embeddings_data):
                    chunk["embedding"] = embeddings_data[i]["embedding"]
                    chunk["embedding_model"] = embeddings_data[i]["embedding_model"]
            
            # Store in ChromaDB
            success = chromadb_service.add_document_chunks(document_id, chunk_data)
            
            if not success:
                raise Exception("Failed to store chunks in ChromaDB")
            
            # Update document status in database
            if db_session:
                DocumentService.update_document_status(db_session, document_id, "completed")
            
            result = {
                "success": True,
                "document_id": document_id,
                "total_chunks": len(chunk_data),
                "total_characters": sum(len(chunk["text"]) for chunk in chunk_data),
                "file_type": file_extension,
                "chunks_preview": chunk_data[:3] if chunk_data else []  # First 3 chunks for preview
            }
            
            logger.info(f"Document parsing completed: {result}")
            return result
            
        except Exception as e:
            logger.error(f"Document parsing failed for document_id {document_id}: {e}")
            
            # Update document status to failed
            try:
                if db_session:
                    DocumentService.update_document_status(db_session, document_id, "failed", str(e))
            except Exception as status_error:
                logger.error(f"Failed to update document status: {status_error}")
            
            return {
                "success": False,
                "error": str(e),
                "document_id": document_id
            }
    
    def _load_document(self, file_path: str, file_extension: str) -> List[Document]:
        """Load document using appropriate LangChain loader"""
        try:
            loader_class = self.loader_mapping[file_extension]
            loader = loader_class(file_path)
            documents = loader.load()
            
            logger.info(f"Loaded {len(documents)} document sections from {file_extension} file")
            return documents
            
        except Exception as e:
            logger.error(f"Failed to load document {file_path}: {e}")
            raise Exception(f"Document loading failed: {e}")
    
    def _create_chunks(self, documents: List[Document]) -> List[Document]:
        """Split documents into semantic chunks"""
        try:
            # Split all documents into chunks
            chunks = self.text_splitter.split_documents(documents)
            
            logger.info(f"Created {len(chunks)} chunks from {len(documents)} document sections")
            return chunks
            
        except Exception as e:
            logger.error(f"Failed to create chunks: {e}")
            raise Exception(f"Chunk creation failed: {e}")
    
    def _prepare_chunk_data(
        self, 
        chunks: List[Document], 
        document_id: int, 
        user_id: str, 
        file_path: str
    ) -> List[Dict[str, Any]]:
        """Prepare chunk data for ChromaDB storage"""
        try:
            chunk_data = []
            filename = Path(file_path).name
            
            for i, chunk in enumerate(chunks):
                # Extract text content
                text_content = chunk.page_content.strip()
                
                # Skip empty chunks
                if not text_content:
                    continue
                
                # Extract metadata from chunk
                chunk_metadata = chunk.metadata or {}
                
                # Prepare chunk data
                chunk_info = {
                    "text": text_content,
                    "metadata": {
                        "filename": filename,
                        "file_path": file_path,
                        "user_id": user_id,
                        "chunk_index": i,
                        "word_count": len(text_content.split()),
                        "character_count": len(text_content),
                        **chunk_metadata  # Include original metadata from loader
                    },
                    "page_number": chunk_metadata.get("page", i + 1)  # Use page from metadata or chunk index
                }
                
                chunk_data.append(chunk_info)
            
            logger.info(f"Prepared {len(chunk_data)} chunks for storage")
            return chunk_data
            
        except Exception as e:
            logger.error(f"Failed to prepare chunk data: {e}")
            raise Exception(f"Chunk data preparation failed: {e}")
    
    def get_document_chunks_summary(self, document_id: int) -> Dict[str, Any]:
        """Get summary of chunks for a document"""
        try:
            chunks = chromadb_service.get_document_chunks(document_id)
            
            if not chunks:
                return {"document_id": document_id, "total_chunks": 0, "chunks": []}
            
            # Create summary
            summary = {
                "document_id": document_id,
                "total_chunks": len(chunks),
                "total_characters": sum(len(chunk["text"]) for chunk in chunks),
                "total_words": sum(chunk["metadata"].get("word_count", 0) for chunk in chunks),
                "chunk_preview": []
            }
            
            # Add preview of first few chunks
            for chunk in chunks[:3]:
                preview = {
                    "chunk_id": chunk["id"],
                    "text_preview": chunk["text"][:200] + "..." if len(chunk["text"]) > 200 else chunk["text"],
                    "word_count": chunk["metadata"].get("word_count", 0),
                    "page_number": chunk["metadata"].get("page_number", 1)
                }
                summary["chunk_preview"].append(preview)
            
            return summary
            
        except Exception as e:
            logger.error(f"Failed to get document chunks summary: {e}")
            return {"error": str(e), "document_id": document_id}
    
    def get_chunks_with_embeddings_for_llm(
        self,
        document_id: Optional[int] = None,
        user_id: Optional[str] = None,
        question_context: str = "generate educational questions",
        max_chunks: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get document chunks with embeddings optimized for LLM question generation
        
        Args:
            document_id: Specific document ID (None for all user documents)
            user_id: User ID for filtering
            question_context: Context for finding relevant chunks
            max_chunks: Maximum number of chunks to return
        
        Returns:
            List of chunks with embeddings and metadata optimized for LLM use
        """
        try:
            # Get chunks from ChromaDB
            if document_id:
                chunks = chromadb_service.get_document_chunks(document_id)
            else:
                # Search for chunks across all documents for this user
                chunks = chromadb_service.search_similar_chunks(
                    query=question_context,
                    n_results=max_chunks * 2,  # Get more to filter later
                    filters={"user_id": user_id} if user_id else None
                )
            
            if not chunks:
                return []
            
            # Find best chunks for question generation using embedding service
            best_chunks = embedding_service.find_best_chunks_for_question_generation(
                chunks=chunks,
                query_context=question_context,
                max_chunks=max_chunks
            )
            
            # Format for LLM consumption
            llm_ready_chunks = []
            for chunk in best_chunks:
                llm_chunk = {
                    "chunk_id": chunk.get("id"),
                    "text": chunk.get("text", ""),
                    "embedding": chunk.get("embedding", []),
                    "embedding_model": chunk.get("embedding_model", "unknown"),
                    "metadata": {
                        "document_id": chunk.get("metadata", {}).get("document_id"),
                        "filename": chunk.get("metadata", {}).get("filename"),
                        "page_number": chunk.get("metadata", {}).get("page_number", 1),
                        "word_count": chunk.get("metadata", {}).get("word_count", 0),
                        "character_count": chunk.get("metadata", {}).get("character_count", 0),
                        "question_generation_score": chunk.get("question_generation_score", 0.5),
                        "similarity_to_context": chunk.get("similarity_to_context", 0.0)
                    },
                    "llm_context": {
                        "suitable_for_questions": True,
                        "complexity_level": self._categorize_complexity(chunk.get("text", "")),
                        "suggested_question_types": self._suggest_question_types(chunk.get("text", "")),
                        "bloom_taxonomy_levels": self._analyze_bloom_levels(chunk.get("text", ""))
                    }
                }
                llm_ready_chunks.append(llm_chunk)
            
            logger.info(f"Prepared {len(llm_ready_chunks)} chunks for LLM question generation")
            return llm_ready_chunks
            
        except Exception as e:
            logger.error(f"Failed to get chunks for LLM: {e}")
            return []
    
    def _categorize_complexity(self, text: str) -> str:
        """Categorize text complexity for question generation"""
        try:
            words = text.split()
            avg_word_length = sum(len(word) for word in words) / len(words) if words else 0
            
            if avg_word_length < 4:
                return "basic"
            elif avg_word_length < 6:
                return "intermediate"
            else:
                return "advanced"
        except:
            return "intermediate"
    
    def _suggest_question_types(self, text: str) -> List[str]:
        """Suggest appropriate question types based on content"""
        try:
            text_lower = text.lower()
            question_types = []
            
            # Check for definitions
            if any(word in text_lower for word in ["definition", "define", "meaning", "is", "are"]):
                question_types.append("definition")
            
            # Check for processes/procedures
            if any(word in text_lower for word in ["process", "step", "procedure", "method", "how"]):
                question_types.append("process")
            
            # Check for examples
            if any(word in text_lower for word in ["example", "instance", "such as", "including"]):
                question_types.append("example")
            
            # Check for comparisons
            if any(word in text_lower for word in ["compare", "contrast", "difference", "similar", "unlike"]):
                question_types.append("comparison")
            
            # Check for analysis content
            if any(word in text_lower for word in ["analysis", "analyze", "examine", "evaluate", "assess"]):
                question_types.append("analysis")
            
            # Default question types
            if not question_types:
                question_types = ["multiple_choice", "short_answer"]
            else:
                question_types.extend(["multiple_choice", "short_answer"])
            
            return list(set(question_types))  # Remove duplicates
            
        except:
            return ["multiple_choice", "short_answer"]
    
    def _analyze_bloom_levels(self, text: str) -> List[str]:
        """Analyze which Bloom's taxonomy levels are appropriate for this content"""
        try:
            text_lower = text.lower()
            bloom_levels = []
            
            # Remember level
            if any(word in text_lower for word in ["define", "list", "name", "identify", "recall"]):
                bloom_levels.append("remember")
            
            # Understand level
            if any(word in text_lower for word in ["explain", "describe", "summarize", "interpret"]):
                bloom_levels.append("understand")
            
            # Apply level
            if any(word in text_lower for word in ["use", "apply", "implement", "execute", "solve"]):
                bloom_levels.append("apply")
            
            # Analyze level
            if any(word in text_lower for word in ["analyze", "examine", "compare", "contrast", "categorize"]):
                bloom_levels.append("analyze")
            
            # Evaluate level
            if any(word in text_lower for word in ["evaluate", "assess", "judge", "critique", "defend"]):
                bloom_levels.append("evaluate")
            
            # Create level
            if any(word in text_lower for word in ["create", "design", "develop", "compose", "generate"]):
                bloom_levels.append("create")
            
            # Default levels if none detected
            if not bloom_levels:
                bloom_levels = ["remember", "understand"]
            
            return bloom_levels
            
        except:
            return ["remember", "understand"]

    def search_document_content(
        self, 
        query: str, 
        document_id: Optional[int] = None,
        user_id: Optional[str] = None,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """Search document content using semantic similarity"""
        try:
            # Prepare filters
            filters = {}
            if user_id:
                filters["user_id"] = user_id
            
            # Search using ChromaDB
            results = chromadb_service.search_similar_chunks(
                query=query,
                n_results=limit,
                document_id=document_id,
                filters=filters
            )
            
            # Format results for API response
            formatted_results = []
            for result in results:
                formatted_result = {
                    "chunk_id": result["id"],
                    "text": result["text"],
                    "similarity_score": 1 - result.get("distance", 0) if result.get("distance") is not None else None,
                    "document_id": result["metadata"].get("document_id"),
                    "filename": result["metadata"].get("filename"),
                    "page_number": result["metadata"].get("page_number"),
                    "word_count": result["metadata"].get("word_count")
                }
                formatted_results.append(formatted_result)
            
            logger.info(f"Found {len(formatted_results)} relevant chunks for query: {query[:50]}...")
            return formatted_results
            
        except Exception as e:
            logger.error(f"Document content search failed: {e}")
            return []

# Global service instance
document_parser = DocumentParsingService() 