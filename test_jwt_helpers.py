#!/usr/bin/env python3
"""
Demo script for the simplified JWT helper functions.
Tests create_access_token() and decode_access_token().
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app.auth.jwt import create_access_token, decode_access_token
from fastapi import HTTPException
import time

print("=" * 70)
print("JWT Helper Functions Demo")
print("=" * 70)

# Test 1: Create token with default expiration
print("\n📝 Test 1: Create token with default expiration")
print("-" * 70)
token = create_access_token({"sub": "user123", "email": "test@example.com"})
print(f"✅ Token created: {token[:50]}...")
print(f"   Full length: {len(token)} characters")

# Test 2: Decode valid token
print("\n🔓 Test 2: Decode valid token")
print("-" * 70)
try:
    payload = decode_access_token(token)
    print("✅ Token decoded successfully!")
    print(f"   Payload: {payload}")
    print(f"   User ID: {payload['sub']}")
    print(f"   Email: {payload.get('email')}")
    print(f"   Issued at: {payload.get('iat')}")
    print(f"   Expires at: {payload.get('exp')}")
except HTTPException as e:
    print(f"❌ Error: {e.detail}")

# Test 3: Create token with custom expiration
print("\n⏰ Test 3: Create token with custom expiration (60 minutes)")
print("-" * 70)
custom_token = create_access_token(
    {"sub": "admin456", "role": "admin"},
    expires_minutes=60
)
print(f"✅ Custom token created: {custom_token[:50]}...")
decoded = decode_access_token(custom_token)
print(f"   User ID: {decoded['sub']}")
print(f"   Role: {decoded.get('role')}")

# Test 4: Create short-lived token and let it expire
print("\n⌛ Test 4: Create token with 1-second expiration (will expire)")
print("-" * 70)
short_token = create_access_token(
    {"sub": "temp_user"},
    expires_minutes=1/60  # 1 second
)
print(f"✅ Short-lived token created")
print("   Waiting 2 seconds for token to expire...")
time.sleep(2)

try:
    payload = decode_access_token(short_token)
    print(f"❌ Unexpected: Token should have expired but decoded: {payload}")
except HTTPException as e:
    print(f"✅ Expected error caught: {e.detail}")
    print(f"   Status code: {e.status_code}")

# Test 5: Try to decode invalid token
print("\n🚫 Test 5: Decode invalid/malformed token")
print("-" * 70)
try:
    payload = decode_access_token("invalid.token.here")
    print(f"❌ Unexpected: Invalid token should fail but decoded: {payload}")
except HTTPException as e:
    print(f"✅ Expected error caught: {e.detail}")
    print(f"   Status code: {e.status_code}")

# Test 6: Token with various data types
print("\n📦 Test 6: Token with various data types")
print("-" * 70)
complex_data = {
    "sub": "user789",
    "email": "user@example.com",
    "roles": ["admin", "user"],
    "permissions": {"read": True, "write": True, "delete": False},
    "quota": 1000,
    "active": True
}
complex_token = create_access_token(complex_data)
decoded = decode_access_token(complex_token)
print(f"✅ Complex token created and decoded:")
print(f"   User: {decoded['sub']}")
print(f"   Roles: {decoded['roles']}")
print(f"   Permissions: {decoded['permissions']}")
print(f"   Quota: {decoded['quota']}")
print(f"   Active: {decoded['active']}")

print("\n" + "=" * 70)
print("✅ All JWT helper function tests completed!")
print("=" * 70)
print("\n💡 Usage Examples:")
print("   # Create token")
print("   token = create_access_token({'sub': 'user_id'})")
print("   token = create_access_token({'sub': 'user_id'}, expires_minutes=120)")
print("\n   # Decode token")
print("   payload = decode_access_token(token)")
print("   user_id = payload['sub']")
print("=" * 70)
