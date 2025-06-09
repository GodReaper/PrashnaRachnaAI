"""
Question generation and management API routes
"""

import logging
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, Body
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from config.database import get_db
from auth.clerk_auth import clerk_auth
from app.services.question_generation_service import question_generation_service
from app.services.ollama_service import ollama_service
from app.services.document_service import DocumentService
from app.services.document_parser import document_parser
from app.services.user_service import UserService
from app.models.question import Question, QuestionFeedback, QuestionSet
from app.models.document import Document

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/questions", tags=["Questions"])

# Pydantic schemas
class QuestionGenerationRequest(BaseModel):
    """Request schema for question generation"""
    document_ids: List[str] = Field(..., description="List of document IDs to generate questions from")
    question_type: str = Field(default="all_types", description="Type of questions to generate")
    bloom_level: str = Field(default="understand", description="Bloom's taxonomy level")
    difficulty: str = Field(default="intermediate", description="Difficulty level")
    num_questions: int = Field(default=7, ge=1, le=20, description="Number of questions to generate")
    model: Optional[str] = Field(default="deepseek-r1:1.5b", description="Specific Ollama model to use")

class QuestionFeedbackRequest(BaseModel):
    """Request schema for question feedback"""
    vote: Optional[str] = Field(None, description="Vote: up, down, or neutral")
    difficulty_rating: Optional[int] = Field(None, ge=1, le=5, description="Difficulty rating 1-5")
    quality_rating: Optional[int] = Field(None, ge=1, le=5, description="Quality rating 1-5")
    comments: Optional[str] = Field(None, description="Optional comments")
    is_helpful: Optional[bool] = Field(None, description="Is this question helpful?")
    is_accurate: Optional[bool] = Field(None, description="Is this question accurate?")

class QuestionSetRequest(BaseModel):
    """Request schema for creating question sets"""
    name: str = Field(..., description="Name of the question set")
    description: Optional[str] = Field(None, description="Description of the question set")
    question_ids: List[str] = Field(..., description="List of question IDs to include")
    tags: Optional[List[str]] = Field(None, description="Tags for the question set")

