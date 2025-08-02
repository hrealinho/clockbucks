from sqlalchemy import Column, String, Integer, Float, DateTime, Text, ForeignKey, Table
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from src.database import Base


class DBMeeting(Base):
    """Database model for meetings."""

    __tablename__ = "meetings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    title = Column(String(500), nullable=False, index=True)
    description = Column(Text)
    duration_minutes = Column(Integer, nullable=False)
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    total_cost = Column(Float)
    cost_per_minute = Column(Float)
    meeting_type = Column(String(100))  # 'standup', 'planning', 'review', etc.
    status = Column(
        String(50), default="scheduled"
    )  # 'scheduled', 'in_progress', 'completed', 'cancelled'
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    participants = relationship(
        "DBMeetingParticipant", back_populates="meeting", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Meeting(id={self.id}, title='{self.title}', cost=${self.total_cost})>"


class DBMeetingParticipant(Base):
    """Association table for meeting participants with their individual costs."""

    __tablename__ = "meeting_participants"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    meeting_id = Column(UUID(as_uuid=True), ForeignKey("meetings.id"), nullable=False)
    participant_id = Column(
        UUID(as_uuid=True), ForeignKey("participants.id"), nullable=False
    )
    hourly_rate_at_time = Column(Float, nullable=False)  # Rate at the time of meeting
    individual_cost = Column(Float)
    attendance_status = Column(
        String(50), default="confirmed"
    )  # 'confirmed', 'tentative', 'declined', 'attended'
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    meeting = relationship("DBMeeting", back_populates="participants")
    participant = relationship("DBParticipant", back_populates="meeting_participants")

    def __repr__(self):
        return f"<MeetingParticipant(meeting_id={self.meeting_id}, participant_id={self.participant_id}, cost=${self.individual_cost})>"
