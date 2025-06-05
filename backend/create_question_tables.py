"""
Database migration script to create question tables
"""

import logging
from sqlalchemy import create_engine, text
from config.settings import settings
from config.database import Base
from app.models.question import Question, QuestionFeedback, QuestionSet, question_set_questions

logger = logging.getLogger(__name__)

def create_question_tables():
    """Create question-related tables in the database"""
    try:
        # Create engine
        engine = create_engine(settings.DATABASE_URL)
        
        # Create tables
        logger.info("Creating question tables...")
        
        # Import all models to ensure they're registered
        from app.models import user, document, question
        
        # Create all tables
        Base.metadata.create_all(bind=engine)
        
        logger.info("✅ Question tables created successfully!")
        
        # List created tables
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name IN ('questions', 'question_feedback', 'question_sets', 'question_set_questions')
                ORDER BY table_name;
            """))
            
            tables = [row[0] for row in result]
            logger.info(f"📋 Created tables: {tables}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to create question tables: {e}")
        return False

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    success = create_question_tables()
    
    if success:
        print("✅ Question tables migration completed successfully!")
    else:
        print("❌ Question tables migration failed!")
        exit(1) 