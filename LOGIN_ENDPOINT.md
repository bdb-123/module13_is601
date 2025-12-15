# POST /login Implementation

## Overview
The `/auth/login` endpoint authenticates a user with email/username and password, returning a JWT token upon success.

---

## Endpoint Details

**URL:** `POST /auth/login`  
**Status Code:** `200 OK` (success)  
**Response Model:** `TokenResponse`

---

## Request Body

### Schema: `UserLogin`

```json
{
  "username": "john.doe@example.com",
  "password": "SecurePass123!"
}
```

### Field Details

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `username` | string | ✅ Yes | Email address or username |
| `password` | string | ✅ Yes | User's password |

**Note:** The `username` field accepts EITHER an email address OR a username for flexibility.

---

## Success Response (200 OK)

```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "expires_at": "2025-12-14T12:30:00",
  "user_id": "123e4567-e89b-12d3-a456-426614174000",
  "username": "johndoe",
  "email": "john.doe@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "is_active": true,
  "is_verified": false
}
```

**Response Fields:**
- `access_token`: JWT token for API authentication (30 min expiry)
- `refresh_token`: JWT token for refreshing access token (7 day expiry)
- `token_type`: Always "bearer"
- `expires_at`: Timestamp when access token expires
- `user_id`: User's unique UUID
- `username`: User's username
- `email`: User's email address
- `first_name`: User's first name
- `last_name`: User's last name
- `is_active`: Whether user account is active
- `is_verified`: Whether user email is verified

---

## Error Responses

### 401 Unauthorized - Invalid Credentials

```json
{
  "detail": "Invalid credentials"
}
```

**Trigger Conditions:**
- Email/username not found in database
- Password does not match stored hash
- Account exists but password is incorrect

**Security Note:** Returns same error for invalid email AND invalid password to prevent user enumeration attacks.

---

### 500 Internal Server Error

```json
{
  "detail": "An error occurred during login. Please try again later."
}
```

**Trigger:** Unexpected database or system error
- Actual error logged server-side but not exposed to client

---

## Implementation Flow

```
┌─────────────────────────────────────────────────────────────────┐
│ 1. REQUEST RECEIVED                                             │
│    - FastAPI receives UserLogin schema                         │
│    - Pydantic validates fields                                 │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│ 2. LOOKUP USER (User.authenticate)                              │
│    - Query: SELECT * FROM users                                │
│      WHERE email = ? OR username = ?                           │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│ 3. VERIFY PASSWORD                                              │
│    - If user not found: return None                            │
│    - Compare password with bcrypt hash                         │
│    - If mismatch: return None                                  │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│ 4. UPDATE LAST LOGIN                                            │
│    - Set user.last_login = now()                               │
│    - db.flush() - write to DB without commit                   │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│ 5. GENERATE JWT TOKENS                                          │
│    - Create access token (30 min expiry)                       │
│    - Create refresh token (7 day expiry)                       │
│    - Calculate expires_at timestamp                            │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│ 6. COMMIT TRANSACTION                                            │
│    - db.commit() - persist last_login update                   │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│ 7. RETURN TOKEN RESPONSE (200)                                  │
│    - Include access_token, refresh_token, user data            │
└─────────────────────────────────────────────────────────────────┘
```

---

## Code Implementation

### 1. app/main.py - Login Endpoint

