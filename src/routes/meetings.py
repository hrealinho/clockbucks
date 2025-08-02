from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from datetime import datetime
import uuid

from src.models.meeting import Meeting, MeetingCreate, MeetingCostCalculation, MeetingResponse
from src.models.participant import Participant
from src.services.calculator import MeetingCostCalculator

router = APIRouter()

# In-memory storage for demonstration (use a database in production)
meetings_db = {}

@router.post("/meetings/calculate", response_model=MeetingCostCalculation)
async def calculate_meeting_cost(meeting: MeetingCreate):
    """Calculate the cost of a meeting based on participants and duration."""
    # Create a meeting object for calculation
    meeting_obj = Meeting(
        id=str(uuid.uuid4()),
        title=meeting.title,
        duration_minutes=meeting.duration_minutes,
        participants=meeting.participants,
        start_time=meeting.start_time
    )
    
    # Calculate the cost
    cost_calculation = MeetingCostCalculator.calculate_meeting_cost(meeting_obj)
    
    # Store the meeting for future reference
    meeting_response = MeetingResponse(
        id=meeting_obj.id,
        title=meeting_obj.title,
        duration_minutes=meeting_obj.duration_minutes,
        participants=meeting_obj.participants,
        start_time=meeting_obj.start_time,
        total_cost=cost_calculation.total_cost,
        created_at=datetime.now()
    )
    meetings_db[meeting_obj.id] = meeting_response
    
    return cost_calculation

@router.post("/meetings/real-time-cost")
async def calculate_real_time_cost(
    participants: List[Participant],
    elapsed_minutes: int = Query(..., gt=0, description="Minutes elapsed since meeting started")
):
    """Calculate real-time cost during an ongoing meeting."""
    cost_info = MeetingCostCalculator.calculate_real_time_cost(participants, elapsed_minutes)
    return cost_info

@router.post("/meetings", response_model=MeetingResponse)
async def create_meeting(meeting: MeetingCreate):
    """Create a new meeting record."""
    meeting_id = str(uuid.uuid4())
    
    new_meeting = MeetingResponse(
        id=meeting_id,
        title=meeting.title,
        duration_minutes=meeting.duration_minutes,
        participants=meeting.participants,
        start_time=meeting.start_time,
        created_at=datetime.now()
    )
    
    meetings_db[meeting_id] = new_meeting
    return new_meeting

@router.get("/meetings", response_model=List[MeetingResponse])
async def get_all_meetings():
    """Get all meetings."""
    return list(meetings_db.values())

@router.get("/meetings/{meeting_id}", response_model=MeetingResponse)
async def get_meeting(meeting_id: str):
    """Get a specific meeting by ID."""
    if meeting_id not in meetings_db:
        raise HTTPException(status_code=404, detail="Meeting not found")
    
    return meetings_db[meeting_id]

@router.get("/meetings/{meeting_id}/cost", response_model=MeetingCostCalculation)
async def get_meeting_cost(meeting_id: str):
    """Get the cost calculation for a specific meeting."""
    if meeting_id not in meetings_db:
        raise HTTPException(status_code=404, detail="Meeting not found")
    
    meeting = meetings_db[meeting_id]
    
    # Create Meeting object for calculation
    meeting_obj = Meeting(
        id=meeting.id,
        title=meeting.title,
        duration_minutes=meeting.duration_minutes,
        participants=meeting.participants,
        start_time=meeting.start_time
    )
    
    return MeetingCostCalculator.calculate_meeting_cost(meeting_obj)

@router.get("/meetings/statistics/overview")
async def get_meetings_statistics():
    """Get cost statistics for all meetings."""
    meetings_list = []
    for meeting_response in meetings_db.values():
        meeting_obj = Meeting(
            id=meeting_response.id,
            title=meeting_response.title,
            duration_minutes=meeting_response.duration_minutes,
            participants=meeting_response.participants,
            start_time=meeting_response.start_time
        )
        meetings_list.append(meeting_obj)
    
    return MeetingCostCalculator.get_cost_statistics(meetings_list)

@router.delete("/meetings/{meeting_id}")
async def delete_meeting(meeting_id: str):
    """Delete a meeting."""
    if meeting_id not in meetings_db:
        raise HTTPException(status_code=404, detail="Meeting not found")
    
    del meetings_db[meeting_id]
    return {"message": "Meeting deleted successfully"}
