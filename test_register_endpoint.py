#!/usr/bin/env python3
"""
Test script for POST /register endpoint
Demonstrates all test cases and error scenarios
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"

def print_section(title):
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)

def test_valid_registration():
    """Test 1: Valid registration returns 201 with JWT token"""
    print_section("Test 1: Valid Registration")
    
    response = requests.post(
        f"{BASE_URL}/auth/register",
        json={
            "email": f"test_{datetime.now().timestamp()}@example.com",
            "username": f"testuser_{int(datetime.now().timestamp())}",
            "first_name": "Test",
            "last_name": "User",
            "password": "SecurePass123!",
            "confirm_password": "SecurePass123!"
        }
    )
    
    print(f"Status Code: {response.status_code}")
    if response.status_code == 201:
        data = response.json()
        print(f"✅ SUCCESS!")
        print(f"   Access Token: {data['access_token'][:50]}...")
        print(f"   Refresh Token: {data['refresh_token'][:50]}...")
        print(f"   Token Type: {data['token_type']}")
        print(f"   User ID: {data['user_id']}")
        print(f"   Username: {data['username']}")
        print(f"   Email: {data['email']}")
        print(f"   Name: {data['first_name']} {data['last_name']}")
        print(f"   Is Active: {data['is_active']}")
        print(f"   Is Verified: {data['is_verified']}")
        return data['access_token']
    else:
        print(f"❌ FAILED: {response.json()}")
        return None

def test_duplicate_email():
    """Test 2: Duplicate email returns 400"""
    print_section("Test 2: Duplicate Email")
    
    # First registration
    email = f"duplicate_{datetime.now().timestamp()}@example.com"
    requests.post(
        f"{BASE_URL}/auth/register",
        json={
            "email": email,
            "username": f"user1_{int(datetime.now().timestamp())}",
            "first_name": "User",
            "last_name": "One",
            "password": "SecurePass123!",
            "confirm_password": "SecurePass123!"
        }
    )
    
    # Try duplicate email with different username
    response = requests.post(
        f"{BASE_URL}/auth/register",
        json={
            "email": email,  # Same email
            "username": f"user2_{int(datetime.now().timestamp())}",  # Different username
            "first_name": "User",
            "last_name": "Two",
            "password": "SecurePass123!",
            "confirm_password": "SecurePass123!"
        }
    )
    
    print(f"Status Code: {response.status_code}")
    if response.status_code == 400:
        error = response.json()
        print(f"✅ Correctly rejected: {error['detail']}")
    else:
        print(f"❌ FAILED: Expected 400, got {response.status_code}")

def test_duplicate_username():
    """Test 3: Duplicate username returns 400"""
    print_section("Test 3: Duplicate Username")
    
    # First registration
    username = f"duplicateuser_{int(datetime.now().timestamp())}"
    requests.post(
        f"{BASE_URL}/auth/register",
        json={
            "email": f"user1_{datetime.now().timestamp()}@example.com",
            "username": username,
            "first_name": "User",
            "last_name": "One",
            "password": "SecurePass123!",
            "confirm_password": "SecurePass123!"
        }
    )
    
    # Try duplicate username with different email
    response = requests.post(
        f"{BASE_URL}/auth/register",
        json={
            "email": f"user2_{datetime.now().timestamp()}@example.com",
            "username": username,  # Same username
            "first_name": "User",
            "last_name": "Two",
            "password": "SecurePass123!",
            "confirm_password": "SecurePass123!"
        }
    )
    
    print(f"Status Code: {response.status_code}")
    if response.status_code == 400:
        error = response.json()
        print(f"✅ Correctly rejected: {error['detail']}")
    else:
        print(f"❌ FAILED: Expected 400, got {response.status_code}")

def test_weak_password_no_uppercase():
    """Test 4: Weak password (no uppercase) returns 400"""
    print_section("Test 4: Weak Password - No Uppercase")
    
    response = requests.post(
        f"{BASE_URL}/auth/register",
        json={
            "email": f"test_{datetime.now().timestamp()}@example.com",
            "username": f"testuser_{int(datetime.now().timestamp())}",
            "first_name": "Test",
            "last_name": "User",
            "password": "weakpass123!",  # No uppercase
            "confirm_password": "weakpass123!"
        }
    )
    
    print(f"Status Code: {response.status_code}")
    if response.status_code in [400, 422]:
        error = response.json()
        print(f"✅ Correctly rejected: {error.get('detail', error)}")
    else:
        print(f"❌ FAILED: Expected 400/422, got {response.status_code}")

def test_weak_password_no_digit():
    """Test 5: Weak password (no digit) returns 400"""
    print_section("Test 5: Weak Password - No Digit")
    
    response = requests.post(
        f"{BASE_URL}/auth/register",
        json={
            "email": f"test_{datetime.now().timestamp()}@example.com",
            "username": f"testuser_{int(datetime.now().timestamp())}",
            "first_name": "Test",
            "last_name": "User",
            "password": "WeakPassword!",  # No digit
            "confirm_password": "WeakPassword!"
        }
    )
    
    print(f"Status Code: {response.status_code}")
    if response.status_code in [400, 422]:
        error = response.json()
        print(f"✅ Correctly rejected: {error.get('detail', error)}")
    else:
        print(f"❌ FAILED: Expected 400/422, got {response.status_code}")

def test_password_too_short():
    """Test 6: Password too short returns 400"""
    print_section("Test 6: Password Too Short")
    
    response = requests.post(
        f"{BASE_URL}/auth/register",
        json={
            "email": f"test_{datetime.now().timestamp()}@example.com",
            "username": f"testuser_{int(datetime.now().timestamp())}",
            "first_name": "Test",
            "last_name": "User",
            "password": "Short1!",  # Only 7 chars
            "confirm_password": "Short1!"
        }
    )
    
    print(f"Status Code: {response.status_code}")
    if response.status_code in [400, 422]:
        error = response.json()
        print(f"✅ Correctly rejected: {error.get('detail', error)}")
    else:
        print(f"❌ FAILED: Expected 400/422, got {response.status_code}")

def test_password_mismatch():
    """Test 7: Password mismatch returns 400"""
    print_section("Test 7: Password Mismatch")
    
    response = requests.post(
        f"{BASE_URL}/auth/register",
        json={
            "email": f"test_{datetime.now().timestamp()}@example.com",
            "username": f"testuser_{int(datetime.now().timestamp())}",
            "first_name": "Test",
            "last_name": "User",
            "password": "SecurePass123!",
            "confirm_password": "DifferentPass123!"  # Mismatch
        }
    )
    
    print(f"Status Code: {response.status_code}")
    if response.status_code in [400, 422]:
        error = response.json()
        print(f"✅ Correctly rejected: {error.get('detail', error)}")
    else:
        print(f"❌ FAILED: Expected 400/422, got {response.status_code}")

def test_invalid_email():
    """Test 8: Invalid email format returns 422"""
    print_section("Test 8: Invalid Email Format")
    
    response = requests.post(
        f"{BASE_URL}/auth/register",
        json={
            "email": "not-a-valid-email",  # Invalid format
            "username": f"testuser_{int(datetime.now().timestamp())}",
            "first_name": "Test",
            "last_name": "User",
            "password": "SecurePass123!",
            "confirm_password": "SecurePass123!"
        }
    )
    
    print(f"Status Code: {response.status_code}")
    if response.status_code == 422:
        error = response.json()
        print(f"✅ Correctly rejected with validation error")
        if 'detail' in error and isinstance(error['detail'], list):
            for err in error['detail']:
                print(f"   - {err.get('msg', err)}")
    else:
        print(f"❌ FAILED: Expected 422, got {response.status_code}")

def test_missing_required_field():
    """Test 9: Missing required field returns 422"""
    print_section("Test 9: Missing Required Field")
    
    response = requests.post(
        f"{BASE_URL}/auth/register",
        json={
            "email": f"test_{datetime.now().timestamp()}@example.com",
            # Missing username
            "first_name": "Test",
            "last_name": "User",
            "password": "SecurePass123!",
            "confirm_password": "SecurePass123!"
        }
    )
    
    print(f"Status Code: {response.status_code}")
    if response.status_code == 422:
        error = response.json()
        print(f"✅ Correctly rejected with validation error")
        if 'detail' in error and isinstance(error['detail'], list):
            for err in error['detail']:
                print(f"   - Field: {err.get('loc', 'N/A')}, {err.get('msg', err)}")
    else:
        print(f"❌ FAILED: Expected 422, got {response.status_code}")

def test_use_token(token):
    """Test 10: Use JWT token to access protected endpoint"""
    if not token:
        print("\n⚠️  Skipping token test - no valid token available")
        return
    
    print_section("Test 10: Use JWT Token for Protected Endpoint")
    
    # Try to access a protected endpoint with the token
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/profile", headers=headers)
    
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        print(f"✅ Token works! Accessed protected endpoint")
        print(f"   Response: {response.json()}")
    elif response.status_code == 404:
        print(f"ℹ️  Endpoint doesn't exist (expected), but token was accepted")
    else:
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")

if __name__ == "__main__":
    print("\n" + "█" * 70)
    print("█" + " " * 68 + "█")
    print("█" + "  POST /register Endpoint Tests".center(68) + "█")
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
    
    # Run all tests
    token = test_valid_registration()
    test_duplicate_email()
    test_duplicate_username()
    test_weak_password_no_uppercase()
    test_weak_password_no_digit()
    test_password_too_short()
    test_password_mismatch()
    test_invalid_email()
    test_missing_required_field()
    test_use_token(token)
    
    print("\n" + "=" * 70)
    print("✅ All tests completed!")
    print("=" * 70)
