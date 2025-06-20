import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Settings:
    # Clerk Configuration
    CLERK_PUBLISHABLE_KEY: str = os.getenv("CLERK_PUBLISHABLE_KEY", "")
    CLERK_SECRET_KEY: str = os.getenv("CLERK_SECRET_KEY", "")
    CLERK_JWT_KEY: str = os.getenv("CLERK_JWT_KEY", "")
    
    # Database Configuration
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://postgres:password@localhost:5432/question_generator")
    
    # ChromaDB Configuration
    CHROMADB_HOST: str = os.getenv("CHROMADB_HOST", "localhost")
    CHROMADB_PORT: int = int(os.getenv("CHROMADB_PORT", "8001"))
    CHROMADB_URL: str = os.getenv("CHROMADB_URL", f"http://{os.getenv('CHROMADB_HOST', 'localhost')}:{os.getenv('CHROMADB_PORT', '8001')}")
    CHROMADB_COLLECTION_NAME: str = os.getenv("CHROMADB_COLLECTION_NAME", "document_chunks")
    CHROMADB_DISTANCE_FUNCTION: str = os.getenv("CHROMADB_DISTANCE_FUNCTION", "cosine")
    
    # API Configuration
    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
    API_PORT: int = int(os.getenv("API_PORT", "8000"))
    DEBUG: bool = os.getenv("DEBUG", "True").lower() == "true"
    
    # CORS Configuration
    CORS_ORIGINS: list = ["http://localhost:3000"]  # Frontend URL
    
    # Ollama Configuration
    OLLAMA_HOST: str = os.getenv("OLLAMA_HOST", "localhost")
    OLLAMA_PORT: int = int(os.getenv("OLLAMA_PORT", "11434"))
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", f"http://{os.getenv('OLLAMA_HOST', 'localhost')}:{os.getenv('OLLAMA_PORT', '11434')}")
    
    # Default models (user can override)
    OLLAMA_DEFAULT_MODEL: str = os.getenv("OLLAMA_DEFAULT_MODEL", "deepseek-r1:1.5b")
    OLLAMA_FALLBACK_MODEL: str = os.getenv("OLLAMA_FALLBACK_MODEL", "llama3.2:3b")

# Global settings instance
settings = Settings() 