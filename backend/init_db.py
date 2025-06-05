#!/usr/bin/env python3
"""
Database initialization script
Creates all tables and runs initial setup
"""

import os
import sys
from sqlalchemy import text

# Add project root to path
sys.path.insert(0, os.path.dirname(__file__))

from config.database import engine, create_tables, SessionLocal
from config.settings import settings

def check_database_connection():
    """Test database connection"""
    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            print("✅ Database connection successful")
            return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

def create_database_tables():
    """Create all database tables"""
    try:
        create_tables()
        print("✅ Database tables created successfully")
        return True
    except Exception as e:
        print(f"❌ Failed to create tables: {e}")
        return False

def verify_tables():
    """Verify that all tables were created"""
    try:
        from sqlalchemy import inspect
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        expected_tables = ["users", "documents", "document_chunks", "questions", "question_feedback"]
        missing_tables = [table for table in expected_tables if table not in tables]
        
        if missing_tables:
            print(f"⚠️  Missing tables: {missing_tables}")
            return False
        else:
            print(f"✅ All tables created: {tables}")
            return True
    except Exception as e:
        print(f"❌ Failed to verify tables: {e}")
        return False

def main():
    print("🏗️  Initializing Question Generator Database")
    print("=" * 50)
    
    # Check database URL
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("❌ DATABASE_URL environment variable not set")
        print("Please set DATABASE_URL in your .env file")
        return False
    
    print(f"📍 Database URL: {database_url}")
    
    # Test connection
    if not check_database_connection():
        print("\n💡 Make sure PostgreSQL is running and DATABASE_URL is correct")
        return False
    
    # Create tables
    if not create_database_tables():
        return False
    
    # Verify tables
    if not verify_tables():
        return False
    
    print("\n🎉 Database initialization completed successfully!")
    print("\n📝 Next steps:")
    print("1. Start the FastAPI server: python main.py")
    print("2. Test authentication endpoints")
    print("3. Begin document upload implementation")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 