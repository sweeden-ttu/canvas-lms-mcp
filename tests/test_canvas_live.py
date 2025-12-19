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


@pytest.fixture(scope="module")
def module_id(api_client, course_id):
    """Get a valid module ID from the first course, or skip if not available."""
    response = api_client.get(
        f"/api/v1/courses/{course_id}/modules",
        params={"per_page": 10}
    )
    if response.status_code == 200:
        modules = response.json()
        if modules:
            return modules[0]["id"]
    pytest.skip(f"No modules found in course {course_id}")


@pytest.fixture(scope="module")
def assignment_id(api_client, course_id):
    """Get a valid assignment ID from the first course, or skip if not available."""
    response = api_client.get(
        f"/api/v1/courses/{course_id}/assignments",
        params={"per_page": 10}
    )
    if response.status_code == 200:
        assignments = response.json()
        if assignments:
            return assignments[0]["id"]
    pytest.skip(f"No assignments found in course {course_id}")


@pytest.fixture(scope="module")
def file_id(api_client, course_id, module_id):
    """Get a valid file ID from module items, or skip if not available."""
    response = api_client.get(
        f"/api/v1/courses/{course_id}/modules/{module_id}/items",
        params={"per_page": 50}
    )
    if response.status_code == 200:
        items = response.json()
        for item in items:
            if item.get("type") == "File" and item.get("content_id"):
                return item["content_id"]
    pytest.skip(f"No files found in module {module_id} of course {course_id}")


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
    
    def test_calendar_events(self, api_client):
        """GET /api/v1/calendar_events - List calendar events."""
        response = api_client.get(
            "/api/v1/calendar_events",
            params={"per_page": 50}
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert isinstance(data, list), "Response should be a list"
        
        print(f"\n  ✓ Found {len(data)} calendar event(s)")
    
    def test_planner_items(self, api_client):
        """GET /api/v1/planner/items - List planner items."""
        response = api_client.get(
            "/api/v1/planner/items",
            params={"per_page": 50}
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert isinstance(data, list), "Response should be a list"
        
        print(f"\n  ✓ Found {len(data)} planner item(s)")
    
    def test_planner_notes(self, api_client):
        """GET /api/v1/planner_notes - List planner notes."""
        response = api_client.get(
            "/api/v1/planner_notes",
            params={"per_page": 50}
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert isinstance(data, list), "Response should be a list"
        
        print(f"\n  ✓ Found {len(data)} planner note(s)")


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
    
    def test_module_items(self, api_client, course_id, module_id):
        """GET /api/v1/courses/{id}/modules/{module_id}/items - Get module items."""
        response = api_client.get(
            f"/api/v1/courses/{course_id}/modules/{module_id}/items",
            params={"per_page": 50}
        )
        
        assert response.status_code == 200, (
            f"Expected 200, got {response.status_code}"
        )
        
        data = response.json()
        assert isinstance(data, list), "Response should be a list"
        
        print(f"\n  ✓ Found {len(data)} item(s) in module {module_id}")
        file_count = sum(1 for item in data if item.get("type") == "File")
        if file_count > 0:
            print(f"    - {file_count} file(s) found in module")
    
    def test_course_pages(self, api_client, course_id):
        """GET /api/v1/courses/{id}/pages - Get course wiki pages."""
        response = api_client.get(
            f"/api/v1/courses/{course_id}/pages",
            params={"per_page": 50}
        )
        
        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, list), "Response should be a list"
            print(f"\n  ✓ Found {len(data)} page(s) in course {course_id}")
        elif response.status_code == 404:
            print(f"\n  ✓ Course {course_id} does not have wiki pages (404 - expected)")
            pytest.skip("Course does not have wiki pages enabled")
        else:
            pytest.fail(f"Unexpected status code: {response.status_code}")
    
    def test_course_quizzes(self, api_client, course_id):
        """GET /api/v1/courses/{id}/quizzes - Get course quizzes."""
        response = api_client.get(
            f"/api/v1/courses/{course_id}/quizzes",
            params={"per_page": 50}
        )
        
        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, list), "Response should be a list"
            print(f"\n  ✓ Found {len(data)} quiz(zes) in course {course_id}")
        elif response.status_code == 404:
            print(f"\n  ✓ Course {course_id} does not have quizzes (404 - expected)")
            pytest.skip("Course does not have quizzes or endpoint not available")
        else:
            pytest.fail(f"Unexpected status code: {response.status_code}")
    
    def test_course_sections(self, api_client, course_id):
        """GET /api/v1/courses/{id}/sections - Get course sections."""
        response = api_client.get(
            f"/api/v1/courses/{course_id}/sections",
            params={"per_page": 50}
        )
        
        assert response.status_code == 200, (
            f"Expected 200, got {response.status_code}"
        )
        
        data = response.json()
        assert isinstance(data, list), "Response should be a list"
        
        print(f"\n  ✓ Found {len(data)} section(s) in course {course_id}")
    
    def test_course_settings(self, api_client, course_id):
        """GET /api/v1/courses/{id}/settings - Get course settings."""
        response = api_client.get(
            f"/api/v1/courses/{course_id}/settings"
        )
        
        assert response.status_code == 200, (
            f"Expected 200, got {response.status_code}"
        )
        
        data = response.json()
        assert isinstance(data, dict), "Response should be a dict"
        
        print(f"\n  ✓ Retrieved settings for course {course_id}")
    
    def test_submissions(self, api_client, course_id, assignment_id):
        """GET /api/v1/courses/{id}/assignments/{assignment_id}/submissions - Get submissions."""
        response = api_client.get(
            f"/api/v1/courses/{course_id}/assignments/{assignment_id}/submissions",
            params={"user_id": "self", "per_page": 10}
        )
        
        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, list), "Response should be a list"
            print(f"\n  ✓ Found {len(data)} submission(s) for assignment {assignment_id}")
        elif response.status_code == 403:
            print(f"\n  ✓ Submissions endpoint returns 403 (may require different permissions)")
            pytest.skip("Submissions endpoint returns 403 - may require instructor permissions or different parameters")
        else:
            pytest.fail(f"Unexpected status code: {response.status_code}")
    
    def test_file_metadata(self, api_client, course_id, file_id):
        """GET /api/v1/courses/{id}/files/{file_id} - Get file metadata."""
        response = api_client.get(
            f"/api/v1/courses/{course_id}/files/{file_id}"
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"\n  ✓ Retrieved file metadata for file {file_id}")
            print(f"    - File name: {data.get('filename', 'N/A')}")
            print(f"    - File size: {data.get('size', 'N/A')} bytes")
        elif response.status_code == 403:
            print(f"\n  ✓ File endpoint returns 403 (expected for some files)")
            pytest.skip("File access returns 403 - may require special permissions")
        else:
            pytest.fail(f"Unexpected status code: {response.status_code}")
    
    def test_file_public_url(self, api_client, file_id):
        """GET /api/v1/files/{file_id}/public_url - Get file public download URL."""
        response = api_client.get(
            f"/api/v1/files/{file_id}/public_url"
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"\n  ✓ Retrieved public URL for file {file_id}")
            assert "public_url" in data or "url" in data, "Response should contain URL"
        elif response.status_code == 403:
            print(f"\n  ✓ File public URL endpoint returns 403 (expected for some files)")
            pytest.skip("File public URL access returns 403 - may require special permissions")
        else:
            pytest.fail(f"Unexpected status code: {response.status_code}")
    
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
