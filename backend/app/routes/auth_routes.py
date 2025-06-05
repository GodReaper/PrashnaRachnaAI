from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any
from auth.clerk_auth import clerk_auth

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.get("/profile")
async def get_user_profile(current_user: Dict[str, Any] = Depends(clerk_auth.get_current_user)):
    """Protected route that requires authentication"""
    return {
        "message": "Access granted to protected route",
        "user_id": current_user.get("user_id"),
        "email": current_user.get("email"),
        "authenticated": True
    }

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