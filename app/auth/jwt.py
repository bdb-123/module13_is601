# app/auth/jwt.py
from datetime import datetime, timedelta, timezone
from typing import Any, Optional, Union
from jose import jwt, JWTError, ExpiredSignatureError
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from uuid import UUID
import secrets

from app.core.config import get_settings
from app.auth.redis import add_to_blacklist, is_blacklisted
from app.auth.security import hash_password, verify_password
from app.schemas.token import TokenType
from app.database import get_db
from sqlalchemy.orm import Session
from app.models.user import User

settings = get_settings()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

# Re-export for backward compatibility
get_password_hash = hash_password
__all__ = [
    'hash_password', 'verify_password', 'get_password_hash', 
    'create_token', 'decode_token', 'oauth2_scheme',
    'create_access_token', 'decode_access_token'  # Simple helpers
]

# ============================================================================
# Simple JWT Helpers (Simplified API)
# ============================================================================

def create_access_token(data: dict, expires_minutes: Optional[int] = None) -> str:
    """
    Create a JWT access token with a simplified interface.
    
    Args:
        data: Dictionary of claims to encode in the token (e.g., {"sub": user_id})
        expires_minutes: Optional expiration time in minutes. 
                        Defaults to ACCESS_TOKEN_EXPIRE_MINUTES from settings.
    
    Returns:
        Encoded JWT token string
    
    Example:
        >>> token = create_access_token({"sub": "user123"}, expires_minutes=60)
        >>> token = create_access_token({"sub": "user123", "email": "user@example.com"})
    """
    to_encode = data.copy()
    
    if expires_minutes:
        expire = datetime.now(timezone.utc) + timedelta(minutes=expires_minutes)
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    
    to_encode.update({
        "exp": expire,
        "iat": datetime.now(timezone.utc)
    })
    
    encoded_jwt = jwt.encode(
        to_encode, 
        settings.SECRET_KEY,  # Use the simple SECRET_KEY
        algorithm=settings.ALGORITHM
    )
    return encoded_jwt


def decode_access_token(token: str) -> dict:
    """
    Decode and verify a JWT access token (synchronous version).
    
    Args:
        token: The JWT token string to decode
    
    Returns:
        Dictionary containing the decoded token payload
    
    Raises:
        HTTPException: If token is invalid, expired, or malformed
    
    Example:
        >>> payload = decode_access_token(token)
        >>> user_id = payload["sub"]
    """
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,  # Use the simple SECRET_KEY
            algorithms=[settings.ALGORITHM]
        )
        return payload
        
    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Could not validate token: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )

# ============================================================================
# Advanced JWT Helpers (Full-featured with refresh tokens, blacklisting, etc.)
# ============================================================================

def create_token(
    user_id: Union[str, UUID],
    token_type: TokenType,
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Create a JWT token (access or refresh).
    """
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        if token_type == TokenType.ACCESS:
            expire = datetime.now(timezone.utc) + timedelta(
                minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
            )
        else:
            expire = datetime.now(timezone.utc) + timedelta(
                days=settings.REFRESH_TOKEN_EXPIRE_DAYS
            )

    if isinstance(user_id, UUID):
        user_id = str(user_id)

    to_encode = {
        "sub": user_id,
        "type": token_type.value,
        "exp": expire,
        "iat": datetime.now(timezone.utc),
        "jti": secrets.token_hex(16)
    }

    secret = (
        settings.JWT_SECRET_KEY 
        if token_type == TokenType.ACCESS 
        else settings.JWT_REFRESH_SECRET_KEY
    )

    try:
        return jwt.encode(to_encode, secret, algorithm=settings.ALGORITHM)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Could not create token: {str(e)}"
        )

async def decode_token(
    token: str,
    token_type: TokenType,
    verify_exp: bool = True
) -> dict[str, Any]:
    """
    Decode and verify a JWT token.
    """
    try:
        secret = (
            settings.JWT_SECRET_KEY 
            if token_type == TokenType.ACCESS 
            else settings.JWT_REFRESH_SECRET_KEY
        )
        
        payload = jwt.decode(
            token,
            secret,
            algorithms=[settings.ALGORITHM],
            options={"verify_exp": verify_exp}
        )
        
        if payload.get("type") != token_type.value:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type",
                headers={"WWW-Authenticate": "Bearer"},
            )
            
        if await is_blacklisted(payload["jti"]):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has been revoked",
                headers={"WWW-Authenticate": "Bearer"},
            )
            
        return payload
        
    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """
    Dependency to get current user from access token.
    Returns the actual User model instance.
    """
    try:
        payload = await decode_token(token, TokenType.ACCESS)
        user_id = payload["sub"]
        
        user = db.query(User).filter(User.id == user_id).first()
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
            
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Inactive user"
            )
            
        return user
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )