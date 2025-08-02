from fastapi import APIRouter, HTTPException
from typing import List
from datetime import datetime
import uuid

from src.models.participant import Participant, ParticipantCreate, ParticipantResponse

router = APIRouter()

# In-memory storage for demonstration (use a database in production)
participants_db = {}

@router.post(
    "/participants", 
    response_model=ParticipantResponse,
    status_code=201,
    summary="Create New Participant",
    description="Create a new participant with their role and hourly rate information for meeting cost calculations.",
    response_description="Created participant with generated ID and metadata",
    responses={
        201: {
            "description": "Participant created successfully",
            "content": {
                "application/json": {
                    "example": {
                        "id": "456e7890-e89b-12d3-a456-426614174001",
                        "name": "John Doe",
                        "email": "john.doe@company.com",
                        "hourly_rate": 75.0,
                        "role": "Senior Developer",
                        "department": "Engineering",
                        "created_at": "2025-01-15T09:30:00Z"
                    }
                }
            }
        },
        400: {
            "description": "Invalid participant data",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Hourly rate must be greater than 0"
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
                                "loc": ["body", "name"],
                                "msg": "ensure this value has at least 1 characters",
                                "type": "value_error.any_str.min_length"
                            }
                        ]
                    }
                }
            }
        }
    }
)
async def create_participant(participant: ParticipantCreate):
    """
    Create a new participant for meeting cost calculations.
    
    This endpoint:
    - Creates a persistent participant record
    - Assigns a unique participant ID
    - Stores role and hourly rate information
    - Records creation timestamp
    - Enables participant reuse across multiple meetings
    
    **Use Cases:**
    - Employee onboarding for cost tracking
    - Contractor rate management
    - Team member cost profile setup
    - Meeting planning and cost estimation
    - Department budget planning
    
    **Rate Management:**
    - Hourly rates are used for all cost calculations
    - Rates can be updated as needed
    - Historical rates are preserved in meeting records
    """
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

@router.get(
    "/participants", 
    response_model=List[ParticipantResponse],
    summary="List All Participants",
    description="Retrieve all participants with their current hourly rates and role information.",
    response_description="List of all participants in the system",
    responses={
        200: {
            "description": "Participants retrieved successfully",
            "content": {
                "application/json": {
                    "example": [
                        {
                            "id": "456e7890-e89b-12d3-a456-426614174001",
                            "name": "John Doe",
                            "email": "john.doe@company.com",
                            "hourly_rate": 75.0,
                            "role": "Senior Developer",
                            "department": "Engineering",
                            "created_at": "2025-01-15T09:30:00Z"
                        },
                        {
                            "id": "789f0123-e89b-12d3-a456-426614174002",
                            "name": "Jane Smith",
                            "email": "jane.smith@company.com",
                            "hourly_rate": 85.0,
                            "role": "Product Manager",
                            "department": "Product",
                            "created_at": "2025-01-14T14:20:00Z"
                        }
                    ]
                }
            }
        }
    }
)
async def get_all_participants():
    """
    Get all participants in the system.
    
    This endpoint:
    - Returns complete participant directory
    - Includes current hourly rates and roles
    - Provides participant IDs for meeting creation
    - Shows department and contact information
    - Enables participant selection for meetings
    
    **Use Cases:**
    - Meeting planning and participant selection
    - Team cost analysis and budgeting
    - HR and administrative management
    - Rate comparison and analysis
    - Participant directory for applications
    
    **Data Includes:**
    - Unique participant identifiers
    - Contact information (name, email)
    - Current hourly rates
    - Role and department information
    - Account creation timestamps
    """
    return list(participants_db.values())

