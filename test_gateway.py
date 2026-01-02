"""
Test script for the API Gateway.

Run the gateway first: uvicorn gateway:app --reload
Then run this script: python test_gateway.py
"""

import httpx
import json
import sys

BASE_URL = "http://127.0.0.1:8000"

# Test API keys
PREMIUM_KEY = "premium-key-001"
BASIC_KEY = "basic-key-002"
SOCIAL_KEY = "social-key-003"
INVALID_KEY = "invalid-key-999"


def print_response(name: str, response: httpx.Response):
    """Pretty print a response."""
    print(f"\n{'='*60}")
    print(f"TEST: {name}")
    print(f"{'='*60}")
    print(f"Status: {response.status_code}")
    try:
        data = response.json()
        output = json.dumps(data, indent=2)
        # Truncate long responses
        if len(output) > 500:
            output = output[:500] + "\n  ... (truncated)"
        print(f"Response: {output}")
    except:
        print(f"Response: {response.text[:500]}")
    print()


def test_health(client):
    """Test health endpoint."""
    r = client.get(f"{BASE_URL}/health")
    print_response("Health Check (no auth required)", r)
    return r.status_code == 200


def test_info(client):
    """Test gateway info endpoint."""
    r = client.get(f"{BASE_URL}/info")
    print_response("Gateway Info (no auth required)", r)
    return r.status_code == 200


def test_missing_api_key(client):
    """Test missing API key returns 401."""
    r = client.get(f"{BASE_URL}/api/posts")
    print_response("Missing API Key (expect 401)", r)
    return r.status_code == 401


def test_invalid_api_key(client):
    """Test invalid API key returns 401."""
    r = client.get(f"{BASE_URL}/api/posts", headers={"X-API-Key": INVALID_KEY})
    print_response("Invalid API Key (expect 401)", r)
    return r.status_code == 401


def test_premium_posts(client):
    """Test premium partner can get posts."""
    r = client.get(f"{BASE_URL}/api/posts?_limit=2", headers={"X-API-Key": PREMIUM_KEY})
    print_response("Premium Partner - Get Posts (expect 200)", r)
    return r.status_code == 200


def test_premium_todos(client):
    """Test premium partner can get todos."""
    r = client.get(f"{BASE_URL}/api/todos?_limit=2", headers={"X-API-Key": PREMIUM_KEY})
    print_response("Premium Partner - Get Todos (expect 200)", r)
    return r.status_code == 200


def test_basic_posts(client):
    """Test basic partner can get posts."""
    r = client.get(f"{BASE_URL}/api/posts?_limit=2", headers={"X-API-Key": BASIC_KEY})
    print_response("Basic Partner - Get Posts (expect 200)", r)
    return r.status_code == 200


def test_basic_todos_denied(client):
    """Test basic partner cannot get todos."""
    r = client.get(f"{BASE_URL}/api/todos", headers={"X-API-Key": BASIC_KEY})
    print_response("Basic Partner - Get Todos (expect 403 FORBIDDEN)", r)
    return r.status_code == 403


def test_social_comments(client):
    """Test social partner can get comments."""
    r = client.get(f"{BASE_URL}/api/comments?_limit=2", headers={"X-API-Key": SOCIAL_KEY})
    print_response("Social Partner - Get Comments (expect 200)", r)
    return r.status_code == 200


def test_social_users_denied(client):
    """Test social partner cannot get users."""
    r = client.get(f"{BASE_URL}/api/users", headers={"X-API-Key": SOCIAL_KEY})
    print_response("Social Partner - Get Users (expect 403 FORBIDDEN)", r)
    return r.status_code == 403


def test_partner_info(client):
    """Test partner info endpoint."""
    r = client.get(f"{BASE_URL}/me", headers={"X-API-Key": PREMIUM_KEY})
    print_response("Get Partner Info (/me)", r)
    return r.status_code == 200


def test_create_post(client):
    """Test creating a post."""
    r = client.post(
        f"{BASE_URL}/api/posts",
        headers={"X-API-Key": PREMIUM_KEY, "Content-Type": "application/json"},
        json={"title": "Test Post", "body": "This is a test", "userId": 1}
    )
    print_response("Create Post (POST request)", r)
    return r.status_code == 201


def test_get_user_by_id(client):
    """Test getting user by ID."""
    r = client.get(f"{BASE_URL}/api/users/1", headers={"X-API-Key": PREMIUM_KEY})
    print_response("Get User by ID (/api/users/1)", r)
    return r.status_code == 200


def test_admin_stats(client):
    """Test admin stats endpoint."""
    r = client.get(f"{BASE_URL}/admin/stats", headers={"X-API-Key": PREMIUM_KEY})
    print_response("Admin Stats", r)
    return r.status_code == 200


def test_admin_logs(client):
    """Test admin logs endpoint."""
    r = client.get(f"{BASE_URL}/admin/logs?limit=5", headers={"X-API-Key": PREMIUM_KEY})
    print_response("Admin Logs (last 5)", r)
    return r.status_code == 200


def main():
    tests = [
        ("Health Check", test_health),
        ("Gateway Info", test_info),
        ("Missing API Key", test_missing_api_key),
        ("Invalid API Key", test_invalid_api_key),
        ("Premium - Posts", test_premium_posts),
        ("Premium - Todos", test_premium_todos),
        ("Basic - Posts", test_basic_posts),
        ("Basic - Todos Denied", test_basic_todos_denied),
        ("Social - Comments", test_social_comments),
        ("Social - Users Denied", test_social_users_denied),
        ("Partner Info", test_partner_info),
        ("Create Post", test_create_post),
        ("Get User by ID", test_get_user_by_id),
        ("Admin Stats", test_admin_stats),
        ("Admin Logs", test_admin_logs),
    ]
    
    passed = 0
    failed = 0
    
    with httpx.Client(timeout=30) as client:
        for name, test_func in tests:
            try:
                if test_func(client):
                    passed += 1
                    print(f"✅ PASSED: {name}")
                else:
                    failed += 1
                    print(f"❌ FAILED: {name}")
            except httpx.ConnectError:
                print(f"\n❌ ERROR: Cannot connect to the gateway!")
                print(f"   Make sure to run: uvicorn gateway:app --reload\n")
                sys.exit(1)
            except Exception as e:
                failed += 1
                print(f"❌ FAILED: {name} - {e}")
    
    print(f"\n{'='*60}")
    print(f"RESULTS: {passed} passed, {failed} failed")
    print(f"{'='*60}\n")
    
    return failed == 0


if __name__ == "__main__":
    print("\n" + "🧪 API GATEWAY TEST SUITE ".center(60, "="))
    print("Make sure the gateway is running: uvicorn gateway:app --reload\n")
    
    success = main()
    if success:
        print(" ✅ ALL TESTS PASSED ".center(60, "=") + "\n")
    else:
        print(" ⚠️  SOME TESTS FAILED ".center(60, "=") + "\n")
        sys.exit(1)
