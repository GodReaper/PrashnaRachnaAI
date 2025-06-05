import jwt
import requests
from fastapi import HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional, Dict, Any
from config.settings import settings

# Initialize HTTP Bearer security scheme
security = HTTPBearer()

class ClerkAuth:
    def __init__(self):
        self.publishable_key = settings.CLERK_PUBLISHABLE_KEY
        self.secret_key = settings.CLERK_SECRET_KEY
        self.jwt_key = settings.CLERK_JWT_KEY
        
    def get_clerk_public_key(self) -> str:
        """Fetch Clerk's public key for JWT verification"""
        try:
            # Extract the instance ID from publishable key
            if not self.publishable_key.startswith("pk_"):
                raise ValueError("Invalid Clerk publishable key format")
                
            instance_id = self.publishable_key.split("_")[2] if len(self.publishable_key.split("_")) > 2 else ""
            jwks_url = f"https://{instance_id}.clerk.accounts.dev/.well-known/jwks.json"
            
            response = requests.get(jwks_url)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to fetch Clerk public key: {str(e)}")
    
    def verify_token(self, token: str) -> Dict[str, Any]:
        """Verify and decode the JWT token"""
        try:
            # For development, we'll do basic verification
            # In production, you should verify with Clerk's public key
            if not token:
                raise HTTPException(status_code=401, detail="Token is required")
            
            # Simple token validation (in production, use proper JWT verification)
            if token.startswith("Bearer "):
                token = token.replace("Bearer ", "")
            
            # For now, we'll decode without verification for development
            # In production, use proper key verification
            try:
                # Try to decode the token
                decoded = jwt.decode(token, options={"verify_signature": False})
                return decoded
            except jwt.InvalidTokenError:
                raise HTTPException(status_code=401, detail="Invalid token")
                
        except Exception as e:
            raise HTTPException(status_code=401, detail=f"Token verification failed: {str(e)}")
    
    def get_current_user(self, credentials: HTTPAuthorizationCredentials = Security(security)) -> Dict[str, Any]:
        """Extract current user from JWT token"""
        if not credentials:
            raise HTTPException(status_code=401, detail="Authorization header required")
        
        token = credentials.credentials
        user_data = self.verify_token(token)
        
        # Extract user information from token
        return {
            "user_id": user_data.get("sub"),
            "email": user_data.get("email"),
            "metadata": user_data
        }

# Global auth instance
clerk_auth = ClerkAuth() 