@router.get(
    "/participants/{participant_id}", 
    response_model=ParticipantResponse,
    summary="Get Participant by ID",
    description="Retrieve detailed information about a specific participant including their current hourly rate and role.",
    response_description="Complete participant information",
    responses={
        200: {
            "description": "Participant found and returned successfully",
            "content": {
                "application/json": {
                    "example": {
                        "id": "456e7890-e89b-12d3-a456-426614174001",
                        "name": "John Doe",
                        "email": "john.doe@company.com",
                        "hourly_rate": 75.0,
                        "role": "Senior Developer",
                        "department": "Engineering",
                        "created_at": "2025-01-15T09:30:00Z"
                    }
                }
            }
        },
        404: {
            "description": "Participant not found",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Participant not found"
                    }
                }
            }
        }
    }
)
async def get_participant(participant_id: str):
    """
    Get detailed information about a specific participant.
    
    This endpoint:
    - Retrieves complete participant profile
    - Shows current hourly rate and role information
    - Provides contact and department details
    - Includes account creation history
    - Validates participant existence
    
    **Use Cases:**
    - Participant profile views
    - Rate verification for meetings
    - HR and administrative lookup
    - Meeting planning validation
    - Cost calculation verification
    """
    if participant_id not in participants_db:
        raise HTTPException(status_code=404, detail="Participant not found")
    
    return participants_db[participant_id]

@router.put(
    "/participants/{participant_id}", 
    response_model=ParticipantResponse,
    summary="Update Participant",
    description="Update participant information including hourly rate, role, and contact details.",
    response_description="Updated participant information",
    responses={
        200: {
            "description": "Participant updated successfully",
            "content": {
                "application/json": {
                    "example": {
                        "id": "456e7890-e89b-12d3-a456-426614174001",
                        "name": "John Doe",
                        "email": "john.doe@company.com",
                        "hourly_rate": 85.0,
                        "role": "Lead Developer",
                        "department": "Engineering",
                        "created_at": "2025-01-15T09:30:00Z"
                    }
                }
            }
        },
        404: {
            "description": "Participant not found",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Participant not found"
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
                                "loc": ["body", "hourly_rate"],
                                "msg": "ensure this value is greater than 0",
                                "type": "value_error.number.not_gt"
                            }
                        ]
                    }
                }
            }
        }
    }
)
async def update_participant(participant_id: str, participant: ParticipantCreate):
    """
    Update an existing participant's information.
    
    This endpoint:
    - Updates participant profile information
    - Modifies hourly rates for future meetings
    - Updates role and department information
    - Preserves original creation timestamp
    - Validates all input data
    
    **Important Notes:**
    - Rate changes affect future meetings only
    - Historical meeting costs remain unchanged
    - All fields are required (partial updates not supported)
    - Contact information can be updated
    
    **Use Cases:**
    - Salary/rate adjustments and promotions
    - Role changes and reorganizations
    - Contact information updates
    - Department transfers
    - Hourly rate corrections
    
    **Rate History:**
    - Previous rates are preserved in existing meeting records
    - New rate applies to future meetings only
    - Ensures accurate historical cost reporting
    """
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

@router.delete(
    "/participants/{participant_id}",
    status_code=204,
    summary="Delete Participant",
    description="Permanently delete a participant record. Use with caution as this may affect historical meeting data.",
    responses={
        204: {
            "description": "Participant deleted successfully"
        },
        404: {
            "description": "Participant not found",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Participant not found"
                    }
                }
            }
        },
        409: {
            "description": "Cannot delete participant (has associated meetings)",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Cannot delete participant with existing meeting records"
                    }
                }
            }
        }
    }
)
async def delete_participant(participant_id: str):
    """
    Delete a participant record permanently.
    
    **⚠️ Warning**: This action is irreversible and may affect:
    - Historical meeting cost calculations
    - Participant associations in existing meetings
    - Analytics and reporting data
    - Audit trails and cost records
    
    **Recommendations:**
    - Consider deactivating instead of deleting
    - Ensure no active meetings reference this participant
    - Backup data before deletion for compliance
    - Check for dependencies in related systems
    
    **Use Cases:**
    - Remove duplicate or test participant records
    - Clean up data for ex-employees (with caution)
    - GDPR compliance and data retention policies
    - Administrative data management
    
    **Best Practices:**
    - Archive participant data instead of deletion
    - Use soft deletes to preserve historical references
    - Implement proper authorization for deletions
    - Log deletion activities for audit purposes
    """
    if participant_id not in participants_db:
        raise HTTPException(status_code=404, detail="Participant not found")
    
    del participants_db[participant_id]
    return {"message": "Participant deleted successfully"}
