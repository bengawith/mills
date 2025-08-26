"""
Base service class with common database operations.
"""
from typing import Type, Optional, List, Any
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
import logging

logger = logging.getLogger(__name__)

class BaseService:
    """
    Base service class providing common CRUD operations.
    """
    
    def __init__(self, model: Type[Any]):
        self.model = model
    
    def get_by_id(self, db: Session, id: Any) -> Optional[Any]:
        """Get a single record by ID."""
        try:
            return db.query(self.model).filter(self.model.id == id).first()
        except SQLAlchemyError as e:
            logger.error(f"Error fetching {self.model.__name__} by ID {id}: {str(e)}")
            raise
    
    def get_all(self, db: Session, skip: int = 0, limit: int = 100) -> List[Any]:
        """Get all records with pagination."""
        try:
            return db.query(self.model).offset(skip).limit(limit).all()
        except SQLAlchemyError as e:
            logger.error(f"Error fetching all {self.model.__name__}: {str(e)}")
            raise
    
    def create(self, db: Session, obj_data: dict) -> Any:
        """Create a new record."""
        try:
            db_obj = self.model(**obj_data)
            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
            logger.info(f"Created new {self.model.__name__} with ID {db_obj.id}")
            return db_obj
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"Error creating {self.model.__name__}: {str(e)}")
            raise
    
    def update(self, db: Session, id: Any, obj_data: dict) -> Optional[Any]:
        """Update an existing record."""
        try:
            db_obj = self.get_by_id(db, id)
            if not db_obj:
                return None
            
            for field, value in obj_data.items():
                if hasattr(db_obj, field):
                    setattr(db_obj, field, value)
            
            db.commit()
            db.refresh(db_obj)
            logger.info(f"Updated {self.model.__name__} with ID {id}")
            return db_obj
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"Error updating {self.model.__name__} with ID {id}: {str(e)}")
            raise
    
    def delete(self, db: Session, id: Any) -> bool:
        """Delete a record by ID."""
        try:
            db_obj = self.get_by_id(db, id)
            if not db_obj:
                return False
            
            db.delete(db_obj)
            db.commit()
            logger.info(f"Deleted {self.model.__name__} with ID {id}")
            return True
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"Error deleting {self.model.__name__} with ID {id}: {str(e)}")
            raise
    
    def count(self, db: Session) -> int:
        """Get total count of records."""
        try:
            return db.query(self.model).count()
        except SQLAlchemyError as e:
            logger.error(f"Error counting {self.model.__name__}: {str(e)}")
            raise
