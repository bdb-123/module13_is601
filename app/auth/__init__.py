# app/auth/__init__.py
"""
Authentication and authorization utilities.

This module provides password hashing, JWT token management,
and authentication dependencies for the application.
"""

from app.auth.security import hash_password, verify_password, needs_rehash
from app.auth.jwt import create_token, decode_token, oauth2_scheme
from app.auth.dependencies import get_current_user, get_current_active_user

__all__ = [
    # Password utilities
    'hash_password',
    'verify_password', 
    'needs_rehash',
    # JWT utilities
    'create_token',
    'decode_token',
    'oauth2_scheme',
    # Dependencies
    'get_current_user',
    'get_current_active_user',
]
