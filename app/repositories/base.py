"""
Base repository module providing abstract CRUD operations.

This module implements the Repository pattern with a generic BaseRepository class
that provides common database operations for all entity repositories. It promotes
code reuse and consistent data access patterns across the application.
"""

from abc import ABC
from typing import TypeVar, Generic, List, Optional
from sqlalchemy.orm import Session
from datetime import datetime


# Generic type variable for SQLAlchemy models
T = TypeVar('T')


class BaseRepository(ABC, Generic[T]):
    """
    Abstract base repository providing generic CRUD operations.
    
    This class uses dependency injection to accept a SQLAlchemy session
    and provides common database operations that can be inherited by
    concrete repository implementations.
    
    Type Parameters:
        T: The SQLAlchemy model type this repository manages
    
    Attributes:
        model_class: The SQLAlchemy model class this repository operates on
        session: The SQLAlchemy database session
    """
    
    def __init__(self, model_class: type[T], session: Session):
        """
        Initialize the repository with a model class and database session.
        
        Args:
            model_class: The SQLAlchemy model class to operate on
            session: The SQLAlchemy session for database operations
        """
        self.model_class = model_class
        self.session = session
    
    def create(self, entity: T) -> T:
        """
        Create a new entity in the database.
        
        Adds the entity to the session, flushes to generate any database-assigned
        values (like auto-increment IDs), and returns the entity.
        
        Args:
            entity: The SQLAlchemy model instance to create
            
        Returns:
            The created entity with any database-generated values populated
            
        Raises:
            IntegrityError: If unique constraints or foreign key constraints are violated
        """
        self.session.add(entity)
        self.session.flush()  # Flush to get database-generated values without committing
        return entity
    
    def get_by_id(self, id: any) -> Optional[T]:
        """
        Retrieve an entity by its primary key.
        
        Args:
            id: The primary key value to search for
            
        Returns:
            The entity if found, None otherwise
        """
        return self.session.query(self.model_class).filter(
            self.model_class.id == id
        ).first()
    
    def get_all(self) -> List[T]:
        """
        Retrieve all entities of this type.
        
        Returns:
            List of all entities, empty list if none exist
        """
        return self.session.query(self.model_class).all()
    
    def update(self, entity: T) -> T:
        """
        Update an existing entity in the database.
        
        Merges the entity with the session (handles both attached and detached entities),
        flushes to persist changes, and returns the updated entity.
        
        Args:
            entity: The SQLAlchemy model instance with updated values
            
        Returns:
            The updated entity
            
        Raises:
            IntegrityError: If unique constraints or foreign key constraints are violated
        """
        merged_entity = self.session.merge(entity)
        self.session.flush()
        return merged_entity
    
    def delete(self, id: any) -> bool:
        """
        Delete an entity by its primary key.
        
        Performs soft delete if the entity has a 'deleted_at' column, otherwise
        performs hard delete. For soft delete, sets deleted_at to current UTC timestamp.
        
        Args:
            id: The primary key value of the entity to delete
            
        Returns:
            True if entity was deleted, False if entity was not found
        """
        entity = self.get_by_id(id)
        if entity is None:
            return False
        
        # Check if the model supports soft delete (has deleted_at column)
        if hasattr(entity, 'deleted_at'):
            # Soft delete: set deleted_at timestamp
            entity.deleted_at = datetime.utcnow()
            self.session.flush()
        else:
            # Hard delete: remove from database
            self.session.delete(entity)
            self.session.flush()
        
        return True
