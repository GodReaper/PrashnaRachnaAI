import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Settings:
    # Clerk Configuration
    CLERK_PUBLISHABLE_KEY: str = os.getenv("CLERK_PUBLISHABLE_KEY", "")
    CLERK_SECRET_KEY: str = os.getenv("CLERK_SECRET_KEY", "")
    CLERK_JWT_KEY: str = os.getenv("CLERK_JWT_KEY", "")
    
    # API Configuration
    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
    API_PORT: int = int(os.getenv("API_PORT", "8000"))
    DEBUG: bool = os.getenv("DEBUG", "True").lower() == "true"
    
    # CORS Configuration
    CORS_ORIGINS: list = ["http://localhost:3000"]  # Frontend URL

# Global settings instance
settings = Settings() 