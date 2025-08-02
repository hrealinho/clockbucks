from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from src.models.participant import Participant

class Meeting(BaseModel):
    id: Optional[str] = None
    title: str = Field(..., min_length=1, description="Meeting title")
    duration_minutes: int = Field(..., gt=0, description="Meeting duration in minutes")
    participants: List[Participant] = Field(..., min_items=1, description="List of meeting participants")
    start_time: Optional[datetime] = Field(None, description="Meeting start time")
    end_time: Optional[datetime] = Field(None, description="Meeting end time")
    
    class Config:
        json_schema_extra = {
            "example": {
                "title": "Sprint Planning",
                "duration_minutes": 60,
                "participants": [
                    {
                        "name": "John Doe",
                        "hourly_rate": 75.0,
                        "role": "Senior Developer"
                    },
                    {
                        "name": "Jane Smith", 
                        "hourly_rate": 85.0,
                        "role": "Product Manager"
                    }
                ],
                "start_time": "2025-01-15T10:00:00Z"
            }
        }

class MeetingCreate(BaseModel):
    title: str = Field(..., min_length=1)
    duration_minutes: int = Field(..., gt=0)
    participants: List[Participant] = Field(..., min_items=1)
    start_time: Optional[datetime] = None

class MeetingCostCalculation(BaseModel):
    meeting_id: str
    title: str
    duration_minutes: int
    total_cost: float = Field(..., description="Total cost of the meeting in USD")
    cost_per_minute: float = Field(..., description="Cost per minute in USD")
    participants_count: int
    participant_costs: List[dict] = Field(..., description="Individual participant costs")
    calculation_time: datetime

class MeetingResponse(Meeting):
    id: str
    total_cost: Optional[float] = None
    created_at: datetime
