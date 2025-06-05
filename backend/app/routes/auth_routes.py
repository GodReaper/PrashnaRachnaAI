from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any
from auth.clerk_auth import clerk_auth
from config.database import get_db
from app.services.user_service import UserService

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.get("/profile")
async def get_user_profile(
    current_user: Dict[str, Any] = Depends(clerk_auth.get_current_user),
    db: Session = Depends(get_db)
):
    """Protected route that requires authentication and returns user profile from database"""
    clerk_user_id = current_user.get("user_id")
    
    # Get or create user in database
    user_data = {
        "clerk_user_id": clerk_user_id,
        "email": current_user.get("email", ""),
        "first_name": current_user.get("first_name"),
        "last_name": current_user.get("last_name"),
        "profile_image_url": current_user.get("profile_image_url")
    }
    
    try:
        user = UserService.get_or_create_user(db, user_data)
        return {
            "message": "Access granted to protected route",
            "user_id": user.id,
            "clerk_user_id": user.clerk_user_id,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "profile_image_url": user.profile_image_url,
            "is_active": user.is_active,
            "created_at": user.created_at,
            "authenticated": True
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@router.get("/verify")
async def verify_auth(current_user: Dict[str, Any] = Depends(clerk_auth.get_current_user)):
    """Simple endpoint to verify if user is authenticated"""
    return {
        "authenticated": True,
        "user_id": current_user.get("user_id"),
        "timestamp": current_user.get("iat")
    }

@router.get("/public")
async def public_endpoint():
    """Public endpoint that doesn't require authentication"""
    return {
        "message": "This is a public endpoint",
        "authenticated": False,
        "accessible_to": "everyone"
    } 