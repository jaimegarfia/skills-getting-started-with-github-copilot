"""
Tests for the Mergington High School Activity Management API
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app


@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    return TestClient(app)


class TestActivitiesAPI:
    """Test suite for activities endpoints"""

    def test_get_activities_returns_all_activities(self, client):
        """Test GET /activities returns all activities with correct structure"""
        response = client.get("/activities")

        assert response.status_code == 200
        activities = response.json()

        # Should have 9 activities
        assert len(activities) == 9

        # Check that all expected activities are present
        expected_activities = [
            "Chess Club", "Programming Class", "Gym Class", "Basketball Team",
            "Tennis Club", "Art Studio", "Drama Club", "Math Club", "Science Lab"
        ]
        assert set(activities.keys()) == set(expected_activities)

        # Check structure of first activity
        chess_club = activities["Chess Club"]
        assert "description" in chess_club
        assert "schedule" in chess_club
        assert "max_participants" in chess_club
        assert "participants" in chess_club
        assert isinstance(chess_club["participants"], list)

    def test_signup_for_activity_success(self, client):
        """Test successful signup for an activity"""
        response = client.post("/activities/Chess%20Club/signup?email=test@mergington.edu")

        assert response.status_code == 200
        result = response.json()
        assert "message" in result
        assert "test@mergington.edu" in result["message"]
        assert "Chess Club" in result["message"]

        # Verify the participant was added
        activities_response = client.get("/activities")
        activities = activities_response.json()
        assert "test@mergington.edu" in activities["Chess Club"]["participants"]

    def test_signup_for_nonexistent_activity(self, client):
        """Test signup for activity that doesn't exist"""
        response = client.post("/activities/Nonexistent%20Activity/signup?email=test@mergington.edu")

        assert response.status_code == 404
        result = response.json()
        assert result["detail"] == "Activity not found"

    def test_signup_duplicate_participant(self, client):
        """Test signup when participant is already registered"""
        # First signup
        client.post("/activities/Programming%20Class/signup?email=duplicate@mergington.edu")

        # Second signup with same email
        response = client.post("/activities/Programming%20Class/signup?email=duplicate@mergington.edu")

        assert response.status_code == 400
        result = response.json()
        assert result["detail"] == "Student already signed up for this activity"

    def test_remove_participant_success(self, client):
        """Test successful removal of a participant"""
        # First add a participant
        client.post("/activities/Tennis%20Club/signup?email=remove@mergington.edu")

        # Then remove them
        response = client.delete("/activities/Tennis%20Club/participants?email=remove@mergington.edu")

        assert response.status_code == 200
        result = response.json()
        assert "message" in result
        assert "remove@mergington.edu" in result["message"]
        assert "Tennis Club" in result["message"]

        # Verify the participant was removed
        activities_response = client.get("/activities")
        activities = activities_response.json()
        assert "remove@mergington.edu" not in activities["Tennis Club"]["participants"]

    def test_remove_participant_from_nonexistent_activity(self, client):
        """Test removal from activity that doesn't exist"""
        response = client.delete("/activities/Nonexistent%20Activity/participants?email=test@mergington.edu")

        assert response.status_code == 404
        result = response.json()
        assert result["detail"] == "Activity not found"

    def test_remove_nonexistent_participant(self, client):
        """Test removal of participant not in the activity"""
        response = client.delete("/activities/Gym%20Class/participants?email=notfound@mergington.edu")

        assert response.status_code == 404
        result = response.json()
        assert result["detail"] == "Participant not found"

    def test_root_redirect(self, client):
        """Test root endpoint redirects to static index"""
        response = client.get("/", follow_redirects=False)

        assert response.status_code == 307  # Temporary redirect
        assert "/static/index.html" in response.headers["location"]