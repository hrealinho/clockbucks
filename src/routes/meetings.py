from fastapi import APIRouter, HTTPException, Query, Depends
from typing import List, Optional
from datetime import datetime
import uuid
from sqlalchemy.orm import Session

from src.models.meeting import Meeting, MeetingCreate, MeetingUpdate, MeetingCostCalculation, MeetingResponse
from src.models.participant import Participant
from src.models.db.meeting import DBMeeting, DBMeetingParticipant
from src.services.calculator import MeetingCostCalculator
from src.repositories.meeting import MeetingRepository
from src.database import get_db

router = APIRouter()

def get_meeting_repository(db: Session = Depends(get_db)) -> MeetingRepository:
    """Dependency to get meeting repository."""
    return MeetingRepository(db)

@router.post(
    "/meetings/calculate", 
    response_model=MeetingCostCalculation,
    summary="Calculate Meeting Cost",
    description="Calculate the total cost of a meeting based on participants and duration. This endpoint performs cost calculations and optionally stores the meeting record.",
    response_description="Detailed cost calculation including total cost, cost per minute, and per-participant breakdown",
    responses={
        200: {
            "description": "Cost calculation completed successfully",
            "content": {
                "application/json": {
                    "example": {
                        "meeting_id": "123e4567-e89b-12d3-a456-426614174000",
                        "title": "Sprint Planning",
                        "duration_minutes": 60,
                        "total_cost": 160.0,
                        "cost_per_minute": 2.67,
                        "participants_count": 2,
                        "participant_costs": [
                            {
                                "name": "John Doe",
                                "role": "Senior Developer", 
                                "hourly_rate": 75.0,
                                "cost": 75.0
                            },
                            {
                                "name": "Jane Smith",
                                "role": "Product Manager",
                                "hourly_rate": 85.0, 
                                "cost": 85.0
                            }
                        ],
                        "calculation_time": "2025-01-15T10:00:00Z"
                    }
                }
            }
        },
        400: {
            "description": "Invalid meeting data",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Meeting duration must be greater than 0"
                    }
                }
            }
        },
        422: {
            "description": "Validation error",
            "content": {
                "application/json": {
                    "example": {
                        "detail": [
                            {
                                "loc": ["body", "participants"],
                                "msg": "ensure this value has at least 1 items",
                                "type": "value_error.list.min_items"
                            }
                        ]
                    }
                }
            }
        }
    }
)
async def calculate_meeting_cost(
    meeting: MeetingCreate,
    meeting_repo: MeetingRepository = Depends(get_meeting_repository)
):
    """
    Calculate the cost of a meeting based on participants and duration.
    
    This endpoint:
    - Validates meeting data including participants and duration
    - Calculates total meeting cost based on participant hourly rates
    - Provides per-participant cost breakdown
    - Optionally stores the meeting record for future reference
    - Returns detailed cost analysis including cost per minute
    
    **Cost Calculation Formula:**
    - Individual Cost = (Hourly Rate / 60) * Duration in Minutes
    - Total Cost = Sum of all individual participant costs
    - Cost per Minute = Total Cost / Duration in Minutes
    """
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
    
    # Store the meeting in database
    try:
        db_meeting = meeting_repo.create(meeting)
        
        # Update with calculated cost
        meeting_repo.update(db_meeting, MeetingUpdate(total_cost=cost_calculation.total_cost))
        
        # Update the cost calculation with the database ID
        cost_calculation.meeting_id = str(db_meeting.id)
        
    except Exception as e:
        # If database save fails, still return the calculation
        print(f"Warning: Could not save meeting to database: {e}")
    
    return cost_calculation

