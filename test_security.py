#!/usr/bin/env python3
"""
Quick test to demonstrate the auth security utilities.
This shows how to use hash_password and verify_password.
"""

from app.auth.security import hash_password, verify_password, needs_rehash

def test_password_hashing():
    """Test password hashing and verification."""
    
    # Test 1: Hash a password
    plain_password = "MySecurePassword123!"
    hashed = hash_password(plain_password)
    
    print("🔐 Password Hashing Test")
    print("=" * 60)
    print(f"Plain password: {plain_password}")
    print(f"Hashed password: {hashed}")
    print(f"Hash starts with: {hashed[:7]} (bcrypt identifier)")
    print()
    
    # Test 2: Verify correct password
    print("✅ Verification Test - Correct Password")
    print("=" * 60)
    is_valid = verify_password(plain_password, hashed)
    print(f"verify_password('{plain_password}', hashed) = {is_valid}")
    assert is_valid, "Password verification should return True for correct password"
    print("✅ PASSED: Correct password verified successfully")
    print()
    
    # Test 3: Verify incorrect password
    print("❌ Verification Test - Incorrect Password")
    print("=" * 60)
    wrong_password = "WrongPassword123!"
    is_valid = verify_password(wrong_password, hashed)
    print(f"verify_password('{wrong_password}', hashed) = {is_valid}")
    assert not is_valid, "Password verification should return False for incorrect password"
    print("✅ PASSED: Incorrect password rejected successfully")
    print()
    
    # Test 4: Check if rehash is needed
    print("🔄 Rehash Check Test")
    print("=" * 60)
    needs_update = needs_rehash(hashed)
    print(f"needs_rehash(hashed) = {needs_update}")
    print("ℹ️  Returns True if bcrypt rounds have been increased in settings")
    print()
    
    # Test 5: Multiple hashes are different (salt)
    print("🎲 Salt Uniqueness Test")
    print("=" * 60)
    hash1 = hash_password(plain_password)
    hash2 = hash_password(plain_password)
    print(f"Hash 1: {hash1[:30]}...")
    print(f"Hash 2: {hash2[:30]}...")
    print(f"Are hashes different? {hash1 != hash2}")
    assert hash1 != hash2, "Each hash should have a unique salt"
    print("✅ PASSED: Each hash uses a unique salt")
    print()
    
    print("=" * 60)
    print("✅ ALL TESTS PASSED!")
    print("=" * 60)
    print()
    print("Usage Examples:")
    print("-" * 60)
    print("# Hash a password when creating a user:")
    print("hashed = hash_password(user_password)")
    print()
    print("# Verify password during login:")
    print("if verify_password(login_password, stored_hash):")
    print("    # Login successful")
    print()
    print("# Check if password needs rehashing (e.g., after changing BCRYPT_ROUNDS):")
    print("if verify_password(password, hash) and needs_rehash(hash):")
    print("    new_hash = hash_password(password)")
    print("    # Update database with new_hash")


if __name__ == "__main__":
    test_password_hashing()
