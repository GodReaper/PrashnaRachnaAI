from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from config.settings import settings
from app.routes.auth_routes import router as auth_router
from app.routes.document_routes import router as document_router
from app.routes.chromadb_routes import router as chromadb_router

app = FastAPI(
    title="Question Generator API",
    description="Backend API for the Question Generation Platform with Clerk Authentication",
    version="1.0.0"
)

# Configure CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include authentication routes
app.include_router(auth_router)
# Include document routes
app.include_router(document_router)
# Include ChromaDB routes
app.include_router(chromadb_router)

@app.get("/")
async def read_root():
    """Basic Hello World endpoint to verify API is running"""
    return {"message": "Hello World", "status": "API is running successfully"}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "Question Generator API"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000) 