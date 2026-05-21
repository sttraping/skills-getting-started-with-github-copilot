"""
FastAPI tests for Mergington High School API

Tests cover the main endpoints and common error scenarios using the AAA
(Arrange-Act-Assert) testing pattern.
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app


@pytest.fixture
def client():
    """Fixture that provides a TestClient instance for testing the FastAPI app."""
    return TestClient(app)


class TestRootEndpoint:
    """Tests for the root GET / endpoint."""
    
    def test_root_redirect_to_static(self, client):
        """
        Test that GET / redirects to /static/index.html
        
        AAA Pattern:
        - Arrange: TestClient ready
        - Act: Make GET request to /
        - Assert: Verify redirect status and location
        """
        # Act
        response = client.get("/", follow_redirects=False)
        
        # Assert
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"


class TestActivitiesEndpoint:
    """Tests for the GET /activities endpoint."""
    
    def test_get_all_activities_success(self, client):
        """
        Test that GET /activities returns all activities
        
        AAA Pattern:
        - Arrange: TestClient ready, expecting 9 activities
        - Act: Make GET request to /activities
        - Assert: Verify response status and activity data structure
        """
        # Act
        response = client.get("/activities")
        data = response.json()
        
        # Assert
        assert response.status_code == 200
        assert isinstance(data, dict)
        assert len(data) == 9
        assert "Chess Club" in data
        assert "Programming Class" in data
        assert "Soccer Team" in data
    
    def test_get_activities_contains_required_fields(self, client):
        """
        Test that each activity has required fields
        
        AAA Pattern:
        - Arrange: TestClient ready
        - Act: Make GET request to /activities
        - Assert: Verify required fields present in activity objects
        """
        # Act
        response = client.get("/activities")
        activities = response.json()
        
        # Assert
        assert response.status_code == 200
        for activity_name, activity_data in activities.items():
            assert "description" in activity_data
            assert "schedule" in activity_data
            assert "max_participants" in activity_data
            assert "participants" in activity_data
            assert isinstance(activity_data["participants"], list)


class TestSignupEndpoint:
    """Tests for the POST /activities/{activity_name}/signup endpoint."""
    
    def test_signup_new_student_success(self, client):
        """
        Test successful signup of a new student to an activity
        
        AAA Pattern:
        - Arrange: Prepare a new email not in Chess Club participants
        - Act: Make POST signup request
        - Assert: Verify success message and student added to activity
        """
        # Arrange
        activity_name = "Chess Club"
        new_email = "newstudent@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": new_email}
        )
        
        # Assert
        assert response.status_code == 200
        assert response.json()["message"] == f"Signed up {new_email} for {activity_name}"
        
        # Verify student was added
        activities_response = client.get("/activities")
        activities = activities_response.json()
        assert new_email in activities[activity_name]["participants"]
    
    def test_signup_activity_not_found(self, client):
        """
        Test signup request for non-existent activity returns 404
        
        AAA Pattern:
        - Arrange: Prepare non-existent activity name
        - Act: Make POST signup request to invalid activity
        - Assert: Verify 404 response with appropriate error message
        """
        # Arrange
        invalid_activity = "Nonexistent Club"
        email = "student@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{invalid_activity}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"
    
    def test_signup_student_already_signed_up(self, client):
        """
        Test signup request for student already in activity returns 400
        
        AAA Pattern:
        - Arrange: Get existing participant from activity
        - Act: Attempt to signup same student again
        - Assert: Verify 400 response with conflict message
        """
        # Arrange
        activity_name = "Chess Club"
        activities_response = client.get("/activities")
        activities = activities_response.json()
        existing_email = activities[activity_name]["participants"][0]
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": existing_email}
        )
        
        # Assert
        assert response.status_code == 400
        assert response.json()["detail"] == "Student already signed up"


class TestUnregisterEndpoint:
    """Tests for the DELETE /activities/{activity_name}/participants endpoint."""
    
    def test_unregister_student_success(self, client):
        """
        Test successful unregister of a student from an activity
        
        AAA Pattern:
        - Arrange: Add a new student, then prepare to remove them
        - Act: Make DELETE unregister request
        - Assert: Verify success message and student removed from activity
        """
        # Arrange
        activity_name = "Chess Club"
        test_email = "unregister_test@mergington.edu"
        
        # First, signup the student
        client.post(
            f"/activities/{activity_name}/signup",
            params={"email": test_email}
        )
        
        # Act: Unregister the student
        response = client.delete(
            f"/activities/{activity_name}/participants",
            params={"email": test_email}
        )
        
        # Assert
        assert response.status_code == 200
        assert response.json()["message"] == f"Unregistered {test_email} from {activity_name}"
        
        # Verify student was removed
        activities_response = client.get("/activities")
        activities = activities_response.json()
        assert test_email not in activities[activity_name]["participants"]
    
    def test_unregister_activity_not_found(self, client):
        """
        Test unregister request for non-existent activity returns 404
        
        AAA Pattern:
        - Arrange: Prepare non-existent activity name
        - Act: Make DELETE request to invalid activity
        - Assert: Verify 404 response with appropriate error message
        """
        # Arrange
        invalid_activity = "Nonexistent Club"
        email = "student@mergington.edu"
        
        # Act
        response = client.delete(
            f"/activities/{invalid_activity}/participants",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"
    
    def test_unregister_student_not_signed_up(self, client):
        """
        Test unregister request for student not in activity returns 404
        
        AAA Pattern:
        - Arrange: Use email not in any activity participant list
        - Act: Attempt to unregister student from activity
        - Assert: Verify 404 response indicating student not signed up
        """
        # Arrange
        activity_name = "Chess Club"
        non_participant_email = "never_signed_up@mergington.edu"
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/participants",
            params={"email": non_participant_email}
        )
        
        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Student not signed up for this activity"
