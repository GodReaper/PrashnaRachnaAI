"""
Question models for database storage
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Float, JSON, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from config.database import Base

class Question(Base):
    """Generated questions storage"""
    __tablename__ = "questions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)  # Reference to users table
    
    # Question content
    question_text = Column(Text, nullable=False)
    question_type = Column(String, nullable=False)  # multiple_choice, true_false, etc.
    
    # Answer data (JSON for flexibility)
    correct_answer = Column(JSON)  # Stores answers in appropriate format
    options = Column(JSON)  # For multiple choice options
    explanation = Column(Text)
    
    # Educational metadata
    bloom_level = Column(String)  # remember, understand, apply, etc.
    difficulty = Column(String)  # basic, intermediate, advanced
    topic = Column(String)
    
    # Source information
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=True)
    source_content = Column(JSON)  # Information about source chunks
    
    # Generation metadata
    model_used = Column(String)  # Which LLM model generated this
    generation_time = Column(Float)  # Time taken to generate
    raw_llm_response = Column(Text)  # Original LLM response
    
    # Feedback and analytics
    upvotes = Column(Integer, default=0)
    downvotes = Column(Integer, default=0)
    difficulty_rating = Column(Float)  # User-rated difficulty
    quality_score = Column(Float)  # Computed quality score
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="questions")
    document = relationship("Document", back_populates="questions")
    feedbacks = relationship("QuestionFeedback", back_populates="question", cascade="all, delete-orphan")

class QuestionFeedback(Base):
    """User feedback on questions"""
    __tablename__ = "question_feedback"
    
    id = Column(Integer, primary_key=True, index=True)
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)  # Reference to users table
    
    # Feedback types
    vote = Column(String)  # 'up', 'down', 'neutral'
    difficulty_rating = Column(Integer)  # 1-5 scale
    quality_rating = Column(Integer)  # 1-5 scale
    
    # Optional feedback
    comments = Column(Text)
    is_helpful = Column(Boolean)
    is_accurate = Column(Boolean)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="question_feedbacks")
    question = relationship("Question", back_populates="feedbacks")

class QuestionSet(Base):
    """Collection of questions for organized study"""
    __tablename__ = "question_sets"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)  # Reference to users table
    
    # Set metadata
    name = Column(String, nullable=False)
    description = Column(Text)
    tags = Column(JSON)  # List of tags
    
    # Generation parameters
    source_documents = Column(JSON)  # List of document IDs used
    question_types = Column(JSON)  # Types of questions in set
    bloom_levels = Column(JSON)  # Bloom levels covered
    difficulty_mix = Column(JSON)  # Difficulty distribution
    
    # Analytics
    total_questions = Column(Integer, default=0)
    avg_difficulty = Column(Float)
    completion_rate = Column(Float)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="question_sets")
    questions = relationship("Question", secondary="question_set_questions")

# Association table for many-to-many relationship
from sqlalchemy import Table
question_set_questions = Table(
    'question_set_questions',
    Base.metadata,
    Column('question_set_id', Integer, ForeignKey('question_sets.id'), primary_key=True),
    Column('question_id', Integer, ForeignKey('questions.id'), primary_key=True)
)