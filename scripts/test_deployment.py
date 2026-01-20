#!/usr/bin/env python3
"""
Test script to verify Paste Server deployment
Checks all critical functionality
"""
import sys
import time
import requests
from typing import Dict, Any


BASE_URL = "http://localhost"
PASSWORD = None  # Will be prompted


def test_health() -> bool:
    """Test health endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health check passed: {data}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False


def test_login(password: str) -> tuple[bool, requests.Session]:
    """Test login endpoint"""
    session = requests.Session()
    try:
        response = session.post(
            f"{BASE_URL}/api/login",
            json={"password": password},
            timeout=5
        )
        if response.status_code == 200:
            print("✅ Login successful")
            return True, session
        else:
            print(f"❌ Login failed: {response.status_code} - {response.text}")
            return False, session
    except Exception as e:
        print(f"❌ Login error: {e}")
        return False, session


def test_create_paste(session: requests.Session) -> tuple[bool, int]:
    """Test creating a paste"""
    try:
        test_content = f"Test paste created at {time.time()}"
        response = session.post(
            f"{BASE_URL}/api/paste",
            json={"content": test_content},
            timeout=5
        )
        if response.status_code == 201:
            data = response.json()
            paste_id = data.get('id')
            print(f"✅ Paste created successfully (ID: {paste_id})")
            return True, paste_id
        else:
            print(f"❌ Create paste failed: {response.status_code} - {response.text}")
            return False, 0
    except Exception as e:
        print(f"❌ Create paste error: {e}")
        return False, 0


def test_get_pastes(session: requests.Session) -> bool:
    """Test getting paste list"""
    try:
        response = session.get(f"{BASE_URL}/api/pastes?limit=10&offset=0", timeout=5)
        if response.status_code == 200:
            data = response.json()
            count = len(data.get('pastes', []))
            total = data.get('total', 0)
            print(f"✅ Retrieved pastes successfully ({count} items, {total} total)")
            return True
        else:
            print(f"❌ Get pastes failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Get pastes error: {e}")
        return False


def test_delete_paste(session: requests.Session, paste_id: int) -> bool:
    """Test deleting a paste"""
    try:
        response = session.delete(f"{BASE_URL}/api/paste/{paste_id}", timeout=5)
        if response.status_code == 200:
            print(f"✅ Paste deleted successfully (ID: {paste_id})")
            return True
        else:
            print(f"❌ Delete paste failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Delete paste error: {e}")
        return False


def test_rate_limiting() -> bool:
    """Test rate limiting on login endpoint"""
    print("\n🔒 Testing rate limiting (may take a moment)...")
    try:
        # Make 6 rapid login attempts (limit is 5)
        for i in range(6):
            response = requests.post(
                f"{BASE_URL}/api/login",
                json={"password": "wrong_password"},
                timeout=5
            )
            if i < 5:
                if response.status_code != 401:
                    print(f"❌ Expected 401, got {response.status_code}")
                    return False
            else:
                # 6th request should be rate limited
                if response.status_code == 429:
                    print("✅ Rate limiting working correctly")
                    return True
                else:
                    print(f"❌ Expected 429 on 6th request, got {response.status_code}")
                    return False
        return False
    except Exception as e:
        print(f"❌ Rate limiting test error: {e}")
        return False


def main() -> None:
    print("=== Paste Server Deployment Test ===\n")

    # Get password
    global PASSWORD
    if len(sys.argv) > 1:
        PASSWORD = sys.argv[1]
    else:
        from getpass import getpass
        PASSWORD = getpass("Enter password: ")

    results: Dict[str, bool] = {}

    # Run tests
    print("\n🧪 Running tests...\n")

    # Test 1: Health check
    results['health'] = test_health()
    print()

    # Test 2: Login
    login_success, session = test_login(PASSWORD)
    results['login'] = login_success
    print()

    if not login_success:
        print("❌ Cannot proceed without login. Exiting.")
        sys.exit(1)

    # Test 3: Create paste
    create_success, paste_id = test_create_paste(session)
    results['create_paste'] = create_success
    print()

    # Test 4: Get pastes
    results['get_pastes'] = test_get_pastes(session)
    print()

    # Test 5: Delete paste
    if create_success:
        results['delete_paste'] = test_delete_paste(session, paste_id)
        print()

    # Test 6: Rate limiting
    results['rate_limiting'] = test_rate_limiting()

    # Summary
    print("\n" + "="*50)
    print("📊 Test Summary")
    print("="*50)

    total = len(results)
    passed = sum(1 for v in results.values() if v)

    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")

    print("="*50)
    print(f"Result: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 All tests passed! Deployment is working correctly.")
        sys.exit(0)
    else:
        print("\n⚠️  Some tests failed. Check logs and configuration.")
        sys.exit(1)


if __name__ == '__main__':
    main()