```python
@app.post(
    "/auth/login", 
    response_model=TokenResponse, 
    tags=["auth"],
    responses={
        200: {
            "description": "Login successful - JWT token returned",
            "model": TokenResponse
        },
        401: {
            "description": "Unauthorized - Invalid credentials",
            "content": {
                "application/json": {
                    "example": {"detail": "Invalid credentials"}
                }
            }
        }
    }
)
def login_json(user_login: UserLogin, db: Session = Depends(get_db)):
    """
    Authenticate a user and return JWT tokens.
    
    - **username**: User's email address or username
    - **password**: User's password
    
    Returns access token and refresh token upon successful authentication.
    """
    try:
        # Authenticate user by email or username
        auth_result = User.authenticate(db, user_login.username, user_login.password)
        
        if auth_result is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Commit the last_login update
        user = auth_result["user"]
        db.commit()

        # Ensure expires_at is timezone-aware
        expires_at = auth_result.get("expires_at")
        if expires_at and expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)
        else:
            expires_at = datetime.now(timezone.utc) + timedelta(
                minutes=get_settings().ACCESS_TOKEN_EXPIRE_MINUTES
            )

        return TokenResponse(
            access_token=auth_result["access_token"],
            refresh_token=auth_result["refresh_token"],
            token_type="bearer",
            expires_at=expires_at,
            user_id=user.id,
            username=user.username,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            is_active=user.is_active,
            is_verified=user.is_verified
        )
    
    except HTTPException:
        # Re-raise HTTP exceptions (401 Unauthorized)
        db.rollback()
        raise
    
    except Exception as e:
        # Handle any unexpected errors
        db.rollback()
        print(f"Login error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred during login. Please try again later."
        )
```

**Key Features:**
1. ✅ Accepts email OR username in the `username` field
2. ✅ Returns exactly `"Invalid credentials"` on authentication failure
3. ✅ Returns full `TokenResponse` with JWT tokens on success
4. ✅ Updates `last_login` timestamp
5. ✅ Proper error handling with rollback
6. ✅ Safe error messages (no internal details exposed)

---

### 2. app/models/user.py - authenticate() Method

```python
@classmethod
def authenticate(cls, db, username_or_email: str, password: str):
    """
    Authenticate a user by username/email and password.
    
    Args:
        db: SQLAlchemy database session
        username_or_email: Username or email to authenticate
        password: Password to verify
        
    Returns:
        dict: Authentication result with tokens and user data, or None if authentication fails
    """
    # Lookup user by email OR username
    user = db.query(cls).filter(
        or_(cls.username == username_or_email, cls.email == username_or_email)
    ).first()

    # Verify user exists and password matches
    if not user or not user.verify_password(password):
        return None

    # Update the last_login timestamp
    user.last_login = utcnow()
    db.flush()

    # Generate JWT tokens
    access_token = cls.create_access_token({"sub": str(user.id)})
    refresh_token = cls.create_refresh_token({"sub": str(user.id)})
    expires_at = utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_at": expires_at,
        "user": user
    }
```

**Key Features:**
1. ✅ Accepts email OR username (flexible lookup)
2. ✅ Uses `or_()` for SQL OR condition
3. ✅ Password verification with bcrypt
4. ✅ Returns `None` on failure (not an exception)
5. ✅ Updates `last_login` timestamp
6. ✅ Generates both access and refresh tokens
7. ✅ Returns user object for building response

---

### 3. app/schemas/user.py - UserLogin Schema

```python
class UserLogin(BaseModel):
    """
    Schema for user login.
    Accepts email or username with password for authentication.
    """
    username: str = Field(
        ...,
        min_length=1,  # Allow any length for login
        description="Username or email address"
    )
    password: str = Field(
        ...,
        min_length=1,  # Don't validate password length on login
        description="User's password"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "username": "john.doe@example.com",
                "password": "SecurePass123!"
            }
        }
    )
```

**Key Changes:**
1. ✅ Removed password length validation (only validate on registration)
2. ✅ Removed username length validation (could be email address)
3. ✅ Updated description to clarify "username or email"
4. ✅ Example shows email address usage

---

## Usage Examples

### cURL Example - Login with Email

```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john.doe@example.com",
    "password": "SecurePass123!"
  }'
```

### cURL Example - Login with Username

```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "johndoe",
    "password": "SecurePass123!"
  }'
```

---

### Python Requests Example