@router.post("/generate")
async def generate_questions(
    request: QuestionGenerationRequest,
    current_user = Depends(clerk_auth.get_current_user_db),
    db: Session = Depends(get_db)
):
    """
    Generate questions from documents using Ollama LLMs
    
    Supports multiple question types, Bloom's taxonomy levels, and difficulty levels.
    Uses DeepSeek R1, Llama, or other configured models.
    """
    try:
        user = current_user  # Now we get the User object directly
        
        # Validate document access
        documents = []
        for doc_id in request.document_ids:
            try:
                # Try to convert to int, handle conversion errors
                doc_id_int = int(doc_id)
                doc = DocumentService.get_document_by_id(db, doc_id_int, user.id)
                if not doc:
                    raise HTTPException(status_code=404, detail=f"Document {doc_id} not found or access denied")
                documents.append(doc)
            except ValueError:
                raise HTTPException(status_code=400, detail=f"Invalid document ID format: {doc_id}")
            except Exception as e:
                logger.error(f"Error accessing document {doc_id}: {e}")
                raise HTTPException(status_code=500, detail=f"Error accessing document {doc_id}")
        
        # Get LLM-ready chunks from documents
        all_chunks = []
        for document in documents:
            chunks = document_parser.get_chunks_with_embeddings_for_llm(
                document_id=document.id,
                user_id=user.clerk_user_id,
                question_context="generate educational questions",
                max_chunks=10
            )
            if chunks:
                all_chunks.extend(chunks)
        
        if not all_chunks:
            raise HTTPException(status_code=400, detail="No processable content found in documents")
        
        # Limit chunks for processing
        max_chunks = 10  # Reasonable limit for question generation
        if len(all_chunks) > max_chunks:
            # Sort by relevance score if available
            all_chunks.sort(key=lambda x: x.get("llm_analysis", {}).get("relevance_score", 0), reverse=True)
            all_chunks = all_chunks[:max_chunks]
        
        # Generate questions
        result = question_generation_service.generate_questions(
            content_chunks=all_chunks,
            question_type=request.question_type,
            bloom_level=request.bloom_level,
            difficulty=request.difficulty,
            num_questions=request.num_questions,
            model=request.model,
            user_id=user.clerk_user_id
        )
        
        if not result["success"]:
            raise HTTPException(status_code=500, detail=f"Question generation failed: {result['error']}")
        
        # Store questions in database
        stored_questions = []
        for question_data in result["questions"]:
            try:
                # Create question record
                db_question = Question(
                    user_id=user.id,
                    question_text=question_data.get("question", ""),
                    question_type=question_data.get("type", request.question_type),
                    correct_answer=question_data.get("correct_answer") or question_data.get("correct_answers"),
                    options=question_data.get("options"),
                    explanation=question_data.get("explanation"),
                    bloom_level=question_data.get("bloom_level", request.bloom_level),
                    difficulty=question_data.get("difficulty", request.difficulty),
                    topic=question_data.get("topic"),
                    document_id=documents[0].id if documents else None,  # Primary document
                    source_content=question_data.get("source_content"),
                    model_used=result["metadata"].get("model"),
                    generation_time=result["metadata"].get("generation_time"),
                    raw_llm_response=result.get("raw_response", "")
                )
                
                db.add(db_question)
                db.flush()  # Get the ID
                
                stored_questions.append({
                    "id": db_question.id,
                    "question": question_data.get("question"),
                    "type": question_data.get("type"),
                    "correct_answer": question_data.get("correct_answer") or question_data.get("correct_answers"),
                    "options": question_data.get("options"),
                    "explanation": question_data.get("explanation"),
                    "bloom_level": question_data.get("bloom_level"),
                    "difficulty": question_data.get("difficulty"),
                    "topic": question_data.get("topic"),
                    "created_at": db_question.created_at.isoformat()
                })
                
            except Exception as e:
                logger.error(f"Failed to store question: {e}")
                continue
        
        db.commit()
        
        return {
            "success": True,
            "questions": stored_questions,
            "metadata": {
                **result["metadata"],
                "questions_stored": len(stored_questions),
                "documents_used": [{"id": doc.id, "filename": doc.filename} for doc in documents]
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Question generation endpoint error: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/")
async def get_user_questions(
    current_user = Depends(clerk_auth.get_current_user_db),
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0, description="Number of questions to skip"),
    limit: int = Query(50, ge=1, le=100, description="Number of questions to return"),
    question_type: Optional[str] = Query(None, description="Filter by question type"),
    bloom_level: Optional[str] = Query(None, description="Filter by Bloom's level"),
    difficulty: Optional[str] = Query(None, description="Filter by difficulty")
):
    """Get user's generated questions with pagination and filtering"""
    try:
        user = current_user
        
        # Build query
        query = db.query(Question).filter(Question.user_id == user.id)
        
        # Apply filters
        if question_type:
            query = query.filter(Question.question_type == question_type)
        if bloom_level:
            query = query.filter(Question.bloom_level == bloom_level)
        if difficulty:
            query = query.filter(Question.difficulty == difficulty)
        
        # Get total count
        total = query.count()
        
        # Apply pagination and get results
        questions = query.order_by(Question.created_at.desc()).offset(skip).limit(limit).all()
        
        # Format response
        questions_data = []
        for question in questions:
            questions_data.append({
                "id": question.id,
                "question": question.question_text,
                "type": question.question_type,
                "correct_answer": question.correct_answer,
                "options": question.options,
                "explanation": question.explanation,
                "bloom_level": question.bloom_level,
                "difficulty": question.difficulty,
                "topic": question.topic,
                "upvotes": question.upvotes,
                "downvotes": question.downvotes,
                "difficulty_rating": question.difficulty_rating,
                "quality_score": question.quality_score,
                "created_at": question.created_at.isoformat(),
                "document_id": question.document_id if question.document_id else None
            })
        
        return {
            "success": True,
            "questions": questions_data,
            "pagination": {
                "total": total,
                "skip": skip,
                "limit": limit,
                "has_more": skip + limit < total
            }
        }
        
    except Exception as e:
        logger.error(f"Get questions error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{question_id}")
async def get_question(
    question_id: str,
    current_user = Depends(clerk_auth.get_current_user_db),
    db: Session = Depends(get_db)
):
    """Get a specific question by ID"""
    try:
        user = current_user
        
        question = db.query(Question).filter(
            Question.id == question_id,
            Question.user_id == user.id
        ).first()
        
        if not question:
            raise HTTPException(status_code=404, detail="Question not found")
        
        return {
            "success": True,
            "question": {
                "id": question.id,
                "question": question.question_text,
                "type": question.question_type,
                "correct_answer": question.correct_answer,
                "options": question.options,
                "explanation": question.explanation,
                "bloom_level": question.bloom_level,
                "difficulty": question.difficulty,
                "topic": question.topic,
                "upvotes": question.upvotes,
                "downvotes": question.downvotes,
                "difficulty_rating": question.difficulty_rating,
                "quality_score": question.quality_score,
                "model_used": question.model_used,
                "generation_time": question.generation_time,
                "source_content": question.source_content,
                "created_at": question.created_at.isoformat(),
                "document_id": question.document_id if question.document_id else None
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get question error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{question_id}/feedback")
async def submit_feedback(
    question_id: str,
    feedback: QuestionFeedbackRequest,
    current_user = Depends(clerk_auth.get_current_user_db),
    db: Session = Depends(get_db)
):
    """Submit feedback for a question"""
    try:
        user = current_user
        
        # Verify question exists and user has access
        question = db.query(Question).filter(
            Question.id == question_id,
            Question.user_id == user.id
        ).first()
        
        if not question:
            raise HTTPException(status_code=404, detail="Question not found")
        
        # Check if user already gave feedback
        existing_feedback = db.query(QuestionFeedback).filter(
            QuestionFeedback.question_id == question_id,
            QuestionFeedback.user_id == user.id
        ).first()
        
        if existing_feedback:
            # Update existing feedback
            if feedback.vote:
                existing_feedback.vote = feedback.vote
            if feedback.difficulty_rating:
                existing_feedback.difficulty_rating = feedback.difficulty_rating
            if feedback.quality_rating:
                existing_feedback.quality_rating = feedback.quality_rating
            if feedback.comments:
                existing_feedback.comments = feedback.comments
            if feedback.is_helpful is not None:
                existing_feedback.is_helpful = feedback.is_helpful
            if feedback.is_accurate is not None:
                existing_feedback.is_accurate = feedback.is_accurate
        else:
            # Create new feedback
            existing_feedback = QuestionFeedback(
                question_id=question_id,
                user_id=user.id,
                vote=feedback.vote,
                difficulty_rating=feedback.difficulty_rating,
                quality_rating=feedback.quality_rating,
                comments=feedback.comments,
                is_helpful=feedback.is_helpful,
                is_accurate=feedback.is_accurate
            )
            db.add(existing_feedback)
        
        # Update question aggregated data
        if feedback.vote == "up":
            question.upvotes += 1
        elif feedback.vote == "down":
            question.downvotes += 1
        
        if feedback.difficulty_rating:
            # Update average difficulty rating (simplified)
            question.difficulty_rating = feedback.difficulty_rating
        
        db.commit()
        
        return {
            "success": True,
            "message": "Feedback submitted successfully",
            "question_stats": {
                "upvotes": question.upvotes,
                "downvotes": question.downvotes,
                "difficulty_rating": question.difficulty_rating
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Submit feedback error: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{question_id}")
async def delete_question(
    question_id: str,
    current_user = Depends(clerk_auth.get_current_user_db),
    db: Session = Depends(get_db)
):
    """Delete a question"""
    try:
        user = current_user
        
        question = db.query(Question).filter(
            Question.id == question_id,
            Question.user_id == user.id
        ).first()
        
        if not question:
            raise HTTPException(status_code=404, detail="Question not found")
        
        db.delete(question)
        db.commit()
        
        return {
            "success": True,
            "message": "Question deleted successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Delete question error: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/types/supported")
async def get_supported_types():
    """Get supported question types and Bloom's levels"""
    question_types = question_generation_service.get_question_types()
    question_types.append("all_types")  # Add the option to generate all types
    
    return {
        "success": True,
        "question_types": question_types,
        "bloom_levels": question_generation_service.get_bloom_levels(),
        "difficulty_levels": ["basic", "intermediate", "advanced"]
    }

@router.get("/ollama/status")
async def get_ollama_status():
    """Get Ollama service status and available models"""
    try:
        health = ollama_service.health_check()
        models = ollama_service.get_recommended_models()
        
        return {
            "success": True,
            "ollama_healthy": health,
            "models": models,
            "service_url": ollama_service.base_url
        }
        
    except Exception as e:
        logger.error(f"Ollama status error: {e}")
        return {
            "success": False,
            "error": str(e),
            "ollama_healthy": False
        }

@router.post("/ollama/pull-model")
async def pull_ollama_model(
    model_name: str = Body(..., embed=True),
    current_user = Depends(clerk_auth.get_current_user_db)
):
    """Pull a specific Ollama model"""
    try:
        result = ollama_service.pull_model(model_name)
        
        if result:
            return {
                "success": True,
                "message": f"Model {model_name} pulled successfully",
                "model": model_name
            }
        else:
            return {
                "success": False,
                "error": f"Failed to pull model {model_name}"
            }
            
    except Exception as e:
        logger.error(f"Pull model error: {e}")
        raise HTTPException(status_code=500, detail=str(e)) 