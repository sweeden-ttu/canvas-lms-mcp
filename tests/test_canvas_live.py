"""
Canvas LMS Live API Tests

These tests hit the REAL Canvas API at Texas Tech University.
They are designed to:
1. Verify endpoint accessibility with current credentials
2. Discover which endpoints work for the current user
3. Skip tests gracefully when required IDs are missing

Run with: uv run pytest tests/test_canvas_live.py -v

Note: Some tests may be skipped if test_hints.json is not configured.
"""

import pytest
import httpx
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import get_config, get_api_headers


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture(scope="module")
def canvas_config():
    """Load Canvas configuration."""
    config, hints = get_config()
    return config, hints


@pytest.fixture(scope="module")
def api_client(canvas_config):
    """Create an HTTP client for Canvas API."""
    config, _ = canvas_config
    client = httpx.Client(
        base_url=config.base_url,
        headers=get_api_headers(config.api_token),
        timeout=30.0,
    )
    yield client
    client.close()


@pytest.fixture(scope="module")
def course_id(canvas_config):
    """Get a valid course ID from hints, or skip if not available."""
    _, hints = canvas_config
    if not hints.valid_course_ids:
        pytest.skip(
            "Missing 'valid_course_ids' in test_hints.json. "
            "Please add at least one course ID to continue. "
            "You can find course IDs in the URL when viewing a course in Canvas "
            "(e.g., https://texastech.instructure.com/courses/58606)"
        )
    return hints.valid_course_ids[0]


@pytest.fixture(scope="module")
def all_course_ids(canvas_config):
    """Get all valid course IDs from hints."""
    _, hints = canvas_config
    if not hints.valid_course_ids:
        pytest.skip("Missing 'valid_course_ids' in test_hints.json")
    return hints.valid_course_ids


# =============================================================================
# Discovery Tests (No IDs Required)
# =============================================================================

