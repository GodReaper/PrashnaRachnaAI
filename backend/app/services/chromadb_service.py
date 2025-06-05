"""
ChromaDB Service for Vector Database Operations
Handles document chunk storage and retrieval for semantic search
"""

import uuid
from typing import List, Dict, Any, Optional, Tuple
import chromadb
from chromadb.utils import embedding_functions
from config.settings import settings
import logging

logger = logging.getLogger(__name__)

class ChromaDBService:
    """Service for managing ChromaDB vector database operations"""
    
    def __init__(self):
        self.client = None
        self.collection = None
        self.embedding_function = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize ChromaDB client and collection"""
        try:
            # Create ChromaDB client (no auth for development)
            # Note: Some ChromaDB setups require specific configuration
            try:
                self.client = chromadb.HttpClient(
                    host=settings.CHROMADB_HOST,
                    port=settings.CHROMADB_PORT
                )
            except ValueError as ve:
                if "host provided in settings" in str(ve):
                    # Fallback: Try connecting with 0.0.0.0 if localhost fails
                    logger.warning(f"Host mismatch error, trying 0.0.0.0: {ve}")
                    self.client = chromadb.HttpClient(
                        host="0.0.0.0",
                        port=settings.CHROMADB_PORT
                    )
                else:
                    raise ve
            
            # Use default embedding function (can be customized later)
            self.embedding_function = embedding_functions.DefaultEmbeddingFunction()
            
            # Get or create collection
            self.collection = self.client.get_or_create_collection(
                name=settings.CHROMADB_COLLECTION_NAME,
                embedding_function=self.embedding_function,
                metadata={"description": "Document chunks for semantic search"}
            )
            
            logger.info(f"ChromaDB initialized successfully. Collection: {settings.CHROMADB_COLLECTION_NAME}")
            
        except Exception as e:
            logger.error(f"Failed to initialize ChromaDB: {e}")
            raise ConnectionError(f"ChromaDB connection failed: {e}")
    
    def health_check(self) -> bool:
        """Check if ChromaDB is healthy and accessible"""
        try:
            # Try to get version/heartbeat
            self.client.heartbeat()
            return True
        except Exception as e:
            logger.error(f"ChromaDB health check failed: {e}")
            # Try alternative method
            try:
                # Just try to list collections as a health check
                self.client.list_collections()
                return True
            except Exception as e2:
                logger.error(f"ChromaDB alternative health check failed: {e2}")
                return False
    
    def add_document_chunks(
        self, 
        document_id: int, 
        chunks: List[Dict[str, Any]]
    ) -> bool:
        """
        Add document chunks to ChromaDB
        
        Args:
            document_id: Database document ID
            chunks: List of chunk dictionaries with 'text', 'metadata', etc.
        
        Returns:
            bool: Success status
        """
        try:
            if not chunks:
                logger.warning(f"No chunks provided for document {document_id}")
                return True
            
            # Prepare data for ChromaDB
            ids = []
            documents = []
            metadatas = []
            
            for i, chunk in enumerate(chunks):
                # Generate unique ID for chunk
                chunk_id = f"doc_{document_id}_chunk_{i}_{str(uuid.uuid4())[:8]}"
                ids.append(chunk_id)
                
                # Extract text content
                documents.append(chunk.get('text', ''))
                
                # Prepare metadata
                metadata = {
                    'document_id': document_id,
                    'chunk_index': i,
                    'chunk_type': chunk.get('type', 'text'),
                    'page_number': chunk.get('page_number', 0),
                    'word_count': len(chunk.get('text', '').split()),
                    **chunk.get('metadata', {})
                }
                metadatas.append(metadata)
            
            # Add to ChromaDB collection
            self.collection.add(
                ids=ids,
                documents=documents,
                metadatas=metadatas
            )
            
            logger.info(f"Added {len(chunks)} chunks for document {document_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add chunks for document {document_id}: {e}")
            return False
    
    def search_similar_chunks(
        self, 
        query: str, 
        n_results: int = 5,
        document_id: Optional[int] = None,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for similar document chunks
        
        Args:
            query: Search query text
            n_results: Number of results to return
            document_id: Filter by specific document ID
            filters: Additional metadata filters
        
        Returns:
            List of similar chunks with metadata
        """
        try:
            # Prepare where clause for filtering
            where_clause = {}
            
            if document_id:
                where_clause['document_id'] = document_id
            
            if filters:
                where_clause.update(filters)
            
            # Perform similarity search
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results,
                where=where_clause if where_clause else None
            )
            
            # Format results
            formatted_results = []
            if results['documents'] and results['documents'][0]:
                for i in range(len(results['documents'][0])):
                    result = {
                        'id': results['ids'][0][i],
                        'text': results['documents'][0][i],
                        'metadata': results['metadatas'][0][i],
                        'distance': results['distances'][0][i] if 'distances' in results else None
                    }
                    formatted_results.append(result)
            
            logger.info(f"Found {len(formatted_results)} similar chunks for query: {query[:50]}...")
            return formatted_results
            
        except Exception as e:
            logger.error(f"Failed to search similar chunks: {e}")
            return []
    
    def get_document_chunks(self, document_id: int) -> List[Dict[str, Any]]:
        """Get all chunks for a specific document"""
        try:
            results = self.collection.get(
                where={"document_id": document_id}
            )
            
            formatted_results = []
            if results['documents']:
                for i in range(len(results['documents'])):
                    result = {
                        'id': results['ids'][i],
                        'text': results['documents'][i],
                        'metadata': results['metadatas'][i]
                    }
                    formatted_results.append(result)
            
            logger.info(f"Retrieved {len(formatted_results)} chunks for document {document_id}")
            return formatted_results
            
        except Exception as e:
            logger.error(f"Failed to get chunks for document {document_id}: {e}")
            return []
    
    def delete_document_chunks(self, document_id: int) -> bool:
        """Delete all chunks for a specific document"""
        try:
            # Get all chunk IDs for the document
            results = self.collection.get(
                where={"document_id": document_id}
            )
            
            if results['ids']:
                # Delete chunks
                self.collection.delete(ids=results['ids'])
                logger.info(f"Deleted {len(results['ids'])} chunks for document {document_id}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete chunks for document {document_id}: {e}")
            return False
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics about the ChromaDB collection"""
        try:
            count = self.collection.count()
            return {
                "total_chunks": count,
                "collection_name": settings.CHROMADB_COLLECTION_NAME,
                "embedding_function": str(self.embedding_function),
                "distance_function": settings.CHROMADB_DISTANCE_FUNCTION
            }
        except Exception as e:
            logger.error(f"Failed to get collection stats: {e}")
            return {"error": str(e)}
    
    def reset_collection(self) -> bool:
        """Reset (clear) the entire collection - USE WITH CAUTION"""
        try:
            self.client.delete_collection(settings.CHROMADB_COLLECTION_NAME)
            self.collection = self.client.create_collection(
                name=settings.CHROMADB_COLLECTION_NAME,
                embedding_function=self.embedding_function,
                metadata={"description": "Document chunks for semantic search"}
            )
            logger.warning("ChromaDB collection has been reset")
            return True
        except Exception as e:
            logger.error(f"Failed to reset collection: {e}")
            return False

# Global ChromaDB service instance
chromadb_service = ChromaDBService() 