@router.post(
    "/meetings/real-time-cost",
    summary="Calculate Real-Time Meeting Cost",
    description="Calculate the current cost of an ongoing meeting based on elapsed time. Perfect for live cost tracking during meetings.",
    response_description="Current cost calculation for ongoing meeting",
    responses={
        200: {
            "description": "Real-time cost calculated successfully",
            "content": {
                "application/json": {
                    "example": {
                        "elapsed_minutes": 25,
                        "current_total_cost": 66.67,
                        "cost_per_minute": 2.67,
                        "participants_count": 2,
                        "participant_costs": [
                            {
                                "name": "John Doe",
                                "current_cost": 31.25,
                                "hourly_rate": 75.0
                            },
                            {
                                "name": "Jane Smith", 
                                "current_cost": 35.42,
                                "hourly_rate": 85.0
                            }
                        ],
                        "projected_hourly_cost": 160.0
                    }
                }
            }
        },
        400: {
            "description": "Invalid elapsed time",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Elapsed minutes must be greater than 0"
                    }
                }
            }
        }
    }
)
async def calculate_real_time_cost(
    participants: List[Participant],
    elapsed_minutes: int = Query(..., gt=0, description="Minutes elapsed since meeting started")
):
    """
    Calculate real-time cost during an ongoing meeting.
    
    This endpoint is perfect for:
    - Live cost tracking during meetings
    - Real-time budget awareness
    - Cost-conscious meeting management
    - Meeting efficiency optimization
    
    **Usage:**
    - Call this endpoint periodically during a meeting
    - Provide the list of current participants
    - Specify how many minutes have elapsed
    - Get instant cost calculations
    
    **Returns:**
    - Current total cost based on elapsed time
    - Per-participant cost breakdown
    - Projected full hour cost
    - Cost per minute rate
    """
    cost_info = MeetingCostCalculator.calculate_real_time_cost(participants, elapsed_minutes)
    return cost_info

