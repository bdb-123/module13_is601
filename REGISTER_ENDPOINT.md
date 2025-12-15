# POST /register Implementation

## Overview
The `/auth/register` endpoint registers a new user and returns a JWT access token for immediate authentication.

---

## Endpoint Details

**URL:** `POST /auth/register`  
**Status Code:** `201 Created` (success)  
**Response Model:** `TokenResponse`

---

## Request Body

### Schema: `UserCreate` (or `UserRegister`)

```json
{
  "email": "john.doe@example.com",
  "username": "johndoe",
  "first_name": "John",
  "last_name": "Doe",
  "password": "SecurePass123!",
  "confirm_password": "SecurePass123!"
}
```

### Field Validations

| Field | Type | Required | Validation Rules |
|-------|------|----------|------------------|
| `email` | EmailStr | ✅ Yes | Valid email format, must be unique |
| `username` | string | ✅ Yes | 3-50 characters, must be unique |
| `first_name` | string | ✅ Yes | 1-50 characters |
| `last_name` | string | ✅ Yes | 1-50 characters |
| `password` | string | ✅ Yes | Min 8 chars, uppercase, lowercase, digit |
| `confirm_password` | string | ❌ Optional | Must match password if provided |

---

## Success Response (201 Created)

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

---

## Error Responses

### 400 Bad Request - Duplicate Email

```json
{
  "detail": "Email already exists"
}
```

**Trigger:** Email is already registered in the database

---

### 400 Bad Request - Duplicate Username

```json
{
  "detail": "Username already exists"
}
```

**Trigger:** Username is already taken

---

### 400 Bad Request - Weak Password

```json
{
  "detail": "Password must contain at least one uppercase letter"
}
```

**Trigger:** Password doesn't meet strength requirements
- Missing uppercase letter
- Missing lowercase letter
- Missing digit
- Less than 8 characters

---

### 400 Bad Request - Password Mismatch

```json
{
  "detail": "Passwords do not match"
}
```

**Trigger:** `password` and `confirm_password` don't match

---

### 422 Unprocessable Entity - Validation Error

```json
{
  "detail": [
    {
      "type": "string_too_short",
      "loc": ["body", "username"],
      "msg": "String should have at least 3 characters",
      "input": "ab",
      "ctx": {"min_length": 3}
    }
  ]
}
```

**Trigger:** Pydantic validation fails (invalid email format, field too short, etc.)

---

### 500 Internal Server Error

```json
{
  "detail": "An error occurred during registration. Please try again later."
}
```

**Trigger:** Unexpected database error or system failure
- Note: Actual error is logged server-side but not exposed to client

---

## Implementation Flow

```
┌─────────────────────────────────────────────────────────────────┐
│ 1. REQUEST RECEIVED                                             │
│    - FastAPI receives UserCreate schema                        │
│    - Pydantic validates all fields                             │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│ 2. DUPLICATE EMAIL CHECK                                        │
│    - Query: SELECT * FROM users WHERE email = ?                │
│    - If found: HTTPException(400, "Email already exists")      │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│ 3. DUPLICATE USERNAME CHECK                                     │
│    - Query: SELECT * FROM users WHERE username = ?             │
│    - If found: HTTPException(400, "Username already exists")   │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│ 4. USER REGISTRATION (User.register)                            │
│    - Hash password using bcrypt                                │
│    - Create User instance                                      │
│    - Add to database session                                   │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│ 5. DATABASE COMMIT                                              │
│    - db.commit() - persist user to database                    │
│    - db.refresh(user) - reload user with generated ID          │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│ 6. GENERATE JWT TOKENS                                          │
│    - Create access token (30 min expiry)                       │
│    - Create refresh token (7 day expiry)                       │
│    - Calculate expires_at timestamp                            │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│ 7. RETURN TOKEN RESPONSE (201)                                  │
│    - Include access_token, refresh_token, user data            │
│    - Client can immediately use token for authentication       │
└─────────────────────────────────────────────────────────────────┘
```

