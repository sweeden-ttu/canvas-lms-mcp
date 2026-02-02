#!/usr/bin/env python3
"""
Canvas API Specification Generator

This script:
1. Re-runs verified API endpoints to confirm they still work
2. Captures the JSON response schemas
3. Generates verified_canvas_spec.json documenting what works

Usage:
    uv run python generate_spec.py
    
    # Or with specific course ID
    uv run python generate_spec.py --course-id 58606
"""

import argparse
import asyncio
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import httpx

from config import get_config, get_api_headers, DEFAULT_PER_PAGE


def extract_schema_sample(data: Any, max_items: int = 2) -> Any:
    """
    Extract a sample schema from API response data.
    
    For arrays, keeps only first few items.
    For nested objects, preserves structure with sample values.
    """
    if isinstance(data, list):
        # Keep only first few items as samples
        return [extract_schema_sample(item, max_items) for item in data[:max_items]]
    elif isinstance(data, dict):
        return {k: extract_schema_sample(v, max_items) for k, v in data.items()}
    else:
        return data


def infer_field_types(data: Any) -> dict[str, str]:
    """
    Infer field types from a sample response.
    
    Returns dict mapping field names to their types.
    """
    if isinstance(data, list) and len(data) > 0:
        return infer_field_types(data[0])
    elif isinstance(data, dict):
        types = {}
        for k, v in data.items():
            if v is None:
                types[k] = "null"
            elif isinstance(v, bool):
                types[k] = "boolean"
            elif isinstance(v, int):
                types[k] = "integer"
            elif isinstance(v, float):
                types[k] = "number"
            elif isinstance(v, str):
                types[k] = "string"
            elif isinstance(v, list):
                types[k] = "array"
            elif isinstance(v, dict):
                types[k] = "object"
            else:
                types[k] = type(v).__name__
        return types
    return {}


