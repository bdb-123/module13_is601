#!/usr/bin/env python3
"""
Test script for POST /login endpoint
Demonstrates login scenarios and token usage
"""

import requests
from datetime import datetime

BASE_URL = "http://localhost:8000"

def print_section(title):
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)

def register_test_user():
    """Helper: Register a test user for login tests"""
    print_section("Setup: Register Test User")
    
    timestamp = int(datetime.now().timestamp())
    email = f"logintest_{timestamp}@example.com"
    username = f"logintest_{timestamp}"
    password = "TestPass123!"
    
    response = requests.post(
        f"{BASE_URL}/auth/register",
        json={
            "email": email,
            "username": username,
            "first_name": "Login",
            "last_name": "Test",
            "password": password,
            "confirm_password": password
        }
    )
    
    if response.status_code == 201:
        print(f"✅ Test user registered")
        print(f"   Email: {email}")
        print(f"   Username: {username}")
        print(f"   Password: {password}")
        return {"email": email, "username": username, "password": password}
    else:
        print(f"❌ Failed to register test user: {response.json()}")
        return None

def test_login_with_email(credentials):
    """Test 1: Login with email address"""
    print_section("Test 1: Login with Email")
    
    response = requests.post(
        f"{BASE_URL}/auth/login",
        json={
            "username": credentials["email"],  # Field is 'username' but accepts email
            "password": credentials["password"]
        }
    )
    
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print("✅ SUCCESS - Login with email!")
        print(f"   Access Token: {data['access_token'][:50]}...")
        print(f"   Refresh Token: {data['refresh_token'][:50]}...")
        print(f"   Token Type: {data['token_type']}")
        print(f"   Expires At: {data['expires_at']}")
        print(f"   User ID: {data['user_id']}")
        print(f"   Username: {data['username']}")
        print(f"   Email: {data['email']}")
        print(f"   Name: {data['first_name']} {data['last_name']}")
        return data['access_token']
    else:
        print(f"❌ FAILED: {response.json()}")
        return None

def test_login_with_username(credentials):
    """Test 2: Login with username"""
    print_section("Test 2: Login with Username")
    
    response = requests.post(
        f"{BASE_URL}/auth/login",
        json={
            "username": credentials["username"],
            "password": credentials["password"]
        }
    )
    
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print("✅ SUCCESS - Login with username!")
        print(f"   Access Token: {data['access_token'][:50]}...")
        print(f"   User: {data['username']}")
        return data['access_token']
    else:
        print(f"❌ FAILED: {response.json()}")
        return None

def test_invalid_email():
    """Test 3: Invalid email returns 401 'Invalid credentials'"""
    print_section("Test 3: Invalid Email")
    
    response = requests.post(
        f"{BASE_URL}/auth/login",
        json={
            "username": "nonexistent@example.com",
            "password": "SomePassword123!"
        }
    )
    
    print(f"Status Code: {response.status_code}")
    if response.status_code == 401:
        error = response.json()
        print(f"✅ Correctly rejected: {error['detail']}")
        if error['detail'] == "Invalid credentials":
            print("   ✓ Error message matches specification")
        else:
            print(f"   ⚠️  Expected 'Invalid credentials', got '{error['detail']}'")
    else:
        print(f"❌ FAILED: Expected 401, got {response.status_code}")

def test_wrong_password(credentials):
    """Test 4: Valid email but wrong password returns 401"""
    print_section("Test 4: Valid Email, Wrong Password")
    
    response = requests.post(
        f"{BASE_URL}/auth/login",
        json={
            "username": credentials["email"],
            "password": "WrongPassword123!"
        }
    )
    
    print(f"Status Code: {response.status_code}")
    if response.status_code == 401:
        error = response.json()
        print(f"✅ Correctly rejected: {error['detail']}")
        if error['detail'] == "Invalid credentials":
            print("   ✓ Error message matches specification")
        else:
            print(f"   ⚠️  Expected 'Invalid credentials', got '{error['detail']}'")
    else:
        print(f"❌ FAILED: Expected 401, got {response.status_code}")

def test_empty_password(credentials):
    """Test 5: Empty password returns 401"""
    print_section("Test 5: Empty Password")
    
    response = requests.post(
        f"{BASE_URL}/auth/login",
        json={
            "username": credentials["email"],
            "password": ""
        }
    )
    
    print(f"Status Code: {response.status_code}")
    if response.status_code in [401, 422]:
        error = response.json()
        print(f"✅ Correctly rejected: {error.get('detail', error)}")
    else:
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")

def test_case_sensitivity(credentials):
    """Test 6: Email is case-insensitive (or case-sensitive based on implementation)"""
    print_section("Test 6: Email Case Sensitivity")
    
    # Try with uppercase email
    email_upper = credentials["email"].upper()
    response = requests.post(
        f"{BASE_URL}/auth/login",
        json={
            "username": email_upper,
            "password": credentials["password"]
        }
    )
    
    print(f"Original Email: {credentials['email']}")
    print(f"Uppercase Email: {email_upper}")
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        print("✅ Email is case-insensitive")
    elif response.status_code == 401:
        print("ℹ️  Email is case-sensitive")
    else:
        print(f"Status: {response.status_code}")

