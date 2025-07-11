from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import Optional, Dict, Any
from app.models.user import User

class UserService:
    
    @staticmethod
    def get_user_by_clerk_id(db: Session, clerk_user_id: str) -> Optional[User]:
        """Get user by Clerk user ID"""
        return db.query(User).filter(User.clerk_user_id == clerk_user_id).first()
    
    @staticmethod
    def get_user_by_email(db: Session, email: str) -> Optional[User]:
        """Get user by email"""
        return db.query(User).filter(User.email == email).first()
    
    @staticmethod
    def create_user(db: Session, user_data: Dict[str, Any]) -> User:
        """Create a new user"""
        try:
            user = User(
                clerk_user_id=user_data["clerk_user_id"],
                email=user_data["email"],
                first_name=user_data.get("first_name"),
                last_name=user_data.get("last_name"),
                profile_image_url=user_data.get("profile_image_url")
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            return user
        except IntegrityError:
            db.rollback()
            raise ValueError("User already exists")
    
    @staticmethod
    def get_or_create_user(db: Session, user_data: Dict[str, Any]) -> User:
        """Get existing user or create new one"""
        # Validate input data
        clerk_user_id = user_data.get("clerk_user_id")
        if not clerk_user_id:
            raise ValueError("clerk_user_id is required")
        
        # Email can be empty initially - will be updated when available
        email = user_data.get("email", "") or ""
        
        # First, try to get existing user
        user = UserService.get_user_by_clerk_id(db, clerk_user_id)
        if user:
            return user
        
        # User doesn't exist, try to create
        try:
            user = UserService.create_user(db, user_data)
            return user
        except ValueError as e:
            if "User already exists" in str(e):
                # Race condition: user was created between our check and creation
                # Try to get the user again
                user = UserService.get_user_by_clerk_id(db, clerk_user_id)
                if user:
                    return user
                else:
                    # This shouldn't happen, but handle it gracefully
                    raise ValueError(f"Failed to create or retrieve user for clerk_user_id: {clerk_user_id}")
            else:
                # Re-raise other ValueError exceptions
                raise
        except Exception as e:
            raise ValueError(f"Database error during user creation: {str(e)}")
    
    @staticmethod
    def update_user(db: Session, user_id: int, update_data: Dict[str, Any]) -> Optional[User]:
        """Update user information"""
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            for key, value in update_data.items():
                if hasattr(user, key):
                    setattr(user, key, value)
            db.commit()
            db.refresh(user)
        return user
    
    @staticmethod
    def deactivate_user(db: Session, user_id: int) -> bool:
        """Deactivate a user"""
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            user.is_active = False
            db.commit()
            return True
        return False 