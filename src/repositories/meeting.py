from typing import List, Optional, Dict, Any
from uuid import UUID
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, desc
from datetime import datetime

from src.repositories.base import BaseRepository
from src.models.db.meeting import DBMeeting, DBMeetingParticipant
from src.models.db.participant import DBParticipant
from src.models.meeting import MeetingCreate, MeetingUpdate


class MeetingRepository(BaseRepository[DBMeeting, MeetingCreate, MeetingUpdate]):
    """Repository for meeting database operations."""

    def __init__(self, db: Session):
        super().__init__(db)
        self.model = DBMeeting

    def get(self, id: UUID) -> Optional[DBMeeting]:
        """Get a meeting by ID with participants."""
        return (
            self.db.query(self.model)
            .options(
                joinedload(self.model.participants).joinedload(
                    DBMeetingParticipant.participant
                )
            )
            .filter(self.model.id == id)
            .first()
        )

    def get_multi(
        self, skip: int = 0, limit: int = 100, filters: Optional[Dict[str, Any]] = None
    ) -> List[DBMeeting]:
        """Get multiple meetings with optional filtering."""
        query = self.db.query(self.model).options(
            joinedload(self.model.participants).joinedload(
                DBMeetingParticipant.participant
            )
        )

        if filters:
            if "status" in filters:
                query = query.filter(self.model.status == filters["status"])
            if "meeting_type" in filters:
                query = query.filter(self.model.meeting_type == filters["meeting_type"])
            if "start_date" in filters:
                query = query.filter(self.model.start_time >= filters["start_date"])
            if "end_date" in filters:
                query = query.filter(self.model.start_time <= filters["end_date"])
            if "search" in filters:
                search_term = f"%{filters['search']}%"
                query = query.filter(
                    or_(
                        self.model.title.ilike(search_term),
                        self.model.description.ilike(search_term),
                    )
                )

        return (
            query.order_by(desc(self.model.created_at)).offset(skip).limit(limit).all()
        )

    def create(self, obj_in: MeetingCreate) -> DBMeeting:
        """Create a new meeting with participants."""
        db_meeting = DBMeeting(
            title=obj_in.title,
            description=getattr(obj_in, "description", None),
            duration_minutes=obj_in.duration_minutes,
            start_time=obj_in.start_time,
            meeting_type=getattr(obj_in, "meeting_type", None),
            status="scheduled",
        )

        self.db.add(db_meeting)
        self.db.flush()

        for participant_data in obj_in.participants:
            if participant_data.id:
                db_participant = (
                    self.db.query(DBParticipant)
                    .filter(DBParticipant.id == participant_data.id)
                    .first()
                )
                if db_participant:
                    meeting_participant = DBMeetingParticipant(
                        meeting_id=db_meeting.id,
                        participant_id=db_participant.id,
                        hourly_rate_at_time=db_participant.hourly_rate,
                        attendance_status="confirmed",
                    )
                    self.db.add(meeting_participant)
            else:
                db_participant = (
                    self.db.query(DBParticipant)
                    .filter(DBParticipant.name == participant_data.name)
                    .first()
                )
                if not db_participant:
                    db_participant = DBParticipant(
                        name=participant_data.name,
                        email=getattr(participant_data, "email", None),
                        hourly_rate=participant_data.hourly_rate,
                        role=getattr(participant_data, "role", None),
                        department=getattr(participant_data, "department", None),
                    )
                    self.db.add(db_participant)
                    self.db.flush()

                meeting_participant = DBMeetingParticipant(
                    meeting_id=db_meeting.id,
                    participant_id=db_participant.id,
                    hourly_rate_at_time=participant_data.hourly_rate,
                    attendance_status="confirmed",
                )
                self.db.add(meeting_participant)

        self.db.commit()
        self.db.refresh(db_meeting)
        return db_meeting

    def update(self, db_obj: DBMeeting, obj_in: MeetingUpdate) -> DBMeeting:
        """Update a meeting."""
        update_data = obj_in.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)

        db_obj.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj

    def delete(self, id: UUID) -> bool:
        """Delete a meeting and its participants."""
        db_meeting = self.get(id)
        if db_meeting:
            self.db.delete(db_meeting)
            self.db.commit()
            return True
        return False

    def count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """Count meetings with optional filtering."""
        query = self.db.query(self.model)
        if filters:
            if "status" in filters:
                query = query.filter(self.model.status == filters["status"])
            if "meeting_type" in filters:
                query = query.filter(self.model.meeting_type == filters["meeting_type"])
        return query.count()

    def get_by_status(self, status: str) -> List[DBMeeting]:
        """Get meetings by status."""
        return self.db.query(self.model).filter(self.model.status == status).all()

    def get_active_meetings(self) -> List[DBMeeting]:
        """Get currently active meetings."""
        return self.get_by_status("in_progress")

    def get_upcoming_meetings(self, limit: int = 10) -> List[DBMeeting]:
        """Get upcoming scheduled meetings."""
        now = datetime.utcnow()
        return (
            self.db.query(self.model)
            .filter(and_(self.model.status == "scheduled", self.model.start_time > now))
            .order_by(self.model.start_time)
            .limit(limit)
            .all()
        )

    def get_meeting_statistics(self) -> Dict[str, Any]:
        """Get meeting statistics."""
        from sqlalchemy import func, case

        stats = self.db.query(
            func.count(self.model.id).label("total_meetings"),
            func.sum(self.model.total_cost).label("total_cost"),
            func.avg(self.model.total_cost).label("average_cost"),
            func.avg(self.model.duration_minutes).label("average_duration"),
            func.sum(case([(self.model.status == "completed", 1)], else_=0)).label(
                "completed_meetings"
            ),
            func.sum(case([(self.model.status == "in_progress", 1)], else_=0)).label(
                "active_meetings"
            ),
            func.sum(case([(self.model.status == "scheduled", 1)], else_=0)).label(
                "scheduled_meetings"
            ),
        ).first()

        return {
            "total_meetings": stats.total_meetings or 0,
            "total_cost": float(stats.total_cost or 0),
            "average_cost": float(stats.average_cost or 0),
            "average_duration": float(stats.average_duration or 0),
            "completed_meetings": stats.completed_meetings or 0,
            "active_meetings": stats.active_meetings or 0,
            "scheduled_meetings": stats.scheduled_meetings or 0,
        }

    def start_meeting(self, meeting_id: UUID) -> Optional[DBMeeting]:
        """Start a meeting (change status to in_progress)."""
        db_meeting = self.get(meeting_id)
        if db_meeting and db_meeting.status == "scheduled":
            db_meeting.status = "in_progress"
            db_meeting.start_time = datetime.utcnow()
            db_meeting.updated_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(db_meeting)
            return db_meeting
        return None

    def end_meeting(
        self, meeting_id: UUID, total_cost: float = None
    ) -> Optional[DBMeeting]:
        """End a meeting (change status to completed)."""
        db_meeting = self.get(meeting_id)
        if db_meeting and db_meeting.status == "in_progress":
            db_meeting.status = "completed"
            db_meeting.end_time = datetime.utcnow()
            db_meeting.updated_at = datetime.utcnow()

            if total_cost is not None:
                db_meeting.total_cost = total_cost

                # Calculate individual costs for participants
                if db_meeting.duration_minutes and db_meeting.participants:
                    for meeting_participant in db_meeting.participants:
                        individual_cost = (
                            meeting_participant.hourly_rate_at_time / 60
                        ) * db_meeting.duration_minutes
                        meeting_participant.individual_cost = individual_cost
                        meeting_participant.attendance_status = "attended"

            self.db.commit()
            self.db.refresh(db_meeting)
            return db_meeting
        return None
