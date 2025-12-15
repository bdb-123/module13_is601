# app/auth/security.py
"""
Authentication security utilities for password hashing and verification.

This module provides secure password hashing using bcrypt through passlib.
All password operations in the application should use these utilities.
"""

from passlib.context import CryptContext
from app.core.config import get_settings

settings = get_settings()

# Configure password hashing context
# Using bcrypt with configurable rounds for security/performance balance
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=settings.BCRYPT_ROUNDS
)


def hash_password(plain: str) -> str:
    """
    Hash a plain-text password using bcrypt.
    
    This function uses the passlib CryptContext with bcrypt hashing.
    The number of bcrypt rounds is configurable via settings.BCRYPT_ROUNDS.
    
    Args:
        plain: The plain-text password to hash
        
    Returns:
        str: The hashed password string (bcrypt hash)
        
    Example:
        >>> hashed = hash_password("MySecurePassword123!")
        >>> print(hashed[:7])
        $2b$12$
    """
    return pwd_context.hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    """
    Verify a plain-text password against a hashed password.
    
    This function uses constant-time comparison to prevent timing attacks.
    It automatically handles bcrypt's salt and rounds parameters.
    
    Args:
        plain: The plain-text password to verify
        hashed: The hashed password to verify against
        
    Returns:
        bool: True if the password matches, False otherwise
        
    Example:
        >>> hashed = hash_password("MyPassword123!")
        >>> verify_password("MyPassword123!", hashed)
        True
        >>> verify_password("WrongPassword", hashed)
        False
    """
    return pwd_context.verify(plain, hashed)


def needs_rehash(hashed: str) -> bool:
    """
    Check if a hashed password needs to be rehashed.
    
    This is useful when you've updated the bcrypt rounds in settings
    and want to upgrade existing password hashes on user login.
    
    Args:
        hashed: The hashed password to check
        
    Returns:
        bool: True if the hash should be updated, False otherwise
        
    Example:
        >>> if verify_password(plain, hashed) and needs_rehash(hashed):
        >>>     new_hash = hash_password(plain)
        >>>     # Update database with new_hash
    """
    return pwd_context.needs_update(hashed)
