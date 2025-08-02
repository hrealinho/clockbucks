import pytest
from fastapi.testclient import TestClient
from uuid import uuid4

def test_health_check(client: TestClient):
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "clock-bucks-api"

def test_root_endpoint(client: TestClient):
    """Test root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "Clock Bucks" in data["message"]

def test_api_documentation(client: TestClient):
    """Test that API documentation is accessible."""
    response = client.get("/docs")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]

def test_openapi_schema(client: TestClient):
    """Test OpenAPI schema endpoint."""
    response = client.get("/openapi.json")
    assert response.status_code == 200
    data = response.json()
    assert "openapi" in data
    assert "info" in data
    assert data["info"]["title"] == "Clock Bucks - Meeting Cost Calculator"

class TestParticipantEndpoints:
    """Test participant-related endpoints."""
    
    def test_create_participant(self, client: TestClient, sample_participant_data):
        """Test creating a new participant."""
        response = client.post("/api/v1/participants", json=sample_participant_data)
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == sample_participant_data["name"]
        assert data["email"] == sample_participant_data["email"]
        assert data["hourly_rate"] == sample_participant_data["hourly_rate"]
        assert "id" in data
        assert "created_at" in data
    
    def test_create_participant_invalid_data(self, client: TestClient):
        """Test creating participant with invalid data."""
        invalid_data = {
            "name": "",  # Empty name
            "hourly_rate": -10,  # Negative rate
            "email": "invalid-email"  # Invalid email format
        }
        response = client.post("/api/v1/participants", json=invalid_data)
        assert response.status_code == 422
    
    def test_get_participants(self, client: TestClient, sample_participant_data):
        """Test getting list of participants."""
        # Create a participant first
        client.post("/api/v1/participants", json=sample_participant_data)
        
        response = client.get("/api/v1/participants")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
    
    def test_get_participant_by_id(self, client: TestClient, sample_participant_data):
        """Test getting a specific participant."""
        # Create participant
        create_response = client.post("/api/v1/participants", json=sample_participant_data)
        participant_id = create_response.json()["id"]
        
        # Get participant
        response = client.get(f"/api/v1/participants/{participant_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == participant_id
        assert data["name"] == sample_participant_data["name"]
    
    def test_get_nonexistent_participant(self, client: TestClient):
        """Test getting a non-existent participant."""
        fake_id = str(uuid4())
        response = client.get(f"/api/v1/participants/{fake_id}")
        assert response.status_code == 404
    
    def test_update_participant(self, client: TestClient, sample_participant_data):
        """Test updating a participant."""
        # Create participant
        create_response = client.post("/api/v1/participants", json=sample_participant_data)
        participant_id = create_response.json()["id"]
        
        # Update participant
        update_data = {"hourly_rate": 90.0, "role": "Lead Developer"}
        response = client.put(f"/api/v1/participants/{participant_id}", json=update_data)
        assert response.status_code == 200
        data = response.json()
        assert data["hourly_rate"] == 90.0
        assert data["role"] == "Lead Developer"
    
    def test_delete_participant(self, client: TestClient, sample_participant_data):
        """Test deleting a participant."""
        # Create participant
        create_response = client.post("/api/v1/participants", json=sample_participant_data)
        participant_id = create_response.json()["id"]
        
        # Delete participant
        response = client.delete(f"/api/v1/participants/{participant_id}")
        assert response.status_code == 200
        
        # Verify participant is deleted
        get_response = client.get(f"/api/v1/participants/{participant_id}")
        assert get_response.status_code == 404

class TestMeetingEndpoints:
    """Test meeting-related endpoints."""
    
    def test_calculate_meeting_cost(self, client: TestClient, sample_meeting_data):
        """Test calculating meeting cost."""
        response = client.post("/api/v1/meetings/calculate", json=sample_meeting_data)
        assert response.status_code == 200
        data = response.json()
        assert "total_cost" in data
        assert "cost_per_minute" in data
        assert "participants_count" in data
        assert data["participants_count"] == 2
        assert data["total_cost"] > 0
    
    def test_calculate_meeting_cost_invalid_data(self, client: TestClient):
        """Test calculating cost with invalid data."""
        invalid_data = {
            "title": "",  # Empty title
            "duration_minutes": -30,  # Negative duration
            "participants": []  # No participants
        }
        response = client.post("/api/v1/meetings/calculate", json=invalid_data)
        assert response.status_code == 422
    
    def test_real_time_cost_calculation(self, client: TestClient):
        """Test real-time cost calculation."""
        participants = [
            {"name": "John", "hourly_rate": 75.0},
            {"name": "Jane", "hourly_rate": 85.0}
        ]
        response = client.post(
            "/api/v1/meetings/real-time-cost",
            json={"participants": participants, "elapsed_minutes": 30}
        )
        assert response.status_code == 200
        data = response.json()
        assert "current_total_cost" in data
        assert "cost_per_minute" in data
        assert data["elapsed_minutes"] == 30

class TestValidation:
    """Test data validation."""
    
    def test_participant_email_validation(self, client: TestClient):
        """Test email validation for participants."""
        invalid_emails = ["", "invalid", "@invalid.com", "invalid@"]
        
        for email in invalid_emails:
            data = {
                "name": "Test User",
                "email": email,
                "hourly_rate": 50.0
            }
            response = client.post("/api/v1/participants", json=data)
            assert response.status_code == 422
    
    def test_hourly_rate_validation(self, client: TestClient):
        """Test hourly rate validation."""
        invalid_rates = [-10, 0, 15000]  # negative, zero, too high
        
        for rate in invalid_rates:
            data = {
                "name": "Test User",
                "email": "test@example.com",
                "hourly_rate": rate
            }
            response = client.post("/api/v1/participants", json=data)
            assert response.status_code == 422

class TestErrorHandling:
    """Test error handling."""
    
    def test_404_handling(self, client: TestClient):
        """Test 404 error handling."""
        response = client.get("/nonexistent-endpoint")
        assert response.status_code == 404
    
    def test_method_not_allowed(self, client: TestClient):
        """Test 405 error handling."""
        response = client.patch("/api/v1/participants")  # PATCH not allowed
        assert response.status_code == 405
