from sqlalchemy import Column, String, Float, DateTime, Text, Boolean, Uuid
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from src.database import Base


class DBParticipant(Base):
    """Database model for participants."""

    __tablename__ = "participants"

    id = Column(Uuid, primary_key=True, default=uuid.uuid4, index=True)
    name = Column(String(255), nullable=False, index=True)
    email = Column(String(255), unique=True, index=True)
    hourly_rate = Column(Float, nullable=False)
    role = Column(String(255))
    department = Column(String(255))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    meeting_participants = relationship(
        "DBMeetingParticipant", back_populates="participant"
    )

    def __repr__(self):
        return (
            f"<Participant(id={self.id}, name='{self.name}', rate=${self.hourly_rate})>"
        )
