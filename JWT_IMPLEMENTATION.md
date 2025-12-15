# JWT Helpers Implementation Summary

## Changes Made

### 1. **app/core/config.py** - Added JWT Configuration

```python
class Settings(BaseSettings):
    # ... existing settings ...
    
    # JWT Settings
    # Generate a secure random key for local dev, but should be set in production via env
    SECRET_KEY: str = secrets.token_urlsafe(32)  # Simple name for general use
    JWT_SECRET_KEY: str = "your-super-secret-key-change-this-in-production"  # Access tokens
    JWT_REFRESH_SECRET_KEY: str = "your-refresh-secret-key-change-this-in-production"  # Refresh tokens
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
```

**Key Points:**
- Added `SECRET_KEY` with a secure random default using `secrets.token_urlsafe(32)`
- This generates a different key each time for local development (safe default)
- In production, set `SECRET_KEY` via environment variable (`.env` file)
- `ALGORITHM` set to "HS256" (HMAC with SHA-256)
- Configurable expiration times for access tokens (30 minutes default)

**Environment Variables:**
Set these in your `.env` file for production:
```bash
SECRET_KEY=your-production-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

---

### 2. **app/auth/jwt.py** - Added Simple JWT Helpers

#### **create_access_token(data: dict, expires_minutes: int) -> str**

```python
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
```

**Usage:**
```python
# Create token with default 30-minute expiration
token = create_access_token({"sub": "user_id_123"})

# Create token with custom 2-hour expiration
token = create_access_token(
    {"sub": "user_id_123", "email": "user@example.com"},
    expires_minutes=120
)
```

---

#### **decode_access_token(token: str) -> dict**

```python
def decode_access_token(token: str) -> dict:
    """
    Decode and verify a JWT access token (synchronous version).
    
    Args:
        token: The JWT token string to decode
    
    Returns:
        Dictionary containing the decoded token payload
    
    Raises:
        HTTPException: If token is invalid, expired, or malformed
            - 401 with "Token has expired" if expired
            - 401 with "Could not validate token: ..." if invalid
    
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
```

**Usage:**
```python
from fastapi import HTTPException

try:
    payload = decode_access_token(token)
    user_id = payload["sub"]
    email = payload.get("email")
    print(f"User {user_id} authenticated")
except HTTPException as e:
    print(f"Authentication failed: {e.detail}")
```

---

## Usage Examples

### 1. **Basic Authentication Flow**

```python
from app.auth.jwt import create_access_token, decode_access_token

# Login endpoint - create token after verifying credentials
@app.post("/login")
def login(credentials: LoginData):
    # ... verify username/password ...
    
    # Create access token
    token = create_access_token(
        data={"sub": str(user.id), "email": user.email}
    )
    
    return {"access_token": token, "token_type": "bearer"}
```

### 2. **Protected Endpoint - Verify Token**

```python
from fastapi import Depends, Header

def get_current_user_id(authorization: str = Header(...)):
    # Extract token from "Bearer <token>"
    token = authorization.replace("Bearer ", "")
    
    # Decode and verify
    payload = decode_access_token(token)
    return payload["sub"]

@app.get("/profile")
def get_profile(user_id: str = Depends(get_current_user_id)):
    # user_id is now verified from the token
    return {"user_id": user_id}
```

### 3. **Custom Expiration Times**

```python
# Short-lived token for password reset (15 minutes)
reset_token = create_access_token(
    data={"sub": user.id, "type": "password_reset"},
    expires_minutes=15
)

# Long-lived token for remember-me (7 days = 10080 minutes)
remember_token = create_access_token(
    data={"sub": user.id},
    expires_minutes=10080
)
```

---

## Error Handling

The `decode_access_token` function raises `HTTPException` with appropriate status codes:

| Error | Status Code | Detail |
|-------|-------------|--------|
| Token expired | 401 UNAUTHORIZED | "Token has expired" |
| Invalid signature | 401 UNAUTHORIZED | "Could not validate token: ..." |
| Malformed token | 401 UNAUTHORIZED | "Could not validate token: ..." |

**Example Error Handling:**

```python
from fastapi import HTTPException

def verify_token(token: str):
    try:
        payload = decode_access_token(token)
        return payload
    except HTTPException as e:
        if "expired" in e.detail.lower():
            # Token expired - redirect to login
            return {"error": "session_expired"}
        else:
            # Invalid token
            return {"error": "invalid_token"}
```

---

## Configuration

### Local Development (uses random secret)
The default `SECRET_KEY` is generated randomly each time using `secrets.token_urlsafe(32)`.
This is fine for development but tokens won't survive server restarts.

### Production Setup
Create a `.env` file in your project root:

```bash
# .env
SECRET_KEY=super-secret-production-key-at-least-32-characters
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

**Generate a secure production key:**
```python
import secrets
print(secrets.token_urlsafe(32))
# Example output: "8f4c9b2e1a7d3f6e9b4c8a2d5f7e9b1a3c6e8f2a4d7e9f1b3c5a7e9b2d4f6e8"
```

---

## Testing

Run the demo script to test the JWT helpers:
```bash
python3 test_jwt_helpers.py
```

This will demonstrate:
- Creating tokens with default expiration
- Creating tokens with custom expiration
- Decoding valid tokens
- Handling expired tokens
- Handling invalid tokens
- Encoding complex data structures

---

## API Reference

### `create_access_token(data: dict, expires_minutes: Optional[int] = None) -> str`

**Parameters:**
- `data` (dict): Payload to encode in the token. Should include at minimum `{"sub": user_id}`
- `expires_minutes` (int, optional): Expiration time in minutes. Defaults to `ACCESS_TOKEN_EXPIRE_MINUTES` from config

**Returns:**
- `str`: Encoded JWT token

**Automatically Added Claims:**
- `exp`: Expiration timestamp (UTC)
- `iat`: Issued-at timestamp (UTC)

---

### `decode_access_token(token: str) -> dict`

**Parameters:**
- `token` (str): The JWT token to decode

**Returns:**
- `dict`: Decoded payload containing all claims

**Raises:**
- `HTTPException(401)`: If token is expired, invalid, or malformed

**Returned Claims:**
- All claims from the original `data` parameter
- `exp`: Expiration timestamp
- `iat`: Issued-at timestamp

---

## Security Notes

1. **SECRET_KEY**: Must be kept secret and never committed to version control
2. **HTTPS**: Always use HTTPS in production to prevent token interception
3. **Token Storage**: Store tokens securely (e.g., httpOnly cookies or secure localStorage)
4. **Expiration**: Use short expiration times (15-30 minutes) for access tokens
5. **Refresh Tokens**: For longer sessions, implement refresh tokens separately
6. **Token Rotation**: Consider rotating tokens on each use for maximum security