```python
import requests

# Login with email
response = requests.post(
    "http://localhost:8000/auth/login",
    json={
        "username": "john.doe@example.com",
        "password": "SecurePass123!"
    }
)

if response.status_code == 200:
    data = response.json()
    access_token = data["access_token"]
    refresh_token = data["refresh_token"]
    
    print(f"✅ Login successful!")
    print(f"Access Token: {access_token[:50]}...")
    print(f"User: {data['first_name']} {data['last_name']}")
    
    # Use token for authenticated requests
    headers = {"Authorization": f"Bearer {access_token}"}
    profile = requests.get("http://localhost:8000/profile", headers=headers)
    
elif response.status_code == 401:
    print(f"❌ {response.json()['detail']}")
else:
    print(f"Error {response.status_code}: {response.json()}")
```

---

### JavaScript Fetch Example

```javascript
// Login with username or email
const response = await fetch('http://localhost:8000/auth/login', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    username: 'john.doe@example.com',  // or 'johndoe'
    password: 'SecurePass123!'
  })
});

if (response.ok) {
  const data = await response.json();
  
  // Store tokens in localStorage
  localStorage.setItem('access_token', data.access_token);
  localStorage.setItem('refresh_token', data.refresh_token);
  localStorage.setItem('user', JSON.stringify({
    id: data.user_id,
    username: data.username,
    email: data.email,
    name: `${data.first_name} ${data.last_name}`
  }));
  
  console.log('✅ Login successful!', data);
  
  // Redirect to dashboard
  window.location.href = '/dashboard';
  
} else if (response.status === 401) {
  const error = await response.json();
  alert(`Login failed: ${error.detail}`);
} else {
  console.error('Unexpected error:', response.status);
}
```

---

### Using the Access Token

```javascript
// Make authenticated API request
const headers = {
  'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
  'Content-Type': 'application/json'
};

const response = await fetch('http://localhost:8000/calculations', {
  method: 'GET',
  headers: headers
});

if (response.status === 401) {
  // Token expired - redirect to login
  localStorage.clear();
  window.location.href = '/login';
}
```

---

## Testing Checklist

- [ ] ✅ Valid login with email returns 200 with JWT token
- [ ] ✅ Valid login with username returns 200 with JWT token
- [ ] ✅ Invalid email returns 401 "Invalid credentials"
- [ ] ✅ Valid email but wrong password returns 401 "Invalid credentials"
- [ ] ✅ Non-existent user returns 401 "Invalid credentials"
- [ ] ✅ Empty password returns 401 "Invalid credentials"
- [ ] ✅ JWT token is valid and can be decoded
- [ ] ✅ Token contains correct user_id in "sub" claim
- [ ] ✅ last_login timestamp is updated in database
- [ ] ✅ Database transaction rolled back on error
- [ ] ✅ Response includes access_token and refresh_token
- [ ] ✅ expires_at is calculated correctly (30 minutes from now)
- [ ] ✅ User data (email, name, etc.) included in response

---

## Security Considerations

1. **Password Verification**: Uses bcrypt constant-time comparison to prevent timing attacks
2. **Error Messages**: Same error for invalid email AND invalid password (prevents user enumeration)
3. **JWT Security**: Tokens use HS256 with secret key from environment
4. **Last Login Tracking**: Records when user last authenticated
5. **Transaction Safety**: Rollback on errors prevents partial updates
6. **No Password Exposure**: Passwords never returned in responses

---

## Comparison: Register vs Login

| Feature | POST /register | POST /login |
|---------|---------------|-------------|
| **Input** | Email, username, password, name | Username/email, password |
| **Validation** | Password strength requirements | No validation (login only) |
| **Success Code** | 201 Created | 200 OK |
| **Error - Duplicate** | 400 "Email already exists" | N/A |
| **Error - Invalid** | 400 validation errors | 401 "Invalid credentials" |
| **Password Handling** | Hash and store | Verify against hash |
| **DB Operation** | INSERT new user | SELECT and UPDATE last_login |
| **Response** | TokenResponse (auto-login) | TokenResponse |

---

## Related Endpoints

- **POST /auth/register** - Create new user account
- **POST /auth/token** - OAuth2 form-based login (for Swagger UI)
- **POST /auth/refresh** - Refresh access token using refresh token
- **POST /auth/logout** - Invalidate tokens
- **GET /profile** - Get current user profile (requires JWT)
