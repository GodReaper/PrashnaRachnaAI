#!/usr/bin/env python3
"""
Setup verification script for Question Generator Backend
Checks all dependencies, configurations, and database connectivity
"""

import os
import sys
import importlib
from typing import List, Tuple

def check_python_version() -> bool:
    """Check if Python version is compatible"""
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print(f"❌ Python {version.major}.{version.minor}.{version.micro} - Requires Python 3.8+")
        return False

def check_dependencies() -> bool:
    """Check if all required dependencies are installed"""
    required_packages = [
        "fastapi",
        "uvicorn",
        "pydantic",
        "python_multipart",
        "python_dotenv",
        "sqlalchemy",
        "alembic",
        "psycopg2",
        "pyjwt",
        "cryptography",
        "requests"
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            importlib.import_module(package)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} - Not installed")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n📦 Missing packages: {', '.join(missing_packages)}")
        print("Install with: pip install -r requirements.txt")
        return False
    
    return True

def check_environment_variables() -> bool:
    """Check if required environment variables are set"""
    from dotenv import load_dotenv
    load_dotenv()
    
    required_vars = [
        ("DATABASE_URL", "PostgreSQL connection string"),
        ("CLERK_PUBLISHABLE_KEY", "Clerk publishable key"),
        ("CLERK_SECRET_KEY", "Clerk secret key"),
    ]
    
    missing_vars = []
    for var_name, description in required_vars:
        value = os.getenv(var_name)
        if value:
            # Mask sensitive values
            if "SECRET" in var_name or "PASSWORD" in var_name:
                masked_value = value[:8] + "..." if len(value) > 8 else "***"
                print(f"✅ {var_name}: {masked_value}")
            else:
                print(f"✅ {var_name}: {value}")
        else:
            print(f"❌ {var_name}: Not set - {description}")
            missing_vars.append(var_name)
    
    if missing_vars:
        print(f"\n⚠️  Missing environment variables: {', '.join(missing_vars)}")
        print("Copy env.example to .env and update with your values")
        return False
    
    return True

def check_database_connection() -> bool:
    """Test database connection"""
    try:
        from config.database import engine
        from sqlalchemy import text
        
        with engine.connect() as connection:
            result = connection.execute(text("SELECT version()"))
            version = result.fetchone()[0]
            print(f"✅ Database connection: {version}")
            return True
    except Exception as e:
        print(f"❌ Database connection failed: {str(e)}")
        print("Make sure PostgreSQL is running and DATABASE_URL is correct")
        return False

def check_database_tables() -> bool:
    """Check if database tables exist"""
    try:
        from sqlalchemy import inspect
        from config.database import engine
        
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        expected_tables = ["users", "documents", "document_chunks", "questions", "question_feedback"]
        existing_tables = [table for table in expected_tables if table in tables]
        missing_tables = [table for table in expected_tables if table not in tables]
        
        if existing_tables:
            print(f"✅ Existing tables: {', '.join(existing_tables)}")
        
        if missing_tables:
            print(f"⚠️  Missing tables: {', '.join(missing_tables)}")
            print("Run: python init_db.py to create tables")
            return False
        
        return True
    except Exception as e:
        print(f"❌ Failed to check tables: {str(e)}")
        return False

def main():
    print("🔍 Question Generator Backend Setup Check")
    print("=" * 50)
    
    checks = [
        ("Python Version", check_python_version),
        ("Dependencies", check_dependencies),
        ("Environment Variables", check_environment_variables),
        ("Database Connection", check_database_connection),
        ("Database Tables", check_database_tables),
    ]
    
    all_passed = True
    
    for check_name, check_func in checks:
        print(f"\n📋 Checking {check_name}...")
        try:
            passed = check_func()
            all_passed = all_passed and passed
        except Exception as e:
            print(f"❌ {check_name} check failed: {str(e)}")
            all_passed = False
    
    print("\n" + "=" * 50)
    
    if all_passed:
        print("🎉 All checks passed! Your setup is ready.")
        print("\n📝 Next steps:")
        print("1. Start the server: python main.py")
        print("2. Test endpoints: python test_auth.py")
        print("3. View API docs: http://localhost:8000/docs")
    else:
        print("⚠️  Some checks failed. Please fix the issues above.")
        print("\n🛠️  Common solutions:")
        print("- Install dependencies: pip install -r requirements.txt")
        print("- Set environment variables: cp env.example .env")
        print("- Initialize database: python init_db.py")
        print("- Start PostgreSQL service")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 