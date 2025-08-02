from typing import List
from datetime import datetime
from src.models.meeting import Meeting, MeetingCostCalculation
from src.models.participant import Participant

class MeetingCostCalculator:
    """Service class for calculating meeting costs based on participant salaries."""
    
    @staticmethod
    def calculate_meeting_cost(meeting: Meeting) -> MeetingCostCalculation:
        """
        Calculate the total cost of a meeting based on participant hourly rates and duration.
        
        Args:
            meeting: Meeting object containing participants and duration
            
        Returns:
            MeetingCostCalculation with detailed cost breakdown
        """
        participant_costs = []
        total_cost = 0.0
        
        # Calculate cost for each participant
        for participant in meeting.participants:
            # Convert minutes to hours for calculation
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
        
        # Calculate cost per minute
        cost_per_minute = total_cost / meeting.duration_minutes if meeting.duration_minutes > 0 else 0
        
        return MeetingCostCalculation(
            meeting_id=meeting.id or "temp",
            title=meeting.title,
            duration_minutes=meeting.duration_minutes,
            total_cost=round(total_cost, 2),
            cost_per_minute=round(cost_per_minute, 2),
            participants_count=len(meeting.participants),
            participant_costs=participant_costs,
            calculation_time=datetime.now()
        )
    
    @staticmethod
    def calculate_real_time_cost(participants: List[Participant], elapsed_minutes: int) -> dict:
        """
        Calculate real-time cost during an ongoing meeting.
        
        Args:
            participants: List of meeting participants
            elapsed_minutes: Minutes elapsed since meeting started
            
        Returns:
            Dictionary with current cost information
        """
        if elapsed_minutes <= 0:
            return {
                "elapsed_minutes": 0,
                "current_total_cost": 0.0,
                "cost_per_minute": 0.0,
                "projected_hourly_cost": 0.0
            }
        
        # Calculate total hourly rate
        total_hourly_rate = sum(p.hourly_rate for p in participants)
        
        # Calculate current cost based on elapsed time
        elapsed_hours = elapsed_minutes / 60.0
        current_total_cost = total_hourly_rate * elapsed_hours
        
        # Calculate cost per minute
        cost_per_minute = total_hourly_rate / 60.0
        
        return {
            "elapsed_minutes": elapsed_minutes,
            "current_total_cost": round(current_total_cost, 2),
            "cost_per_minute": round(cost_per_minute, 2),
            "projected_hourly_cost": round(total_hourly_rate, 2)
        }
    
    @staticmethod
    def get_cost_statistics(meetings: List[Meeting]) -> dict:
        """
        Generate cost statistics for a list of meetings.
        
        Args:
            meetings: List of meetings to analyze
            
        Returns:
            Dictionary with cost statistics
        """
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
            calculation = MeetingCostCalculator.calculate_meeting_cost(meeting)
            total_cost += calculation.total_cost
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
