from sqlalchemy import Column, String, Float, DateTime, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from src.database import Base

class DBParticipant(Base):
    """Database model for participants."""
    
    __tablename__ = "participants"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    name = Column(String(255), nullable=False, index=True)
    email = Column(String(255), unique=True, index=True)
    hourly_rate = Column(Float, nullable=False)
    role = Column(String(255))
    department = Column(String(255))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    meeting_participants = relationship("DBMeetingParticipant", back_populates="participant")
    
    def __repr__(self):
        return f"<Participant(id={self.id}, name='{self.name}', rate=${self.hourly_rate})>"
