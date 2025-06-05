-- Question Generator Database Initialization Script
-- This script runs automatically when the PostgreSQL container starts for the first time

-- Create the main database (already created by POSTGRES_DB env var)
-- CREATE DATABASE question_generator;

-- Connect to the database
\c question_generator;

-- Create extensions that might be useful
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Grant permissions
GRANT ALL PRIVILEGES ON DATABASE question_generator TO postgres;

-- Display confirmation
SELECT 'Question Generator Database initialized successfully!' as status; 