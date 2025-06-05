from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Dict, Any, List, Optional
from app.services.chromadb_service import chromadb_service
from auth.clerk_auth import clerk_auth

router = APIRouter(prefix="/chromadb", tags=["ChromaDB"])

@router.get("/health")
async def chromadb_health_check():
    """Check ChromaDB health status"""
    try:
        is_healthy = chromadb_service.health_check()
        return {
            "status": "healthy" if is_healthy else "unhealthy",
            "service": "ChromaDB",
            "message": "ChromaDB is accessible" if is_healthy else "ChromaDB is not accessible"
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"ChromaDB health check failed: {str(e)}")

@router.get("/stats")
async def get_collection_stats(
    current_user: Dict[str, Any] = Depends(clerk_auth.get_current_user)
):
    """Get ChromaDB collection statistics"""
    try:
        stats = chromadb_service.get_collection_stats()
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get collection stats: {str(e)}")

@router.post("/search")
async def search_chunks(
    query: str = Query(..., min_length=1, description="Search query"),
    n_results: int = Query(5, ge=1, le=20, description="Number of results"),
    document_id: Optional[int] = Query(None, description="Filter by document ID"),
    current_user: Dict[str, Any] = Depends(clerk_auth.get_current_user)
):
    """Search for similar document chunks"""
    try:
        results = chromadb_service.search_similar_chunks(
            query=query,
            n_results=n_results,
            document_id=document_id
        )
        
        return {
            "query": query,
            "n_results": len(results),
            "results": results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@router.get("/documents/{document_id}/chunks")
async def get_document_chunks(
    document_id: int,
    current_user: Dict[str, Any] = Depends(clerk_auth.get_current_user)
):
    """Get all chunks for a specific document"""
    try:
        chunks = chromadb_service.get_document_chunks(document_id)
        return {
            "document_id": document_id,
            "chunk_count": len(chunks),
            "chunks": chunks
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get document chunks: {str(e)}")

@router.delete("/documents/{document_id}/chunks")
async def delete_document_chunks(
    document_id: int,
    current_user: Dict[str, Any] = Depends(clerk_auth.get_current_user)
):
    """Delete all chunks for a specific document"""
    try:
        success = chromadb_service.delete_document_chunks(document_id)
        if success:
            return {
                "message": f"Successfully deleted chunks for document {document_id}",
                "document_id": document_id
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to delete document chunks")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete document chunks: {str(e)}")

@router.post("/test-add-chunks")
async def test_add_chunks(
    current_user: Dict[str, Any] = Depends(clerk_auth.get_current_user)
):
    """Add test chunks to ChromaDB for testing purposes"""
    try:
        test_chunks = [
            {
                "text": "This is a test document chunk about artificial intelligence and machine learning.",
                "metadata": {"type": "test", "topic": "AI"},
                "page_number": 1
            },
            {
                "text": "FastAPI is a modern, fast web framework for building APIs with Python.",
                "metadata": {"type": "test", "topic": "Python"},
                "page_number": 1
            },
            {
                "text": "ChromaDB is an open-source vector database designed for AI applications.",
                "metadata": {"type": "test", "topic": "Database"},
                "page_number": 2
            }
        ]
        
        success = chromadb_service.add_document_chunks(
            document_id=999,  # Test document ID
            chunks=test_chunks
        )
        
        if success:
            return {
                "message": "Test chunks added successfully",
                "chunk_count": len(test_chunks),
                "test_document_id": 999
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to add test chunks")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add test chunks: {str(e)}")

@router.delete("/reset-collection")
async def reset_collection(
    confirm: bool = Query(False, description="Confirm collection reset"),
    current_user: Dict[str, Any] = Depends(clerk_auth.get_current_user)
):
    """Reset the entire ChromaDB collection - USE WITH CAUTION"""
    if not confirm:
        raise HTTPException(
            status_code=400, 
            detail="Collection reset requires confirmation. Set confirm=true to proceed."
        )
    
    try:
        success = chromadb_service.reset_collection()
        if success:
            return {
                "message": "ChromaDB collection reset successfully",
                "warning": "All document chunks have been deleted"
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to reset collection")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to reset collection: {str(e)}") 