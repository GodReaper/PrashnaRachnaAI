from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey, JSON, Float
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from config.database import Base

class Question(Base):
    __tablename__ = "questions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False)
    
    # Question content
    question_text = Column(Text, nullable=False)
    question_type = Column(String, nullable=False)  # MCQ, FillInTheBlank, TrueFalse, ShortAnswer
    bloom_level = Column(String, nullable=False)  # Remember, Understand, Apply, Analyze, Evaluate, Create
    
    # Answer data (JSON format for flexibility)
    correct_answer = Column(JSON, nullable=False)  # Correct answer(s)
    options = Column(JSON, nullable=True)  # For MCQ: list of options
    explanation = Column(Text, nullable=True)  # Explanation of correct answer
    
    # Difficulty and feedback
    difficulty_level = Column(String, default="medium")  # easy, medium, hard
    estimated_time_minutes = Column(Integer, default=5)  # Estimated time to answer
    
    # User feedback
    upvotes = Column(Integer, default=0)
    downvotes = Column(Integer, default=0)
    user_rating = Column(Float, nullable=True)  # 1.0 to 5.0
    feedback_comments = Column(Text, nullable=True)
    
    # Generation metadata
    generation_prompt = Column(Text, nullable=True)  # Prompt used to generate question
    ai_model_used = Column(String, nullable=True)  # Which AI model was used
    generation_time_ms = Column(Integer, nullable=True)  # Time taken to generate
    
    # Status
    is_active = Column(Boolean, default=True)
    is_reviewed = Column(Boolean, default=False)
    review_status = Column(String, default="pending")  # pending, approved, rejected
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="questions")
    document = relationship("Document", back_populates="questions")
    feedback_entries = relationship("QuestionFeedback", back_populates="question", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Question(id={self.id}, type='{self.question_type}', bloom='{self.bloom_level}')>"

class QuestionFeedback(Base):
    __tablename__ = "question_feedback"
    
    id = Column(Integer, primary_key=True, index=True)
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Feedback data
    feedback_type = Column(String, nullable=False)  # upvote, downvote, rating, difficulty
    feedback_value = Column(String, nullable=True)  # For difficulty: too_easy, just_right, too_hard
    rating_score = Column(Float, nullable=True)  # 1.0 to 5.0
    comments = Column(Text, nullable=True)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    question = relationship("Question", back_populates="feedback_entries")
    user = relationship("User")
    
    def __repr__(self):
        return f"<QuestionFeedback(id={self.id}, type='{self.feedback_type}', question_id={self.question_id})>" 