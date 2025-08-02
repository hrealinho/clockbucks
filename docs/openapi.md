# Clock Bucks API - OpenAPI Documentation

## Overview

The Clock Bucks API is a comprehensive meeting cost calculator service built with FastAPI. It provides real-time cost tracking, participant management, and detailed analytics for meeting efficiency optimization.

## API Documentation Access

### Development Environment
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

### Production Environment  
- **Swagger UI**: https://api.clockbucks.com/docs
- **ReDoc**: https://api.clockbucks.com/redoc
- **OpenAPI JSON**: https://api.clockbucks.com/openapi.json

## Authentication

Currently, the API operates without authentication for development purposes. Production deployments should implement:

- JWT token-based authentication
- API key authentication
- OAuth 2.0 integration
- Rate limiting per user/organization

## API Endpoints Overview

### System Endpoints
- `GET /` - API information and service status
- `GET /health` - Health check for monitoring
- `GET /metrics` - Service metrics (if enabled)

### Meeting Management
- `POST /api/v1/meetings/calculate` - Calculate meeting costs
- `POST /api/v1/meetings/real-time-cost` - Real-time cost tracking
- `POST /api/v1/meetings` - Create new meeting
- `GET /api/v1/meetings` - List meetings with filtering
- `GET /api/v1/meetings/{id}` - Get meeting details
- `GET /api/v1/meetings/{id}/cost` - Get meeting cost calculation
- `GET /api/v1/meetings/statistics/overview` - Meeting statistics
- `POST /api/v1/meetings/{id}/start` - Start meeting tracking
- `POST /api/v1/meetings/{id}/end` - End meeting and finalize costs
- `DELETE /api/v1/meetings/{id}` - Delete meeting record

### Participant Management
- `POST /api/v1/participants` - Create new participant
- `GET /api/v1/participants` - List all participants
- `GET /api/v1/participants/{id}` - Get participant details
- `PUT /api/v1/participants/{id}` - Update participant
- `DELETE /api/v1/participants/{id}` - Delete participant

## Data Models

### Meeting Models

#### MeetingCreate
```json
{
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
  "description": "Planning meeting for next sprint",
  "meeting_type": "planning"
}
```

#### MeetingResponse
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "title": "Sprint Planning",
  "duration_minutes": 60,
  "participants": [...],
  "start_time": "2025-01-15T10:00:00Z",
  "end_time": null,
  "total_cost": 75.0,
  "created_at": "2025-01-15T09:45:00Z"
}
```

#### MeetingCostCalculation
```json
{
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
    }
  ],
  "calculation_time": "2025-01-15T10:00:00Z"
}
```

### Participant Models

#### ParticipantCreate
```json
{
  "name": "John Doe",
  "email": "john.doe@company.com",
  "hourly_rate": 75.0,
  "role": "Senior Developer",
  "department": "Engineering"
}
```

#### ParticipantResponse
```json
{
  "id": "456e7890-e89b-12d3-a456-426614174001",
  "name": "John Doe",
  "email": "john.doe@company.com",
  "hourly_rate": 75.0,
  "role": "Senior Developer",
  "department": "Engineering",
  "created_at": "2025-01-15T09:30:00Z"
}
```

## Cost Calculation Logic

### Basic Cost Formula
```
Individual Cost = (Hourly Rate / 60) * Duration in Minutes
Total Meeting Cost = Sum of all Individual Costs
Cost per Minute = Total Cost / Duration in Minutes
```

### Real-Time Calculation
```
Current Cost = (Hourly Rate / 60) * Elapsed Minutes
Projected Total = (Hourly Rate / 60) * Expected Duration
```

## Error Handling

The API uses standard HTTP status codes and provides detailed error messages:

### Common Error Responses

#### 400 Bad Request
```json
{
  "detail": "Meeting duration must be greater than 0"
}
```

#### 404 Not Found
```json
{
  "detail": "Meeting not found"
}
```

#### 422 Validation Error
```json
{
  "detail": [
    {
      "loc": ["body", "participants"],
      "msg": "ensure this value has at least 1 items",
      "type": "value_error.list.min_items"
    }
  ]
}
```

#### 500 Internal Server Error
```json
{
  "message": "Internal server error",
  "error_code": "INTERNAL_ERROR",
  "details": {}
}
```

## Rate Limiting

- Default: 60 requests per minute per IP
- Configurable via environment variables
- Headers included in responses:
  - `X-RateLimit-Limit`: Request limit
  - `X-RateLimit-Remaining`: Remaining requests
  - `X-RateLimit-Reset`: Reset timestamp

## Examples

### Create and Calculate Meeting Cost

1. **Create Participants**
```bash
curl -X POST "http://localhost:8000/api/v1/participants" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "email": "john@company.com",
    "hourly_rate": 75.0,
    "role": "Senior Developer",
    "department": "Engineering"
  }'
```

2. **Calculate Meeting Cost**
```bash
curl -X POST "http://localhost:8000/api/v1/meetings/calculate" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Sprint Planning",
    "duration_minutes": 60,
    "participants": [
      {
        "name": "John Doe",
        "hourly_rate": 75.0,
        "role": "Senior Developer"
      }
    ]
  }'
```

### Real-Time Cost Tracking

```bash
curl -X POST "http://localhost:8000/api/v1/meetings/real-time-cost?elapsed_minutes=30" \
  -H "Content-Type: application/json" \
  -d '{
    "participants": [
      {
        "name": "John Doe",
        "hourly_rate": 75.0,
        "role": "Senior Developer"
      }
    ]
  }'
```

### Get Meeting Statistics

```bash
curl -X GET "http://localhost:8000/api/v1/meetings/statistics/overview"
```

## SDK and Client Libraries

Future releases will include:
- Python SDK
- JavaScript/TypeScript SDK
- REST client libraries
- Webhook support

## Versioning

- Current version: v1
- Base path: `/api/v1`
- Semantic versioning for releases
- Backward compatibility maintained

## Support and Resources

- **Documentation**: https://docs.clockbucks.com
- **GitHub Repository**: https://github.com/hrealinho/clockbucks
- **Issue Tracker**: https://github.com/hrealinho/clockbucks/issues
- **API Status**: https://status.clockbucks.com

## Changes and Updates

API changes are documented in the [CHANGELOG.md](../CHANGELOG.md) file. Subscribe to releases on GitHub for notifications about updates.