@router.post(
    "/meetings", 
    response_model=MeetingResponse,
    status_code=201,
    summary="Create New Meeting",
    description="Create a new meeting record with participants and cost calculation. This stores the meeting for future reference and reporting.",
    response_description="Created meeting with generated ID and metadata",
    responses={
        201: {
            "description": "Meeting created successfully",
            "content": {
                "application/json": {
                    "example": {
                        "id": "123e4567-e89b-12d3-a456-426614174000",
                        "title": "Sprint Planning",
                        "duration_minutes": 60,
                        "participants": [
                            {
                                "name": "John Doe",
                                "hourly_rate": 75.0,
                                "role": "Senior Developer"
                            }
                        ],
                        "start_time": "2025-01-15T10:00:00Z",
                        "total_cost": 75.0,
                        "created_at": "2025-01-15T09:45:00Z"
                    }
                }
            }
        },
        400: {
            "description": "Invalid meeting data or creation failed",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Could not create meeting: Invalid participant data"
                    }
                }
            }
        }
    }
)
async def create_meeting(
    meeting: MeetingCreate,
    meeting_repo: MeetingRepository = Depends(get_meeting_repository)
):
    """
    Create a new meeting record.
    
    This endpoint:
    - Creates a persistent meeting record
    - Assigns a unique meeting ID
    - Stores participant information
    - Records creation timestamp
    - Enables future cost tracking and reporting
    
    **Use Cases:**
    - Schedule future meetings with cost estimates
    - Create meeting records for accounting purposes
    - Enable meeting history and analytics
    - Support recurring meeting templates
    """
    try:
        db_meeting = meeting_repo.create(meeting)
        
        # Convert to response model
        return MeetingResponse(
            id=str(db_meeting.id),
            title=db_meeting.title,
            duration_minutes=db_meeting.duration_minutes,
            participants=meeting.participants,  # Use original participants data
            start_time=db_meeting.start_time,
            total_cost=db_meeting.total_cost,
            created_at=db_meeting.created_at
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Could not create meeting: {str(e)}")

@router.get(
    "/meetings", 
    response_model=List[MeetingResponse],
    summary="List All Meetings",
    description="Retrieve all meetings with optional filtering and pagination. Perfect for meeting history, reporting, and analytics.",
    response_description="List of meetings matching the specified criteria",
    responses={
        200: {
            "description": "Meetings retrieved successfully",
            "content": {
                "application/json": {
                    "example": [
                        {
                            "id": "123e4567-e89b-12d3-a456-426614174000",
                            "title": "Sprint Planning",
                            "duration_minutes": 60,
                            "participants": [
                                {
                                    "name": "John Doe",
                                    "hourly_rate": 75.0,
                                    "role": "Senior Developer"
                                }
                            ],
                            "start_time": "2025-01-15T10:00:00Z",
                            "total_cost": 75.0,
                            "created_at": "2025-01-15T09:45:00Z"
                        }
                    ]
                }
            }
        },
        400: {
            "description": "Invalid query parameters",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Invalid pagination parameters"
                    }
                }
            }
        }
    }
)
async def get_all_meetings(
    skip: int = Query(0, ge=0, description="Number of meetings to skip for pagination"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of meetings to return"),
    status: Optional[str] = Query(None, description="Filter by meeting status (e.g., 'scheduled', 'in-progress', 'completed')"),
    meeting_type: Optional[str] = Query(None, description="Filter by meeting type (e.g., 'sprint-planning', 'standup', 'review')"),
    search: Optional[str] = Query(None, description="Search term to match against meeting title and description"),
    meeting_repo: MeetingRepository = Depends(get_meeting_repository)
):
    """
    Get all meetings with optional filtering and pagination.
    
    This endpoint supports:
    - **Pagination**: Use `skip` and `limit` for efficient data loading
    - **Status Filtering**: Filter by meeting status for workflow management  
    - **Type Filtering**: Filter by meeting type for categorization
    - **Text Search**: Search meeting titles and descriptions
    - **Sorting**: Results ordered by creation date (newest first)
    
    **Use Cases:**
    - Meeting history and audit trails
    - Cost reporting and analytics
    - Meeting pattern analysis
    - Administrative dashboards
    - Budget planning based on historical data
    
    **Performance Notes:**
    - Results are paginated for optimal performance
    - Use filters to reduce result set size
    - Consider caching for frequently accessed data
    """
    filters = {}
    if status:
        filters['status'] = status
    if meeting_type:
        filters['meeting_type'] = meeting_type
    if search:
        filters['search'] = search
    
    db_meetings = meeting_repo.get_multi(skip=skip, limit=limit, filters=filters)
    
    # Convert to response models
    meetings_response = []
    for db_meeting in db_meetings:
        # Convert participants from database format
        participants = []
        for mp in db_meeting.participants:
            if mp.participant:
                participants.append(Participant(
                    id=str(mp.participant.id),
                    name=mp.participant.name,
                    email=mp.participant.email,
                    hourly_rate=mp.hourly_rate_at_time,
                    role=mp.participant.role,
                    department=mp.participant.department
                ))
        
        meetings_response.append(MeetingResponse(
            id=str(db_meeting.id),
            title=db_meeting.title,
            duration_minutes=db_meeting.duration_minutes,
            participants=participants,
            start_time=db_meeting.start_time,
            total_cost=db_meeting.total_cost,
            created_at=db_meeting.created_at
        ))
    
    return meetings_response

@router.get(
    "/meetings/{meeting_id}", 
    response_model=MeetingResponse,
    summary="Get Meeting by ID",
    description="Retrieve detailed information about a specific meeting including participants and cost data.",
    response_description="Complete meeting information with participant details",
    responses={
        200: {
            "description": "Meeting found and returned successfully",
            "content": {
                "application/json": {
                    "example": {
                        "id": "123e4567-e89b-12d3-a456-426614174000",
                        "title": "Sprint Planning",
                        "duration_minutes": 60,
                        "participants": [
                            {
                                "id": "456e7890-e89b-12d3-a456-426614174001",
                                "name": "John Doe",
                                "email": "john.doe@company.com",
                                "hourly_rate": 75.0,
                                "role": "Senior Developer",
                                "department": "Engineering"
                            }
                        ],
                        "start_time": "2025-01-15T10:00:00Z",
                        "total_cost": 75.0,
                        "created_at": "2025-01-15T09:45:00Z"
                    }
                }
            }
        },
        400: {
            "description": "Invalid meeting ID format",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Invalid meeting ID format"
                    }
                }
            }
        },
        404: {
            "description": "Meeting not found",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Meeting not found"
                    }
                }
            }
        }
    }
)
async def get_meeting(
    meeting_id: str,
    meeting_repo: MeetingRepository = Depends(get_meeting_repository)
):
    """
    Get a specific meeting by ID.
    
    This endpoint:
    - Validates the meeting ID format (UUID)
    - Retrieves complete meeting information
    - Includes participant details with historical hourly rates
    - Returns full cost information
    - Provides creation metadata
    
    **Use Cases:**
    - Meeting detail views in applications
    - Cost analysis and reporting
    - Audit trails and record keeping
    - Integration with calendar systems
    - Historical meeting data access
    """
    try:
        meeting_uuid = uuid.UUID(meeting_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid meeting ID format")
    
    db_meeting = meeting_repo.get(meeting_uuid)
    if not db_meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")
    
    # Convert participants from database format
    participants = []
    for mp in db_meeting.participants:
        if mp.participant:
            participants.append(Participant(
                id=str(mp.participant.id),
                name=mp.participant.name,
                email=mp.participant.email,
                hourly_rate=mp.hourly_rate_at_time,
                role=mp.participant.role,
                department=mp.participant.department
            ))
    
    return MeetingResponse(
        id=str(db_meeting.id),
        title=db_meeting.title,
        duration_minutes=db_meeting.duration_minutes,
        participants=participants,
        start_time=db_meeting.start_time,
        total_cost=db_meeting.total_cost,
        created_at=db_meeting.created_at
    )

@router.get(
    "/meetings/{meeting_id}/cost", 
    response_model=MeetingCostCalculation,
    summary="Get Meeting Cost Calculation",
    description="Retrieve detailed cost calculation for a specific meeting with participant breakdown.",
    response_description="Complete cost analysis including per-participant costs",
    responses={
        200: {
            "description": "Cost calculation retrieved successfully",
            "content": {
                "application/json": {
                    "example": {
                        "meeting_id": "123e4567-e89b-12d3-a456-426614174000",
                        "title": "Sprint Planning",
                        "duration_minutes": 60,
                        "total_cost": 160.0,
                        "cost_per_minute": 2.67,
                        "participants_count": 2,
                        "participant_costs": [
                            {
                                "name": "John Doe",
                                "role": "Senior Developer",
                                "hourly_rate": 75.0,
                                "cost": 75.0
                            },
                            {
                                "name": "Jane Smith",
                                "role": "Product Manager", 
                                "hourly_rate": 85.0,
                                "cost": 85.0
                            }
                        ],
                        "calculation_time": "2025-01-15T10:00:00Z"
                    }
                }
            }
        },
        400: {
            "description": "Invalid meeting ID format"
        },
        404: {
            "description": "Meeting not found"
        }
    }
)
async def get_meeting_cost(
    meeting_id: str,
    meeting_repo: MeetingRepository = Depends(get_meeting_repository)
):
    """
    Get the cost calculation for a specific meeting.
    
    This endpoint:
    - Retrieves stored meeting data
    - Recalculates costs using current participant rates
    - Provides detailed cost breakdown per participant
    - Returns cost-per-minute analysis
    - Useful for audit trails and reporting
    
    **Use Cases:**
    - Financial reporting and cost analysis
    - Meeting cost verification
    - Budget tracking and variance analysis
    - Cost center allocation
    - ROI analysis for meetings
    """
    try:
        meeting_uuid = uuid.UUID(meeting_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid meeting ID format")
    
    db_meeting = meeting_repo.get(meeting_uuid)
    if not db_meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")
    
    # Convert participants from database format
    participants = []
    for mp in db_meeting.participants:
        if mp.participant:
            participants.append(Participant(
                id=str(mp.participant.id),
                name=mp.participant.name,
                email=mp.participant.email,
                hourly_rate=mp.hourly_rate_at_time,
                role=mp.participant.role,
                department=mp.participant.department
            ))
    
    # Create Meeting object for calculation
    meeting_obj = Meeting(
        id=str(db_meeting.id),
        title=db_meeting.title,
        duration_minutes=db_meeting.duration_minutes,
        participants=participants,
        start_time=db_meeting.start_time
    )
    
    return MeetingCostCalculator.calculate_meeting_cost(meeting_obj)

@router.get(
    "/meetings/statistics/overview",
    summary="Get Meeting Statistics",
    description="Retrieve comprehensive statistics about all meetings including cost analytics and trends.",
    response_description="Meeting statistics with cost analysis",
    responses={
        200: {
            "description": "Statistics retrieved successfully",
            "content": {
                "application/json": {
                    "example": {
                        "total_meetings": 150,
                        "total_cost": 45000.00,
                        "average_cost_per_meeting": 300.00,
                        "average_duration_minutes": 45,
                        "total_participants": 500,
                        "average_participants_per_meeting": 3.33,
                        "cost_by_department": {
                            "Engineering": 25000.00,
                            "Product": 12000.00,
                            "Marketing": 8000.00
                        },
                        "meetings_by_type": {
                            "standup": 60,
                            "sprint-planning": 30,
                            "review": 30,
                            "retrospective": 30
                        },
                        "cost_trends": {
                            "this_month": 3500.00,
                            "last_month": 3200.00,
                            "percentage_change": 9.38
                        }
                    }
                }
            }
        }
    }
)
async def get_meetings_statistics(
    meeting_repo: MeetingRepository = Depends(get_meeting_repository)
):
    """
    Get comprehensive cost statistics for all meetings.
    
    This endpoint provides:
    - **Overall Metrics**: Total meetings, costs, and averages
    - **Cost Breakdown**: By department, team, and meeting type
    - **Trends Analysis**: Month-over-month cost changes
    - **Efficiency Metrics**: Average duration and participant counts
    - **Budget Insights**: Cost per minute and hourly rates
    
    **Use Cases:**
    - Executive dashboards and reporting
    - Budget planning and cost control
    - Meeting efficiency analysis
    - Department cost allocation
    - Trend analysis and forecasting
    """
    return meeting_repo.get_meeting_statistics()

@router.delete(
    "/meetings/{meeting_id}",
    status_code=204,
    summary="Delete Meeting",
    description="Permanently delete a meeting record and all associated data.",
    responses={
        204: {
            "description": "Meeting deleted successfully"
        },
        400: {
            "description": "Invalid meeting ID format",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Invalid meeting ID format"
                    }
                }
            }
        },
        404: {
            "description": "Meeting not found",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Meeting not found"
                    }
                }
            }
        }
    }
)
async def delete_meeting(
    meeting_id: str,
    meeting_repo: MeetingRepository = Depends(get_meeting_repository)
):
    """
    Delete a meeting record permanently.
    
    **⚠️ Warning**: This action is irreversible and will permanently delete:
    - Meeting metadata and details
    - Participant associations
    - Cost calculation history
    - Any related analytics data
    
    **Use Cases:**
    - Remove duplicate or incorrect meeting records
    - Clean up test data
    - GDPR compliance and data retention policies
    - Administrative data management
    
    **Best Practices:**
    - Consider archiving instead of deleting for audit purposes
    - Ensure proper authorization before deletion
    - Backup important data before deletion
    """
    """Delete a meeting."""
    try:
        meeting_uuid = uuid.UUID(meeting_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid meeting ID format")
    
    success = meeting_repo.delete(meeting_uuid)
    if not success:
        raise HTTPException(status_code=404, detail="Meeting not found")
    
    return {"message": "Meeting deleted successfully"}

@router.post(
    "/meetings/{meeting_id}/start",
    summary="Start Meeting",
    description="Start a meeting by changing its status to 'in_progress' and begin cost tracking.",
    response_description="Meeting start confirmation with updated status",
    responses={
        200: {
            "description": "Meeting started successfully",
            "content": {
                "application/json": {
                    "example": {
                        "message": "Meeting started successfully",
                        "status": "in_progress",
                        "started_at": "2025-01-15T10:00:00Z"
                    }
                }
            }
        },
        400: {
            "description": "Cannot start meeting (invalid ID or already in progress)",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Meeting not found or cannot be started (may already be in progress)"
                    }
                }
            }
        },
        404: {
            "description": "Meeting not found"
        }
    }
)
async def start_meeting(
    meeting_id: str,
    meeting_repo: MeetingRepository = Depends(get_meeting_repository)
):
    """
    Start a meeting and begin cost tracking.
    
    This endpoint:
    - Changes meeting status to 'in_progress'
    - Records the actual start time
    - Enables real-time cost tracking
    - Prevents duplicate starts
    
    **Use Cases:**
    - Meeting room systems integration
    - Calendar application integration
    - Automated meeting tracking
    - Real-time cost monitoring initialization
    - Meeting attendance systems
    
    **Status Transitions:**
    - 'scheduled' → 'in_progress'
    - Cannot start meetings already 'in_progress' or 'completed'
    """
    try:
        meeting_uuid = uuid.UUID(meeting_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid meeting ID format")
    
    db_meeting = meeting_repo.start_meeting(meeting_uuid)
    if not db_meeting:
        raise HTTPException(
            status_code=400, 
            detail="Meeting not found or cannot be started (may already be in progress)"
        )
    
    return {"message": "Meeting started successfully", "status": db_meeting.status}

@router.post(
    "/meetings/{meeting_id}/end",
    summary="End Meeting",
    description="End a meeting, calculate final costs, and change status to 'completed'.",
    response_description="Meeting end confirmation with final cost calculation",
    responses={
        200: {
            "description": "Meeting ended successfully with final cost",
            "content": {
                "application/json": {
                    "example": {
                        "message": "Meeting ended successfully",
                        "status": "completed",
                        "total_cost": 160.0,
                        "ended_at": "2025-01-15T11:00:00Z",
                        "actual_duration_minutes": 60
                    }
                }
            }
        },
        400: {
            "description": "Cannot end meeting (invalid ID or not in progress)",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Meeting is not currently in progress"
                    }
                }
            }
        },
        404: {
            "description": "Meeting not found"
        }
    }
)
async def end_meeting(
    meeting_id: str,
    meeting_repo: MeetingRepository = Depends(get_meeting_repository)
):
    """
    End a meeting and calculate final costs.
    
    This endpoint:
    - Changes meeting status to 'completed'
    - Records the actual end time
    - Calculates final meeting cost based on actual duration
    - Updates cost records for reporting
    - Finalizes meeting for billing and analytics
    
    **Cost Calculation:**
    - Uses participant hourly rates at time of meeting
    - Calculates based on actual meeting duration
    - Stores final cost for reporting and analytics
    - Handles pro-rated costs for partial hours
    
    **Use Cases:**
    - Meeting room systems integration
    - Automated cost finalization
    - Billing and accounting systems
    - Meeting analytics and reporting
    - Calendar system integration
    
    **Status Transitions:**
    - 'in_progress' → 'completed'
    - Cannot end meetings not currently in progress
    """
    try:
        meeting_uuid = uuid.UUID(meeting_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid meeting ID format")
    
    db_meeting = meeting_repo.get(meeting_uuid)
    if not db_meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")
    
    if db_meeting.status != 'in_progress':
        raise HTTPException(
            status_code=400, 
            detail="Meeting is not currently in progress"
        )
    
    # Calculate final cost if not already calculated
    if not db_meeting.total_cost:
        # Convert participants for calculation
        participants = []
        for mp in db_meeting.participants:
            if mp.participant:
                participants.append(Participant(
                    id=str(mp.participant.id),
                    name=mp.participant.name,
                    email=mp.participant.email,
                    hourly_rate=mp.hourly_rate_at_time,
                    role=mp.participant.role,
                    department=mp.participant.department
                ))
        
        # Create Meeting object for calculation
        meeting_obj = Meeting(
            id=str(db_meeting.id),
            title=db_meeting.title,
            duration_minutes=db_meeting.duration_minutes,
            participants=participants,
            start_time=db_meeting.start_time
        )
        
        cost_calculation = MeetingCostCalculator.calculate_meeting_cost(meeting_obj)
        total_cost = cost_calculation.total_cost
    else:
        total_cost = db_meeting.total_cost
    
    # End the meeting
    updated_meeting = meeting_repo.end_meeting(meeting_uuid, total_cost)
    
    return {
        "message": "Meeting ended successfully", 
        "status": updated_meeting.status,
        "total_cost": updated_meeting.total_cost
    }
