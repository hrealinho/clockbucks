from abc import ABC, abstractmethod
from typing import Generic, TypeVar, List, Optional, Dict, Any
from uuid import UUID
from sqlalchemy.orm import Session

ModelType = TypeVar("ModelType")
CreateSchemaType = TypeVar("CreateSchemaType")
UpdateSchemaType = TypeVar("UpdateSchemaType")

class BaseRepository(Generic[ModelType, CreateSchemaType, UpdateSchemaType], ABC):
    """Abstract base repository class."""
    
    def __init__(self, db: Session):
        self.db = db
    
    @abstractmethod
    def get(self, id: UUID) -> Optional[ModelType]:
        """Get a single record by ID."""
        pass
    
    @abstractmethod
    def get_multi(
        self, 
        skip: int = 0, 
        limit: int = 100, 
        filters: Optional[Dict[str, Any]] = None
    ) -> List[ModelType]:
        """Get multiple records with optional filtering."""
        pass
    
    @abstractmethod
    def create(self, obj_in: CreateSchemaType) -> ModelType:
        """Create a new record."""
        pass
    
    @abstractmethod
    def update(self, db_obj: ModelType, obj_in: UpdateSchemaType) -> ModelType:
        """Update an existing record."""
        pass
    
    @abstractmethod
    def delete(self, id: UUID) -> bool:
        """Delete a record by ID."""
        pass
    
    @abstractmethod
    def count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """Count records with optional filtering."""
        pass
