from typing import List, Optional, Dict, Any
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from src.models.db.participant import DBParticipant
from src.models.participant import ParticipantCreate, ParticipantUpdate
from src.repositories.base import BaseRepository
from src.exceptions import NotFoundError, DuplicateError
import logging

logger = logging.getLogger("clockbucks.repositories.participant")


class ParticipantRepository(
    BaseRepository[DBParticipant, ParticipantCreate, ParticipantUpdate]
):
    """Repository for participant data access."""

    def get(self, id: UUID) -> Optional[DBParticipant]:
        """Get participant by ID."""
        try:
            return (
                self.db.query(DBParticipant)
                .filter(and_(DBParticipant.id == id, DBParticipant.is_active == True))
                .first()
            )
        except Exception as e:
            logger.error(f"Error getting participant {id}: {str(e)}")
            raise

    def get_by_email(self, email: str) -> Optional[DBParticipant]:
        """Get participant by email."""
        try:
            return (
                self.db.query(DBParticipant)
                .filter(
                    and_(DBParticipant.email == email, DBParticipant.is_active == True)
                )
                .first()
            )
        except Exception as e:
            logger.error(f"Error getting participant by email {email}: {str(e)}")
            raise

    def get_multi(
        self, skip: int = 0, limit: int = 100, filters: Optional[Dict[str, Any]] = None
    ) -> List[DBParticipant]:
        """Get multiple participants with optional filtering."""
        try:
            query = self.db.query(DBParticipant).filter(DBParticipant.is_active == True)

            if filters:
                if "department" in filters:
                    query = query.filter(
                        DBParticipant.department == filters["department"]
                    )
                if "role" in filters:
                    query = query.filter(DBParticipant.role == filters["role"])
                if "min_rate" in filters:
                    query = query.filter(
                        DBParticipant.hourly_rate >= filters["min_rate"]
                    )
                if "max_rate" in filters:
                    query = query.filter(
                        DBParticipant.hourly_rate <= filters["max_rate"]
                    )
                if "search" in filters:
                    search_term = f"%{filters['search']}%"
                    query = query.filter(
                        or_(
                            DBParticipant.name.ilike(search_term),
                            DBParticipant.email.ilike(search_term),
                            DBParticipant.role.ilike(search_term),
                        )
                    )

            return query.offset(skip).limit(limit).all()
        except Exception as e:
            logger.error(f"Error getting participants: {str(e)}")
            raise

    def create(self, obj_in: ParticipantCreate) -> DBParticipant:
        """Create a new participant."""
        try:
            # Check for duplicate email
            if obj_in.email and self.get_by_email(obj_in.email):
                raise DuplicateError(
                    f"Participant with email {obj_in.email} already exists"
                )

            db_obj = DBParticipant(**obj_in.dict())
            self.db.add(db_obj)
            self.db.commit()
            self.db.refresh(db_obj)

            logger.info(f"Created participant: {db_obj.id}")
            return db_obj
        except DuplicateError:
            raise
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating participant: {str(e)}")
            raise

    def update(self, db_obj: DBParticipant, obj_in: ParticipantUpdate) -> DBParticipant:
        """Update an existing participant."""
        try:
            # Check for email conflicts if updating email
            if obj_in.email and obj_in.email != db_obj.email:
                existing = self.get_by_email(obj_in.email)
                if existing and existing.id != db_obj.id:
                    raise DuplicateError(
                        f"Participant with email {obj_in.email} already exists"
                    )

            update_data = obj_in.dict(exclude_unset=True)
            for field, value in update_data.items():
                setattr(db_obj, field, value)

            self.db.commit()
            self.db.refresh(db_obj)

            logger.info(f"Updated participant: {db_obj.id}")
            return db_obj
        except DuplicateError:
            raise
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating participant {db_obj.id}: {str(e)}")
            raise

    def delete(self, id: UUID) -> bool:
        """Soft delete a participant."""
        try:
            db_obj = self.get(id)
            if not db_obj:
                raise NotFoundError(f"Participant {id} not found")

            db_obj.is_active = False
            self.db.commit()

            logger.info(f"Soft deleted participant: {id}")
            return True
        except NotFoundError:
            raise
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error deleting participant {id}: {str(e)}")
            raise

    def hard_delete(self, id: UUID) -> bool:
        """Hard delete a participant."""
        try:
            db_obj = self.get(id)
            if not db_obj:
                raise NotFoundError(f"Participant {id} not found")

            self.db.delete(db_obj)
            self.db.commit()

            logger.info(f"Hard deleted participant: {id}")
            return True
        except NotFoundError:
            raise
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error hard deleting participant {id}: {str(e)}")
            raise

    def count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """Count participants with optional filtering."""
        try:
            query = self.db.query(DBParticipant).filter(DBParticipant.is_active == True)

            if filters:
                if "department" in filters:
                    query = query.filter(
                        DBParticipant.department == filters["department"]
                    )
                if "role" in filters:
                    query = query.filter(DBParticipant.role == filters["role"])

            return query.count()
        except Exception as e:
            logger.error(f"Error counting participants: {str(e)}")
            raise
