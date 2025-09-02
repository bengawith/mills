"""
User management service layer.
"""
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime, timezone
import logging

from services.base_service import BaseService
from database_models import User
from security import get_password_hash, verify_password
import schemas

logger = logging.getLogger(__name__)

class UserService(BaseService):
    """
    Service class for user management operations.
    Provides methods for user creation, authentication, and retrieval.
    Inherits from BaseService for common CRUD operations.
    """
    def __init__(self) -> None:
        """
        Initialize UserService with User as the model.
        """
        super().__init__(User)
    
    def get_by_email(
        self,
        db: Session,
        email: str
    ) -> Optional[User]:
        """
        Get user by email address.
        
        Args:
            db (Session): SQLAlchemy database session.
            email (str): Email address to search for.
        
        Returns:
            Optional[User]: User object if found, else None.
        """
        try:
            return db.query(User).filter(User.email == email).first()
        except SQLAlchemyError as e:
            logger.error(f"Error fetching user by email {email}: {str(e)}")
            raise
    
    def create_user(
        self,
        db: Session,
        user_data: schemas.UserCreate
    ) -> User:
        """
        Create a new user with hashed password.
        
        Args:
            db (Session): SQLAlchemy database session.
            user_data (schemas.UserCreate): Data for the new user.
        
        Returns:
            User: The created user object.
        
        Raises:
            ValueError: If user already exists.
        """
        try:
            # Check if user already exists
            existing_user = self.get_by_email(db, user_data.email)
            if existing_user:
                raise ValueError(f"User with email {user_data.email} already exists")
            
            # Hash the password
            hashed_password = get_password_hash(user_data.password)
            
            # Create user data
            user_dict = {
                "email": user_data.email,
                "first_name": user_data.first_name,
                "last_name": user_data.last_name,
                "hashed_password": hashed_password,
                "role": user_data.role,
                "onboarded": False,
                "disabled": False
            }
            
            return self.create(db, user_dict)
        except ValueError:
            raise
        except SQLAlchemyError as e:
            logger.error(f"Error creating user: {str(e)}")
            raise
    
    def authenticate_user(
        self,
        db: Session,
        email: str,
        password: str
    ) -> Optional[User]:
        """
        Authenticate a user by email and password.
        
        Args:
            db (Session): SQLAlchemy database session.
            email (str): User's email address.
            password (str): User's password.
        
        Returns:
            Optional[User]: Authenticated user object if credentials are valid, else None.
        """
        try:
            user = self.get_by_email(db, email)
            if not user:
                return None
            
            # Fix: Extract string value from SQLAlchemy column if necessary
            hashed_password = user.hashed_password if isinstance(user.hashed_password, str) else str(user.hashed_password)
            if not verify_password(password, hashed_password):
                return None
            
            return user
        except SQLAlchemyError as e:
            logger.error(f"Error authenticating user {email}: {str(e)}")
            raise
    
    def update_user_profile(self, db: Session, user_id: int, update_data: schemas.UserUpdate) -> Optional[User]:
        """Update user profile information."""
        try:
            # Convert Pydantic model to dict, excluding None values
            update_dict = update_data.model_dump(exclude_unset=True)
            return self.update(db, user_id, update_dict)
        except SQLAlchemyError as e:
            logger.error(f"Error updating user profile for user {user_id}: {str(e)}")
            raise
    
    def get_active_users(self, db: Session) -> List[User]:
        """Get all active (non-disabled) users."""
        try:
            return db.query(User).filter(User.disabled == False).all()
        except SQLAlchemyError as e:
            logger.error(f"Error fetching active users: {str(e)}")
            raise
    
    def disable_user(self, db: Session, user_id: int) -> Optional[User]:
        """Disable a user account."""
        try:
            return self.update(db, user_id, {"disabled": True})
        except SQLAlchemyError as e:
            logger.error(f"Error disabling user {user_id}: {str(e)}")
            raise
    
    def enable_user(self, db: Session, user_id: int) -> Optional[User]:
        """Enable a user account."""
        try:
            return self.update(db, user_id, {"disabled": False})
        except SQLAlchemyError as e:
            logger.error(f"Error enabling user {user_id}: {str(e)}")
            raise
    
    def mark_user_onboarded(self, db: Session, user_id: int) -> Optional[User]:
        """Mark a user as onboarded."""
        try:
            return self.update(db, user_id, {"onboarded": True})
        except SQLAlchemyError as e:
            logger.error(f"Error marking user {user_id} as onboarded: {str(e)}")
            raise
