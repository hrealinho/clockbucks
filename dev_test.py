"""
Development script with sample data for testing the Clock Bucks API.
"""
import sys
sys.path.append('.')

from pydantic import BaseModel
from typing import Optional
from datetime import datetime

# Simple participant model for testing
class SimpleParticipant(BaseModel):
    name: str
    hourly_rate: float
    role: Optional[str] = None

# Simple meeting model for testing  
class SimpleMeeting(BaseModel):
    id: Optional[str] = None
    title: str
    duration_minutes: int
    participants: list[SimpleParticipant]
    start_time: Optional[datetime] = None

def create_sample_participants():
    """Create sample participants for testing."""
    return [
        SimpleParticipant(
            name="Alice Johnson",
            hourly_rate=95.0,
            role="Senior Product Manager"
        ),
        SimpleParticipant(
            name="Bob Smith",
            hourly_rate=85.0,
            role="Senior Developer"
        ),
        SimpleParticipant(
            name="Carol Davis",
            hourly_rate=75.0,
            role="UX Designer"
        ),
        SimpleParticipant(
            name="David Wilson",
            hourly_rate=70.0,
            role="QA Engineer"
        ),
        SimpleParticipant(
            name="Eva Brown",
            hourly_rate=90.0,
            role="DevOps Engineer"
        )
    ]

def create_sample_meetings():
    """Create sample meetings for testing."""
    participants = create_sample_participants()
    
    return [
        SimpleMeeting(
            id="meeting-1",
            title="Sprint Planning",
            duration_minutes=90,
            participants=participants[:4],  # 4 participants
            start_time=datetime(2025, 1, 15, 10, 0)
        ),
        SimpleMeeting(
            id="meeting-2", 
            title="Daily Standup",
            duration_minutes=15,
            participants=participants[:3],  # 3 participants
            start_time=datetime(2025, 1, 16, 9, 0)
        ),
        SimpleMeeting(
            id="meeting-3",
            title="Architecture Review",
            duration_minutes=120,
            participants=[participants[0], participants[1], participants[4]],  # 3 participants
            start_time=datetime(2025, 1, 17, 14, 0)
        ),
        SimpleMeeting(
            id="meeting-4",
            title="Retrospective",
            duration_minutes=60,
            participants=participants,  # All 5 participants
            start_time=datetime(2025, 1, 18, 16, 0)
        )
    ]

# Simple calculator class for testing
class SimpleMeetingCostCalculator:
    @staticmethod
    def calculate_meeting_cost(meeting):
        """Calculate the total cost of a meeting."""
        participant_costs = []
        total_cost = 0.0
        
        for participant in meeting.participants:
            participant_hours = meeting.duration_minutes / 60.0
            participant_cost = participant.hourly_rate * participant_hours
            
            participant_costs.append({
                "name": participant.name,
                "role": participant.role,
                "hourly_rate": participant.hourly_rate,
                "hours": participant_hours,
                "cost": round(participant_cost, 2)
            })
            
            total_cost += participant_cost
        
        cost_per_minute = total_cost / meeting.duration_minutes if meeting.duration_minutes > 0 else 0
        
        return {
            "meeting_id": meeting.id or "temp",
            "title": meeting.title,
            "duration_minutes": meeting.duration_minutes,
            "total_cost": round(total_cost, 2),
            "cost_per_minute": round(cost_per_minute, 2),
            "participants_count": len(meeting.participants),
            "participant_costs": participant_costs
        }
    
    @staticmethod
    def calculate_real_time_cost(participants, elapsed_minutes):
        """Calculate real-time cost during an ongoing meeting."""
        if elapsed_minutes <= 0:
            return {
                "elapsed_minutes": 0,
                "current_total_cost": 0.0,
                "cost_per_minute": 0.0,
                "projected_hourly_cost": 0.0
            }
        
        total_hourly_rate = sum(p.hourly_rate for p in participants)
        elapsed_hours = elapsed_minutes / 60.0
        current_total_cost = total_hourly_rate * elapsed_hours
        cost_per_minute = total_hourly_rate / 60.0
        
        return {
            "elapsed_minutes": elapsed_minutes,
            "current_total_cost": round(current_total_cost, 2),
            "cost_per_minute": round(cost_per_minute, 2),
            "projected_hourly_cost": round(total_hourly_rate, 2)
        }
    
    @staticmethod
    def get_cost_statistics(meetings):
        """Generate cost statistics for a list of meetings."""
        if not meetings:
            return {
                "total_meetings": 0,
                "total_cost": 0.0,
                "average_cost_per_meeting": 0.0,
                "average_duration_minutes": 0.0,
                "total_hours": 0.0
            }
        
        total_cost = 0.0
        total_duration = 0
        
        for meeting in meetings:
            calculation = SimpleMeetingCostCalculator.calculate_meeting_cost(meeting)
            total_cost += calculation["total_cost"]
            total_duration += meeting.duration_minutes
        
        average_cost = total_cost / len(meetings)
        average_duration = total_duration / len(meetings)
        total_hours = total_duration / 60.0
        
        return {
            "total_meetings": len(meetings),
            "total_cost": round(total_cost, 2),
            "average_cost_per_meeting": round(average_cost, 2),
            "average_duration_minutes": round(average_duration, 1),
            "total_hours": round(total_hours, 2)
        }

def test_calculator():
    """Test the meeting cost calculator with sample data."""
    print("🕒 Clock Bucks - Meeting Cost Calculator Test")
    print("=" * 50)
    
    meetings = create_sample_meetings()
    
    for i, meeting in enumerate(meetings, 1):
        print(f"\n📅 Meeting {i}: {meeting.title}")
        print(f"⏱️  Duration: {meeting.duration_minutes} minutes")
        print(f"👥 Participants: {len(meeting.participants)}")
        
        # Calculate cost
        cost_calculation = SimpleMeetingCostCalculator.calculate_meeting_cost(meeting)
        
        print(f"💰 Total Cost: ${cost_calculation['total_cost']}")
        print(f"💸 Cost per minute: ${cost_calculation['cost_per_minute']}")
        
        print("\n📊 Participant Breakdown:")
        for participant_cost in cost_calculation['participant_costs']:
            print(f"  • {participant_cost['name']} ({participant_cost['role']}): ${participant_cost['cost']}")
    
    # Test statistics
    print(f"\n📈 Overall Statistics:")
    stats = SimpleMeetingCostCalculator.get_cost_statistics(meetings)
    print(f"  • Total meetings: {stats['total_meetings']}")
    print(f"  • Total cost: ${stats['total_cost']}")
    print(f"  • Average cost per meeting: ${stats['average_cost_per_meeting']}")
    print(f"  • Average duration: {stats['average_duration_minutes']} minutes")
    print(f"  • Total hours: {stats['total_hours']} hours")
    
    # Test real-time calculation
    print(f"\n⏰ Real-time Cost Example (30 minutes elapsed):")
    participants = create_sample_participants()[:3]
    real_time = SimpleMeetingCostCalculator.calculate_real_time_cost(participants, 30)
    print(f"  • Current cost: ${real_time['current_total_cost']}")
    print(f"  • Cost per minute: ${real_time['cost_per_minute']}")
    print(f"  • Projected hourly cost: ${real_time['projected_hourly_cost']}")

if __name__ == "__main__":
    test_calculator()