def test_token_validity(token):
    """Test 7: Verify JWT token structure and claims"""
    if not token:
        print("\n⚠️  Skipping token validity test - no token available")
        return
    
    print_section("Test 7: JWT Token Validity")
    
    # Decode token (without verification for inspection)
    import base64
    import json
    
    try:
        # Split token into parts
        parts = token.split('.')
        if len(parts) != 3:
            print("❌ Invalid JWT format - should have 3 parts")
            return
        
        # Decode payload (add padding if needed)
        payload_b64 = parts[1]
        padding = 4 - len(payload_b64) % 4
        if padding != 4:
            payload_b64 += '=' * padding
        
        payload_json = base64.urlsafe_b64decode(payload_b64)
        payload = json.loads(payload_json)
        
        print("✅ Token decoded successfully")
        print(f"   Subject (user_id): {payload.get('sub')}")
        print(f"   Token Type: {payload.get('type')}")
        print(f"   Issued At: {payload.get('iat')}")
        print(f"   Expires: {payload.get('exp')}")
        print(f"   JTI: {payload.get('jti', 'N/A')}")
        
        # Check required claims
        if 'sub' in payload:
            print("   ✓ 'sub' claim present (user ID)")
        if 'exp' in payload:
            print("   ✓ 'exp' claim present (expiration)")
        if 'iat' in payload:
            print("   ✓ 'iat' claim present (issued at)")
            
    except Exception as e:
        print(f"❌ Failed to decode token: {str(e)}")

def test_use_token_for_api(token):
    """Test 8: Use token to access protected endpoint"""
    if not token:
        print("\n⚠️  Skipping API test - no token available")
        return
    
    print_section("Test 8: Use Token for Protected API Call")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Try to access calculations endpoint (likely requires auth)
    response = requests.get(f"{BASE_URL}/calculations", headers=headers)
    
    print(f"Request: GET /calculations")
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        print("✅ Token accepted - API call successful")
        data = response.json()
        print(f"   Response: {data}")
    elif response.status_code == 401:
        print("⚠️  Token rejected or endpoint requires different auth")
    elif response.status_code == 404:
        print("ℹ️  Endpoint not found (expected)")
    else:
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")

def test_missing_fields():
    """Test 9: Missing required fields returns 422"""
    print_section("Test 9: Missing Required Fields")
    
    response = requests.post(
        f"{BASE_URL}/auth/login",
        json={
            "username": "test@example.com"
            # Missing password
        }
    )
    
    print(f"Status Code: {response.status_code}")
    if response.status_code == 422:
        error = response.json()
        print("✅ Correctly rejected with validation error")
        if 'detail' in error and isinstance(error['detail'], list):
            for err in error['detail']:
                print(f"   - Field: {err.get('loc', 'N/A')}, {err.get('msg', err)}")
    else:
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")

if __name__ == "__main__":
    print("\n" + "█" * 70)
    print("█" + " " * 68 + "█")
    print("█" + "  POST /login Endpoint Tests".center(68) + "█")
    print("█" + " " * 68 + "█")
    print("█" * 70)
    
    print("\n⚠️  Make sure the server is running: uvicorn app.main:app --reload")
    print("⚠️  Run this from the project root directory")
    
    try:
        # Test if server is running
        response = requests.get(f"{BASE_URL}/health", timeout=2)
        if response.status_code != 200:
            print("\n❌ Server not responding correctly!")
            exit(1)
    except requests.exceptions.ConnectionError:
        print(f"\n❌ Cannot connect to {BASE_URL}")
        print("   Make sure the server is running!")
        exit(1)
    
    # Setup: Register a test user
    credentials = register_test_user()
    if not credentials:
        print("\n❌ Cannot proceed without test user")
        exit(1)
    
    # Run all tests
    token = test_login_with_email(credentials)
    test_login_with_username(credentials)
    test_invalid_email()
    test_wrong_password(credentials)
    test_empty_password(credentials)
    test_case_sensitivity(credentials)
    test_token_validity(token)
    test_use_token_for_api(token)
    test_missing_fields()
    
    print("\n" + "=" * 70)
    print("✅ All login tests completed!")
    print("=" * 70)
    print("\n💡 Quick Test Commands:")
    print(f"   # Login with email:")
    print(f'   curl -X POST "{BASE_URL}/auth/login" \\')
    print(f'     -H "Content-Type: application/json" \\')
    print(f'     -d \'{{"username": "{credentials["email"]}", "password": "{credentials["password"]}"}}\'')
    print(f"\n   # Login with username:")
    print(f'   curl -X POST "{BASE_URL}/auth/login" \\')
    print(f'     -H "Content-Type: application/json" \\')
    print(f'     -d \'{{"username": "{credentials["username"]}", "password": "{credentials["password"]}"}}\'')
    print("=" * 70)
