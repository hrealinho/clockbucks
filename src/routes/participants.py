from fastapi import APIRouter, HTTPException, Depends
from typing import List
from uuid import UUID
from sqlalchemy.orm import Session

from src.models.participant import Participant, ParticipantCreate, ParticipantUpdate
from src.repositories.participant import ParticipantRepository
from src.database import get_db
from src.exceptions import NotFoundError, DuplicateError

router = APIRouter()


def get_participant_repository(db: Session = Depends(get_db)) -> ParticipantRepository:
    return ParticipantRepository(db)


@router.post(
    "/participants",
    response_model=Participant,
    status_code=201,
    summary="Create New Participant",
)
async def create_participant(
    participant: ParticipantCreate,
    repo: ParticipantRepository = Depends(get_participant_repository),
):
    try:
        db_participant = repo.create(participant)
        return Participant.model_validate(db_participant)
    except DuplicateError as e:
        raise HTTPException(status_code=409, detail=str(e))


@router.get(
    "/participants",
    response_model=List[Participant],
    summary="List All Participants",
)
async def get_all_participants(
    repo: ParticipantRepository = Depends(get_participant_repository),
):
    db_participants = repo.get_multi()
    return [Participant.model_validate(p) for p in db_participants]


@router.get(
    "/participants/{participant_id}",
    response_model=Participant,
    summary="Get Participant by ID",
)
async def get_participant(
    participant_id: UUID,
    repo: ParticipantRepository = Depends(get_participant_repository),
):
    db_participant = repo.get(participant_id)
    if not db_participant:
        raise HTTPException(status_code=404, detail="Participant not found")
    return Participant.model_validate(db_participant)


@router.put(
    "/participants/{participant_id}",
    response_model=Participant,
    summary="Update Participant",
)
async def update_participant(
    participant_id: UUID,
    update_data: ParticipantUpdate,
    repo: ParticipantRepository = Depends(get_participant_repository),
):
    db_participant = repo.get(participant_id)
    if not db_participant:
        raise HTTPException(status_code=404, detail="Participant not found")
    try:
        updated = repo.update(db_participant, update_data)
        return Participant.model_validate(updated)
    except DuplicateError as e:
        raise HTTPException(status_code=409, detail=str(e))


@router.delete(
    "/participants/{participant_id}",
    status_code=204,
    summary="Delete Participant",
)
async def delete_participant(
    participant_id: UUID,
    repo: ParticipantRepository = Depends(get_participant_repository),
):
    try:
        repo.delete(participant_id)
    except NotFoundError:
        raise HTTPException(status_code=404, detail="Participant not found")