class TestDiscoveryEndpoints:
    """Tests for endpoints that don't require any IDs."""
    
    def test_user_profile(self, api_client):
        """GET /api/v1/users/self/profile - Get current user profile."""
        response = api_client.get("/api/v1/users/self/profile")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "id" in data, "Response should contain user ID"
        assert "name" in data, "Response should contain user name"
        
        print(f"\n  ✓ Authenticated as: {data.get('name', 'Unknown')}")
        print(f"  ✓ User ID: {data.get('id')}")
        print(f"  ✓ Login ID: {data.get('login_id', 'N/A')}")
    
    def test_list_courses(self, api_client):
        """GET /api/v1/courses - List enrolled courses."""
        response = api_client.get(
            "/api/v1/courses",
            params={"enrollment_state": "active", "per_page": 50}
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert isinstance(data, list), "Response should be a list"
        
        print(f"\n  ✓ Found {len(data)} active course(s)")
        for course in data[:5]:  # Show first 5
            print(f"    - {course.get('id')}: {course.get('name', 'Unnamed')}")
        if len(data) > 5:
            print(f"    ... and {len(data) - 5} more")
    
    def test_todo_items(self, api_client):
        """GET /api/v1/users/self/todo - Get to-do items."""
        response = api_client.get(
            "/api/v1/users/self/todo",
            params={"per_page": 50}
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert isinstance(data, list), "Response should be a list"
        
        print(f"\n  ✓ Found {len(data)} to-do item(s)")
    
    def test_upcoming_events(self, api_client):
        """GET /api/v1/users/self/upcoming_events - Get upcoming events."""
        response = api_client.get(
            "/api/v1/users/self/upcoming_events",
            params={"per_page": 50}
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert isinstance(data, list), "Response should be a list"
        
        print(f"\n  ✓ Found {len(data)} upcoming event(s)")


# =============================================================================
# Deep-Dive Tests (Course ID Required)
# =============================================================================

class TestCourseEndpoints:
    """Tests for course-specific endpoints. Requires valid_course_id in test_hints.json."""
    
    def test_course_assignments(self, api_client, course_id):
        """GET /api/v1/courses/{id}/assignments - Get course assignments."""
        response = api_client.get(
            f"/api/v1/courses/{course_id}/assignments",
            params={"per_page": 50, "order_by": "due_at"}
        )
        
        assert response.status_code == 200, (
            f"Expected 200, got {response.status_code}. "
            f"Course ID {course_id} may be invalid or you may not have access."
        )
        
        data = response.json()
        assert isinstance(data, list), "Response should be a list"
        
        print(f"\n  ✓ Found {len(data)} assignment(s) in course {course_id}")
        for assignment in data[:3]:
            due = assignment.get('due_at', 'No due date')
            print(f"    - {assignment.get('name', 'Unnamed')}: due {due}")
    
    def test_course_modules(self, api_client, course_id):
        """GET /api/v1/courses/{id}/modules - Get course modules."""
        response = api_client.get(
            f"/api/v1/courses/{course_id}/modules",
            params={"per_page": 50}
        )
        
        assert response.status_code == 200, (
            f"Expected 200, got {response.status_code}. "
            f"Course {course_id} may not have modules or you may lack access."
        )
        
        data = response.json()
        assert isinstance(data, list), "Response should be a list"
        
        print(f"\n  ✓ Found {len(data)} module(s) in course {course_id}")
    
    def test_discussion_topics(self, api_client, course_id):
        """GET /api/v1/courses/{id}/discussion_topics - Get discussions."""
        response = api_client.get(
            f"/api/v1/courses/{course_id}/discussion_topics",
            params={"per_page": 50}
        )
        
        assert response.status_code == 200, (
            f"Expected 200, got {response.status_code}"
        )
        
        data = response.json()
        assert isinstance(data, list), "Response should be a list"
        
        print(f"\n  ✓ Found {len(data)} discussion topic(s) in course {course_id}")
    
    def test_enrollments_grades(self, api_client, course_id):
        """GET /api/v1/courses/{id}/enrollments - Get grades via enrollment."""
        response = api_client.get(
            f"/api/v1/courses/{course_id}/enrollments",
            params={"user_id": "self", "type[]": "StudentEnrollment"}
        )
        
        assert response.status_code == 200, (
            f"Expected 200, got {response.status_code}"
        )
        
        data = response.json()
        assert isinstance(data, list), "Response should be a list"
        
        print(f"\n  ✓ Found {len(data)} enrollment(s) in course {course_id}")
        for enrollment in data:
            grades = enrollment.get('grades', {})
            if grades:
                print(f"    - Current grade: {grades.get('current_grade', 'N/A')}")
                print(f"    - Current score: {grades.get('current_score', 'N/A')}")
    
    def test_announcements(self, api_client, all_course_ids):
        """GET /api/v1/announcements - Get announcements for courses."""
        context_codes = [f"course_{cid}" for cid in all_course_ids]
        
        response = api_client.get(
            "/api/v1/announcements",
            params={"context_codes[]": context_codes, "per_page": 50}
        )
        
        assert response.status_code == 200, (
            f"Expected 200, got {response.status_code}"
        )
        
        data = response.json()
        assert isinstance(data, list), "Response should be a list"
        
        print(f"\n  ✓ Found {len(data)} announcement(s) across {len(all_course_ids)} course(s)")
    
    def test_files_expect_403(self, api_client, course_id):
        """
        GET /api/v1/courses/{id}/files - Expected to fail with 403.
        
        This test documents that the /files endpoint is NOT accessible
        for student accounts. This is expected behavior.
        """
        response = api_client.get(
            f"/api/v1/courses/{course_id}/files",
            params={"per_page": 50}
        )
        
        # We expect this to fail for student accounts
        if response.status_code == 403:
            print(f"\n  ✓ Files endpoint correctly returns 403 (expected for students)")
            pytest.skip("Files endpoint returns 403 as expected - this is normal for student accounts")
        elif response.status_code == 200:
            # Unexpected success - maybe they have special permissions
            print(f"\n  ! Files endpoint returned 200 (unexpected - user may have elevated permissions)")
            data = response.json()
            print(f"    Found {len(data)} file(s)")
        else:
            pytest.fail(f"Unexpected status code: {response.status_code}")


# =============================================================================
# Error Handling Tests
# =============================================================================

class TestErrorHandling:
    """Tests for error scenarios."""
    
    def test_invalid_course_id(self, api_client):
        """Verify 404 is returned for invalid course ID."""
        response = api_client.get("/api/v1/courses/999999999/assignments")
        
        # Canvas may return 404 or 401 depending on settings
        assert response.status_code in [401, 403, 404], (
            f"Expected 401/403/404 for invalid course, got {response.status_code}"
        )
        print(f"\n  ✓ Invalid course ID correctly returns {response.status_code}")
    
    def test_rate_limit_headers(self, api_client):
        """Check for rate limit headers in response."""
        response = api_client.get("/api/v1/users/self/profile")
        
        # Canvas includes rate limit info in headers
        remaining = response.headers.get("X-Rate-Limit-Remaining")
        if remaining:
            print(f"\n  ✓ Rate limit remaining: {remaining}")
        else:
            print("\n  ℹ Rate limit headers not present in response")


# =============================================================================
# Integration Test
# =============================================================================

class TestIntegration:
    """End-to-end integration tests."""
    
    def test_full_workflow(self, api_client, canvas_config):
        """Test a complete workflow: list courses -> get assignments."""
        # Step 1: Get courses
        courses_response = api_client.get(
            "/api/v1/courses",
            params={"enrollment_state": "active", "per_page": 10}
        )
        assert courses_response.status_code == 200
        courses = courses_response.json()
        
        if not courses:
            pytest.skip("No courses available for integration test")
        
        # Step 2: Get assignments from first course
        course_id = courses[0]["id"]
        assignments_response = api_client.get(
            f"/api/v1/courses/{course_id}/assignments",
            params={"per_page": 5}
        )
        assert assignments_response.status_code == 200
        
        print(f"\n  ✓ Integration test passed:")
        print(f"    - Listed {len(courses)} courses")
        print(f"    - Retrieved assignments from course {course_id}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