---

## Database Session Handling

The endpoint implements proper transaction management:

### Success Path
```python
try:
    # Check duplicates
    # Register user
    db.commit()        # ← Persist changes
    db.refresh(user)   # ← Reload with generated fields
    # Generate tokens
    return TokenResponse(...)
```

### Error Path - HTTP Exceptions
```python
except HTTPException:
    db.rollback()  # ← Undo any pending changes
    raise          # ← Re-raise the exception
```

### Error Path - Validation Errors
```python
except ValueError as e:
    db.rollback()  # ← Undo any pending changes
    raise HTTPException(400, str(e))
```

### Error Path - Unexpected Errors
```python
except Exception as e:
    db.rollback()  # ← Undo any pending changes
    print(f"Error: {e}")  # ← Log for debugging
    raise HTTPException(500, "An error occurred...")  # ← Safe message
```

---

## Code Changes

### 1. app/main.py - Updated Register Endpoint

```python
@app.post(
    "/auth/register", 
    response_model=TokenResponse,  # ← Changed from UserResponse
    status_code=status.HTTP_201_CREATED,
    tags=["auth"],
    responses={
        201: {"description": "User successfully registered with JWT token"},
        400: {"description": "Duplicate email/username or validation error"},
        500: {"description": "Internal server error"}
    }
)
def register(user_create: UserCreate, db: Session = Depends(get_db)):
    """Register a new user and return JWT tokens."""
    try:
        # ✅ Check for duplicate email specifically
        existing_email = db.query(User).filter(User.email == user_create.email).first()
        if existing_email:
            raise HTTPException(400, "Email already exists")
        
        # ✅ Check for duplicate username
        existing_username = db.query(User).filter(User.username == user_create.username).first()
        if existing_username:
            raise HTTPException(400, "Username already exists")
        
        # ✅ Register user (hash password, create instance)
        user_data = user_create.dict(exclude={"confirm_password"})
        user = User.register(db, user_data)
        
        # ✅ Commit transaction
        db.commit()
        db.refresh(user)
        
        # ✅ Generate JWT tokens
        access_token = User.create_access_token({"sub": str(user.id)})
        refresh_token = User.create_refresh_token({"sub": str(user.id)})
        expires_at = datetime.now(timezone.utc) + timedelta(
            minutes=get_settings().ACCESS_TOKEN_EXPIRE_MINUTES
        )
        
        # ✅ Return token response
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
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
        db.rollback()
        raise
    
    except ValueError as e:
        db.rollback()
        raise HTTPException(400, str(e))
    
    except Exception as e:
        db.rollback()
        print(f"Registration error: {str(e)}")
        raise HTTPException(500, "An error occurred during registration. Please try again later.")
```