async def verify_endpoint(
    client: httpx.AsyncClient,
    method: str,
    path: str,
    params: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Verify an endpoint and capture its response.
    
    Returns:
        dict with status, response time, schema sample, and field types
    """
    result = {
        "endpoint": path,
        "method": method,
        "verified": False,
        "status_code": None,
        "response_time_ms": None,
        "error": None,
        "sample_response": None,
        "field_types": None,
    }
    
    try:
        start_time = asyncio.get_event_loop().time()
        response = await client.request(method, path, params=params)
        end_time = asyncio.get_event_loop().time()
        
        result["status_code"] = response.status_code
        result["response_time_ms"] = int((end_time - start_time) * 1000)
        
        if response.status_code == 200:
            result["verified"] = True
            data = response.json()
            result["sample_response"] = extract_schema_sample(data)
            result["field_types"] = infer_field_types(data)
        else:
            result["error"] = f"HTTP {response.status_code}: {response.reason_phrase}"
            
    except httpx.TimeoutException:
        result["error"] = "Request timed out"
    except httpx.RequestError as e:
        result["error"] = f"Request error: {str(e)}"
    except json.JSONDecodeError:
        result["error"] = "Invalid JSON response"
    except Exception as e:
        result["error"] = f"Unexpected error: {str(e)}"
    
    return result


async def generate_specification(course_id: int | None = None) -> dict[str, Any]:
    """
    Generate a complete API specification by verifying all endpoints.
    
    Args:
        course_id: Specific course ID to test, or None to use hints
        
    Returns:
        Complete specification dictionary
    """
    config, hints = get_config()
    
    # Determine which course IDs to test
    if course_id:
        course_ids = [course_id]
    elif hints.valid_course_ids:
        course_ids = hints.valid_course_ids
    else:
        print("WARNING: No course IDs available. Testing only user-level endpoints.", 
              file=sys.stderr)
        course_ids = []
    
    spec = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "canvas_base_url": config.base_url,
        "verified_endpoints": {},
        "failed_endpoints": {},
        "course_ids_tested": course_ids,
        "summary": {
            "total_verified": 0,
            "total_failed": 0,
        }
    }
    
    # Create HTTP client
    async with httpx.AsyncClient(
        base_url=config.base_url,
        headers=get_api_headers(config.api_token),
        timeout=30.0,
    ) as client:
        
        # User-level endpoints (no course ID required)
        user_endpoints = [
            ("GET", "/api/v1/users/self/profile", None),
            ("GET", "/api/v1/courses", {"enrollment_state": "active", "per_page": DEFAULT_PER_PAGE}),
            ("GET", "/api/v1/users/self/todo", {"per_page": DEFAULT_PER_PAGE}),
            ("GET", "/api/v1/users/self/upcoming_events", {"per_page": DEFAULT_PER_PAGE}),
            ("GET", "/api/v1/calendar_events", {"per_page": DEFAULT_PER_PAGE}),
            ("GET", "/api/v1/planner/items", {"per_page": DEFAULT_PER_PAGE}),
            ("GET", "/api/v1/planner_notes", {"per_page": DEFAULT_PER_PAGE}),
        ]
        
        print("Verifying user-level endpoints...")
        for method, path, params in user_endpoints:
            print(f"  {method} {path}...", end=" ", flush=True)
            result = await verify_endpoint(client, method, path, params)
            
            endpoint_key = f"{method} {path}"
            if result["verified"]:
                spec["verified_endpoints"][endpoint_key] = result
                spec["summary"]["total_verified"] += 1
                print(f"✅ ({result['response_time_ms']}ms)")
            else:
                spec["failed_endpoints"][endpoint_key] = result
                spec["summary"]["total_failed"] += 1
                print(f"❌ ({result['error']})")
        
        # Course-level endpoints (require course ID)
        if course_ids:
            course_endpoints = [
                ("GET", "/api/v1/courses/{course_id}/assignments", {"per_page": DEFAULT_PER_PAGE, "order_by": "due_at"}),
                ("GET", "/api/v1/courses/{course_id}/modules", {"per_page": DEFAULT_PER_PAGE}),
                ("GET", "/api/v1/courses/{course_id}/discussion_topics", {"per_page": DEFAULT_PER_PAGE}),
                ("GET", "/api/v1/courses/{course_id}/enrollments", {"user_id": "self", "type[]": "StudentEnrollment"}),
                ("GET", "/api/v1/courses/{course_id}/sections", {"per_page": DEFAULT_PER_PAGE}),
                ("GET", "/api/v1/courses/{course_id}/settings", None),
                ("GET", "/api/v1/courses/{course_id}/files", {"per_page": DEFAULT_PER_PAGE}),
                # These may return 404 if not available, but we'll test them
                ("GET", "/api/v1/courses/{course_id}/pages", {"per_page": DEFAULT_PER_PAGE}),
                ("GET", "/api/v1/courses/{course_id}/quizzes", {"per_page": DEFAULT_PER_PAGE}),
            ]
            
            # Also test announcements (uses course_ids as context_codes)
            context_codes = [f"course_{cid}" for cid in course_ids]
            
            print(f"\nVerifying course-level endpoints (using course {course_ids[0]})...")
            test_course_id = course_ids[0]
            
            for method, path_template, params in course_endpoints:
                path = path_template.replace("{course_id}", str(test_course_id))
                print(f"  {method} {path}...", end=" ", flush=True)
                result = await verify_endpoint(client, method, path, params)
                
                # Use template path as key for generalization
                endpoint_key = f"{method} {path_template}"
                if result["verified"]:
                    spec["verified_endpoints"][endpoint_key] = result
                    spec["summary"]["total_verified"] += 1
                    print(f"✅ ({result['response_time_ms']}ms)")
                else:
                    spec["failed_endpoints"][endpoint_key] = result
                    spec["summary"]["total_failed"] += 1
                    print(f"❌ ({result['error']})")
            
            # Test announcements separately (different parameter style)
            print(f"  GET /api/v1/announcements...", end=" ", flush=True)
            result = await verify_endpoint(
                client, 
                "GET", 
                "/api/v1/announcements",
                {"context_codes[]": context_codes, "per_page": DEFAULT_PER_PAGE}
            )
            endpoint_key = "GET /api/v1/announcements"
            if result["verified"]:
                spec["verified_endpoints"][endpoint_key] = result
                spec["summary"]["total_verified"] += 1
                print(f"✅ ({result['response_time_ms']}ms)")
            else:
                spec["failed_endpoints"][endpoint_key] = result
                spec["summary"]["total_failed"] += 1
                print(f"❌ ({result['error']})")
            
            # Discover module_id and test module items
            print(f"\nDiscovering module and file IDs...")
            modules_result = await verify_endpoint(
                client,
                "GET",
                f"/api/v1/courses/{test_course_id}/modules",
                {"per_page": 10}
            )
            
            if modules_result["verified"] and modules_result["sample_response"]:
                modules = modules_result["sample_response"]
                if isinstance(modules, list) and len(modules) > 0:
                    module_id = modules[0].get("id")
                    if module_id:
                        print(f"  Found module ID: {module_id}")
                        # Test module items
                        print(f"  GET /api/v1/courses/{test_course_id}/modules/{module_id}/items...", end=" ", flush=True)
                        result = await verify_endpoint(
                            client,
                            "GET",
                            f"/api/v1/courses/{test_course_id}/modules/{module_id}/items",
                            {"per_page": DEFAULT_PER_PAGE}
                        )
                        endpoint_key = "GET /api/v1/courses/{course_id}/modules/{module_id}/items"
                        if result["verified"]:
                            spec["verified_endpoints"][endpoint_key] = result
                            spec["summary"]["total_verified"] += 1
                            print(f"✅ ({result['response_time_ms']}ms)")
                            
                            # Try to find a file_id from module items
                            items = result["sample_response"]
                            if isinstance(items, list):
                                for item in items:
                                    if item.get("type") == "File" and item.get("content_id"):
                                        file_id = item["content_id"]
                                        print(f"  Found file ID: {file_id}")
                                        
                                        # Test file metadata
                                        print(f"  GET /api/v1/courses/{test_course_id}/files/{file_id}...", end=" ", flush=True)
                                        file_result = await verify_endpoint(
                                            client,
                                            "GET",
                                            f"/api/v1/courses/{test_course_id}/files/{file_id}",
                                            None
                                        )
                                        endpoint_key = "GET /api/v1/courses/{course_id}/files/{file_id}"
                                        if file_result["verified"]:
                                            spec["verified_endpoints"][endpoint_key] = file_result
                                            spec["summary"]["total_verified"] += 1
                                            print(f"✅ ({file_result['response_time_ms']}ms)")
                                        else:
                                            spec["failed_endpoints"][endpoint_key] = file_result
                                            spec["summary"]["total_failed"] += 1
                                            print(f"❌ ({file_result['error']})")
                                        
                                        # Test file public URL
                                        print(f"  GET /api/v1/files/{file_id}/public_url...", end=" ", flush=True)
                                        url_result = await verify_endpoint(
                                            client,
                                            "GET",
                                            f"/api/v1/files/{file_id}/public_url",
                                            None
                                        )
                                        endpoint_key = "GET /api/v1/files/{file_id}/public_url"
                                        if url_result["verified"]:
                                            spec["verified_endpoints"][endpoint_key] = url_result
                                            spec["summary"]["total_verified"] += 1
                                            print(f"✅ ({url_result['response_time_ms']}ms)")
                                        else:
                                            spec["failed_endpoints"][endpoint_key] = url_result
                                            spec["summary"]["total_failed"] += 1
                                            print(f"❌ ({url_result['error']})")
                                        
                                        break  # Only test first file found
                        else:
                            spec["failed_endpoints"][endpoint_key] = result
                            spec["summary"]["total_failed"] += 1
                            print(f"❌ ({result['error']})")
            
            # Discover assignment_id and test submissions
            print(f"\nDiscovering assignment ID...")
            assignments_result = await verify_endpoint(
                client,
                "GET",
                f"/api/v1/courses/{test_course_id}/assignments",
                {"per_page": 10}
            )
            
            if assignments_result["verified"] and assignments_result["sample_response"]:
                assignments = assignments_result["sample_response"]
                if isinstance(assignments, list) and len(assignments) > 0:
                    assignment_id = assignments[0].get("id")
                    if assignment_id:
                        print(f"  Found assignment ID: {assignment_id}")
                        # Test submissions (may return 403)
                        print(f"  GET /api/v1/courses/{test_course_id}/assignments/{assignment_id}/submissions...", end=" ", flush=True)
                        result = await verify_endpoint(
                            client,
                            "GET",
                            f"/api/v1/courses/{test_course_id}/assignments/{assignment_id}/submissions",
                            {"user_id": "self", "per_page": 10}
                        )
                        endpoint_key = "GET /api/v1/courses/{course_id}/assignments/{assignment_id}/submissions"
                        if result["verified"]:
                            spec["verified_endpoints"][endpoint_key] = result
                            spec["summary"]["total_verified"] += 1
                            print(f"✅ ({result['response_time_ms']}ms)")
                        else:
                            spec["failed_endpoints"][endpoint_key] = result
                            spec["summary"]["total_failed"] += 1
                            print(f"❌ ({result['error']})")
    
    return spec


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Generate Canvas API specification from live endpoint verification"
    )
    parser.add_argument(
        "--course-id",
        type=int,
        help="Specific course ID to test (overrides test_hints.json)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("verified_canvas_spec.json"),
        help="Output file path (default: verified_canvas_spec.json)",
    )
    args = parser.parse_args()
    
    print("=" * 60)
    print("Canvas API Specification Generator")
    print("=" * 60)
    print()
    
    # Run verification
    spec = asyncio.run(generate_specification(args.course_id))
    
    # Write output
    output_path = Path(__file__).parent / args.output
    with open(output_path, "w") as f:
        json.dump(spec, f, indent=2, default=str)
    
    print()
    print("=" * 60)
    print("Summary")
    print("=" * 60)
    print(f"  Verified endpoints: {spec['summary']['total_verified']}")
    print(f"  Failed endpoints:   {spec['summary']['total_failed']}")
    print(f"  Output written to:  {output_path}")
    print()
    
    if spec["summary"]["total_failed"] > 0:
        print("Failed endpoints:")
        for endpoint, result in spec["failed_endpoints"].items():
            print(f"  ❌ {endpoint}: {result['error']}")
    
    print()
    print("Next step: Run 'uv run python server.py' to start the MCP server")
    

if __name__ == "__main__":
    main()
