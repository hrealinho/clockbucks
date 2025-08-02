"""
Development script with sample data for testing the Clock Bucks API.
"""
import asyncio
import json
from src.models.participant import Participant
from src.models.meeting import Meeting
from src.services.calculator import MeetingCostCalculator
from datetime import datetime

def create_sample_participants():
    """Create sample participants for testing."""
    return [
        Participant(
            name="Alice Johnson",
            hourly_rate=95.0,
            role="Senior Product Manager"
        ),
        Participant(
            name="Bob Smith",
            hourly_rate=85.0,
            role="Senior Developer"
        ),
        Participant(
            name="Carol Davis",
            hourly_rate=75.0,
            role="UX Designer"
        ),
        Participant(
            name="David Wilson",
            hourly_rate=70.0,
            role="QA Engineer"
        ),
        Participant(
            name="Eva Brown",
            hourly_rate=90.0,
            role="DevOps Engineer"
        )
    ]

def create_sample_meetings():
    """Create sample meetings for testing."""
    participants = create_sample_participants()
    
    return [
        Meeting(
            id="meeting-1",
            title="Sprint Planning",
            duration_minutes=90,
            participants=participants[:4],  # 4 participants
            start_time=datetime(2025, 1, 15, 10, 0)
        ),
        Meeting(
            id="meeting-2", 
            title="Daily Standup",
            duration_minutes=15,
            participants=participants[:3],  # 3 participants
            start_time=datetime(2025, 1, 16, 9, 0)
        ),
        Meeting(
            id="meeting-3",
            title="Architecture Review",
            duration_minutes=120,
            participants=[participants[0], participants[1], participants[4]],  # 3 participants
            start_time=datetime(2025, 1, 17, 14, 0)
        ),
        Meeting(
            id="meeting-4",
            title="Retrospective",
            duration_minutes=60,
            participants=participants,  # All 5 participants
            start_time=datetime(2025, 1, 18, 16, 0)
        )
    ]

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
        cost_calculation = MeetingCostCalculator.calculate_meeting_cost(meeting)
        
        print(f"💰 Total Cost: ${cost_calculation.total_cost}")
        print(f"💸 Cost per minute: ${cost_calculation.cost_per_minute}")
        
        print("\n📊 Participant Breakdown:")
        for participant_cost in cost_calculation.participant_costs:
            print(f"  • {participant_cost['name']} ({participant_cost['role']}): ${participant_cost['cost']}")
    
    # Test statistics
    print(f"\n📈 Overall Statistics:")
    stats = MeetingCostCalculator.get_cost_statistics(meetings)
    print(f"  • Total meetings: {stats['total_meetings']}")
    print(f"  • Total cost: ${stats['total_cost']}")
    print(f"  • Average cost per meeting: ${stats['average_cost_per_meeting']}")
    print(f"  • Average duration: {stats['average_duration_minutes']} minutes")
    print(f"  • Total hours: {stats['total_hours']} hours")
    
    # Test real-time calculation
    print(f"\n⏰ Real-time Cost Example (30 minutes elapsed):")
    participants = create_sample_participants()[:3]
    real_time = MeetingCostCalculator.calculate_real_time_cost(participants, 30)
    print(f"  • Current cost: ${real_time['current_total_cost']}")
    print(f"  • Cost per minute: ${real_time['cost_per_minute']}")
    print(f"  • Projected hourly cost: ${real_time['projected_hourly_cost']}")

if __name__ == "__main__":
    test_calculator()
