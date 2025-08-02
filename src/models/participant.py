from pydantic import BaseModel, Field, EmailStr, validator
from typing import Optional
from datetime import datetime
from uuid import UUID

class ParticipantBase(BaseModel):
    """Base participant model with common fields."""
    name: str = Field(..., min_length=1, max_length=255, description="Participant's name")
    email: Optional[EmailStr] = Field(None, description="Participant's email address")
    hourly_rate: float = Field(..., gt=0, le=10000, description="Hourly rate in USD")
    role: Optional[str] = Field(None, max_length=255, description="Job role/title")
    department: Optional[str] = Field(None, max_length=255, description="Department")
    
    @validator('hourly_rate')
    def validate_hourly_rate(cls, v):
        if v <= 0:
            raise ValueError('Hourly rate must be positive')
        if v > 10000:
            raise ValueError('Hourly rate seems too high (max $10,000/hour)')
        return v

class ParticipantCreate(ParticipantBase):
    """Schema for creating a participant."""
    pass
    
    class Config:
        schema_extra = {
            "example": {
                "name": "John Doe",
                "email": "john.doe@company.com",
                "hourly_rate": 75.0,
                "role": "Senior Developer",
                "department": "Engineering"
            }
        }

class ParticipantUpdate(BaseModel):
    """Schema for updating a participant."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    email: Optional[EmailStr] = None
    hourly_rate: Optional[float] = Field(None, gt=0, le=10000)
    role: Optional[str] = Field(None, max_length=255)
    department: Optional[str] = Field(None, max_length=255)
    is_active: Optional[bool] = None
    
    @validator('hourly_rate')
    def validate_hourly_rate(cls, v):
        if v is not None:
            if v <= 0:
                raise ValueError('Hourly rate must be positive')
            if v > 10000:
                raise ValueError('Hourly rate seems too high (max $10,000/hour)')
        return v

class Participant(ParticipantBase):
    """Schema for participant responses."""
    id: Optional[UUID] = None  # Made optional for backward compatibility
    is_active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        from_orm = True
        schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "name": "John Doe",
                "email": "john.doe@company.com",
                "hourly_rate": 75.0,
                "role": "Senior Developer",
                "department": "Engineering",
                "is_active": True,
                "created_at": "2025-01-15T10:00:00Z",
                "updated_at": "2025-01-15T10:00:00Z"
            }
        }

class ParticipantSummary(BaseModel):
    """Simplified participant schema for lists."""
    id: UUID
    name: str
    email: Optional[EmailStr]
    hourly_rate: float
    role: Optional[str]
    department: Optional[str]
    
    class Config:
        from_orm = True
