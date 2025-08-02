# Development Testing Script (dev_test.py)

This script provides a quick way to test the Clock Bucks meeting cost calculation logic with realistic sample data, without needing to start the full API server or make HTTP requests.

## 🎯 Purpose

The `dev_test.py` script is designed to:
- **Validate Calculator Logic**: Test the core meeting cost calculation algorithms
- **Demo Functionality**: Show how the cost calculator works with realistic data
- **Quick Development Testing**: Rapidly test changes to the calculation logic
- **Sample Data Generation**: Provide realistic test data for development

## 🚀 Usage

### Basic Run
```bash
python dev_test.py
```

### What It Tests

1. **Sample Participants**: Creates 5 realistic participants with different roles and hourly rates:
   - Alice Johnson (Product Manager) - $95/hour
   - Bob Smith (Senior Developer) - $85/hour  
   - Carol Davis (UX Designer) - $75/hour
   - David Wilson (QA Engineer) - $70/hour
   - Eva Brown (DevOps Engineer) - $90/hour

2. **Sample Meetings**: Tests 4 different meeting scenarios:
   - **Sprint Planning** (90 min, 4 participants) 
   - **Daily Standup** (15 min, 3 participants)
   - **Architecture Review** (120 min, 3 participants)
   - **Retrospective** (60 min, 5 participants)

3. **Calculations Performed**:
   - Individual meeting costs
   - Cost per minute for each meeting
   - Participant-level cost breakdown
   - Overall statistics across all meetings
   - Real-time cost calculation simulation

## 📊 Sample Output

```
🕒 Clock Bucks - Meeting Cost Calculator Test
==================================================

📅 Meeting 1: Sprint Planning
⏱️  Duration: 90 minutes
👥 Participants: 4
💰 Total Cost: $487.50
💸 Cost per minute: $5.42

📊 Participant Breakdown:
  • Alice Johnson (Senior Product Manager): $142.50
  • Bob Smith (Senior Developer): $127.50
  • Carol Davis (UX Designer): $112.50
  • David Wilson (QA Engineer): $105.00

📅 Meeting 2: Daily Standup
⏱️  Duration: 15 minutes
👥 Participants: 3
💰 Total Cost: $63.75
💸 Cost per minute: $4.25

📊 Participant Breakdown:
  • Alice Johnson (Senior Product Manager): $23.75
  • Bob Smith (Senior Developer): $21.25
  • Carol Davis (UX Designer): $18.75

📈 Overall Statistics:
  • Total meetings: 4
  • Total cost: $1342.50
  • Average cost per meeting: $335.62
  • Average duration: 71.2 minutes
  • Total hours: 4.75 hours

⏰ Real-time Cost Example (30 minutes elapsed):
  • Current cost: $125.00
  • Cost per minute: $4.17
  • Projected hourly cost: $250.00
```

## 🔧 Customization

### Adding New Test Participants
```python
def create_sample_participants():
    return [
        Participant(
            name="Your Name",
            hourly_rate=100.0,
            role="Your Role"
        ),
        # ... more participants
    ]
```

### Adding New Test Meetings
```python
def create_sample_meetings():
    participants = create_sample_participants()
    return [
        Meeting(
            id="custom-meeting",
            title="Your Meeting",
            duration_minutes=45,
            participants=participants[:2],
            start_time=datetime(2025, 1, 20, 14, 0)
        ),
        # ... more meetings
    ]
```

### Testing Specific Scenarios
```python
# Test high-cost meeting
expensive_participants = [
    Participant(name="CEO", hourly_rate=500.0, role="Chief Executive"),
    Participant(name="CTO", hourly_rate=400.0, role="Chief Technology Officer")
]

expensive_meeting = Meeting(
    title="Executive Strategy",
    duration_minutes=120,
    participants=expensive_participants
)

cost = MeetingCostCalculator.calculate_meeting_cost(expensive_meeting)
print(f"Executive meeting cost: ${cost.total_cost}")  # $1800.00
```

## 🧪 Use Cases

### Development
- **Logic Validation**: Ensure calculation algorithms work correctly
- **Edge Case Testing**: Test with extreme values (very high/low rates, long/short meetings)
- **Performance Testing**: Check calculation speed with many participants

### Demonstration
- **Client Demos**: Show potential clients how the system works
- **Training**: Help team members understand the calculation logic
- **Documentation**: Generate examples for API documentation

### Integration Testing
- **Before API Changes**: Verify core logic before making API modifications
- **After Database Changes**: Ensure calculations still work with new data models
- **Regression Testing**: Catch calculation bugs during development

## 💡 Tips

1. **Modify for Your Use Case**: Adjust participant rates and meeting types to match your organization
2. **Add Edge Cases**: Test with zero rates, very long meetings, single participants
3. **Benchmark Performance**: Time the calculations for performance optimization
4. **Generate Test Data**: Use this as a template for creating API test fixtures

## 🔗 Related Files

- `src/services/calculator.py` - Core calculation logic being tested
- `src/models/participant.py` - Participant data models
- `src/models/meeting.py` - Meeting data models
- `tests/test_api.py` - Formal unit tests for the API

This script serves as both a development tool and a demonstration of the Clock Bucks calculation capabilities!