**Key Changes:**
1. ✅ Response model changed from `UserResponse` to `TokenResponse`
2. ✅ Duplicate email check with specific error message
3. ✅ Duplicate username check with specific error message
4. ✅ JWT token generation after successful registration
5. ✅ Proper error handling with rollback for all error paths
6. ✅ Safe error messages for 500 errors (don't expose internals)

---

### 2. app/models/user.py - Updated register() Method

```python
@classmethod
def register(cls, db, user_data: dict):
    """Register a new user."""
    password = user_data.get("password")
    
    # ✅ Validate password length (8+ chars)
    if not password or len(password) < 8:
        raise ValueError("Password must be at least 8 characters long")
    
    # ✅ Fallback duplicate check (endpoint should catch first)
    existing_user = db.query(cls).filter(
        or_(cls.email == user_data["email"], cls.username == user_data["username"])
    ).first()
    if existing_user:
        if existing_user.email == user_data["email"]:
            raise ValueError("Email already exists")
        else:
            raise ValueError("Username already exists")
    
    # ✅ Hash password using bcrypt
    hashed_password = cls.hash_password(password)
    
    # ✅ Create user instance
    user = cls(
        first_name=user_data["first_name"],
        last_name=user_data["last_name"],
        email=user_data["email"],
        username=user_data["username"],
        password=hashed_password,
        is_active=True,
        is_verified=False
    )
    
    # ✅ Add to session (don't commit - let endpoint handle it)
    db.add(user)
    return user
```

**Key Changes:**
1. ✅ Password length validation updated to 8 chars (was 6)
2. ✅ Better error messages for duplicate email vs username
3. ✅ No commit in this method - endpoint controls transaction
4. ✅ Comments clarify responsibilities

---

## Usage Examples

### cURL Example

```bash
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "jane@example.com",
    "username": "janedoe",
    "first_name": "Jane",
    "last_name": "Doe",
    "password": "SecurePass123!",
    "confirm_password": "SecurePass123!"
  }'
```

### Python Requests Example

```python
import requests

response = requests.post(
    "http://localhost:8000/auth/register",
    json={
        "email": "jane@example.com",
        "username": "janedoe",
        "first_name": "Jane",
        "last_name": "Doe",
        "password": "SecurePass123!",
        "confirm_password": "SecurePass123!"
    }
)

if response.status_code == 201:
    data = response.json()
    access_token = data["access_token"]
    print(f"✅ Registered! Token: {access_token[:50]}...")
    
    # Use token for authenticated requests
    headers = {"Authorization": f"Bearer {access_token}"}
    profile = requests.get("http://localhost:8000/profile", headers=headers)
    print(profile.json())
else:
    print(f"❌ Error: {response.json()['detail']}")
```

### JavaScript Fetch Example

```javascript
const response = await fetch('http://localhost:8000/auth/register', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    email: 'jane@example.com',
    username: 'janedoe',
    first_name: 'Jane',
    last_name: 'Doe',
    password: 'SecurePass123!',
    confirm_password: 'SecurePass123!'
  })
});

if (response.ok) {
  const data = await response.json();
  // Store token in localStorage
  localStorage.setItem('access_token', data.access_token);
  localStorage.setItem('refresh_token', data.refresh_token);
  console.log('✅ Registered!', data);
} else {
  const error = await response.json();
  console.error('❌ Error:', error.detail);
}
```

---

## Testing Checklist

- [ ] ✅ Valid registration returns 201 with JWT token
- [ ] ✅ Duplicate email returns 400 "Email already exists"
- [ ] ✅ Duplicate username returns 400 "Username already exists"
- [ ] ✅ Weak password (no uppercase) returns 400 with validation error
- [ ] ✅ Weak password (no lowercase) returns 400 with validation error
- [ ] ✅ Weak password (no digit) returns 400 with validation error
- [ ] ✅ Password < 8 chars returns 400 with validation error
- [ ] ✅ Password mismatch returns 400 "Passwords do not match"
- [ ] ✅ Invalid email format returns 422 validation error
- [ ] ✅ Missing required fields returns 422 validation error
- [ ] ✅ JWT token is valid and can be decoded
- [ ] ✅ Token contains correct user_id in "sub" claim
- [ ] ✅ Database transaction rolled back on error
- [ ] ✅ Password is hashed (not stored in plain text)
- [ ] ✅ User is created with is_active=true, is_verified=false

---

## Security Considerations

1. **Password Hashing**: Passwords are hashed using bcrypt with 12 rounds
2. **JWT Security**: Tokens use HS256 algorithm with secret key from environment
3. **Error Messages**: Generic 500 errors don't expose internal details
4. **Input Validation**: Pydantic validates all inputs before processing
5. **Email Uniqueness**: Enforced at database and application level
6. **Transaction Safety**: Rollback on errors prevents partial data commits

---

## Related Endpoints

- **POST /auth/login** - Authenticate with existing credentials
- **POST /auth/refresh** - Refresh access token using refresh token
- **GET /profile** - Get current user profile (requires JWT)
- **POST /auth/logout** - Invalidate tokens
