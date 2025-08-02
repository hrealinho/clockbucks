from fastapi import APIRouter, HTTPException
from typing import List
from datetime import datetime
import uuid

from src.models.participant import Participant, ParticipantCreate, ParticipantResponse

router = APIRouter()

# In-memory storage for demonstration (use a database in production)
participants_db = {}

@router.post("/participants", response_model=ParticipantResponse)
async def create_participant(participant: ParticipantCreate):
    """Create a new participant."""
    participant_id = str(uuid.uuid4())
    
    new_participant = ParticipantResponse(
        id=participant_id,
        name=participant.name,
        hourly_rate=participant.hourly_rate,
        role=participant.role,
        created_at=datetime.now()
    )
    
    participants_db[participant_id] = new_participant
    return new_participant

@router.get("/participants", response_model=List[ParticipantResponse])
async def get_all_participants():
    """Get all participants."""
    return list(participants_db.values())

@router.get("/participants/{participant_id}", response_model=ParticipantResponse)
async def get_participant(participant_id: str):
    """Get a specific participant by ID."""
    if participant_id not in participants_db:
        raise HTTPException(status_code=404, detail="Participant not found")
    
    return participants_db[participant_id]

@router.put("/participants/{participant_id}", response_model=ParticipantResponse)
async def update_participant(participant_id: str, participant: ParticipantCreate):
    """Update an existing participant."""
    if participant_id not in participants_db:
        raise HTTPException(status_code=404, detail="Participant not found")
    
    existing_participant = participants_db[participant_id]
    updated_participant = ParticipantResponse(
        id=participant_id,
        name=participant.name,
        hourly_rate=participant.hourly_rate,
        role=participant.role,
        created_at=existing_participant.created_at
    )
    
    participants_db[participant_id] = updated_participant
    return updated_participant

@router.delete("/participants/{participant_id}")
async def delete_participant(participant_id: str):
    """Delete a participant."""
    if participant_id not in participants_db:
        raise HTTPException(status_code=404, detail="Participant not found")
    
    del participants_db[participant_id]
    return {"message": "Participant deleted successfully"}
