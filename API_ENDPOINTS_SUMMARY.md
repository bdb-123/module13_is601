# API Endpoints Summary

## Final URL Paths

### Page Routes (GET - Render HTML)
- `GET /` → Home page
- `GET /login` → Login page
- `GET /register` → Registration page
- `GET /dashboard` → Dashboard page

### API Routes (POST - Return JSON)
- `POST /auth/register` → User registration API
- `POST /auth/login` → User login API
- `POST /auth/token` → OAuth2 token endpoint (alternative login)

---

## HTML/JS Fetch Endpoints

### Login Page (`/login`)

**JavaScript fetch to login API:**

```javascript
const response = await fetch('/auth/login', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
    },
    body: JSON.stringify({
        username: email,  // API uses 'username' field but accepts email
        password: password
    })
});

const data = await response.json();

if (response.ok) {
    // Store token in localStorage
    localStorage.setItem('token', data.access_token);
    // Redirect to dashboard
    window.location.href = '/dashboard';
} else {
    // Show error message
    showError(data.detail || 'Login failed');
}
```

**Request Example:**
```json
POST /auth/login
Content-Type: application/json

{
    "username": "user@example.com",
    "password": "mypassword123"
}
```

**Response Example (Success):**
```json
HTTP 200 OK

{
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer",
    "user_id": "123e4567-e89b-12d3-a456-426614174000",
    "username": "johndoe",
    "email": "user@example.com"
}
```

**Response Example (Error):**
```json
HTTP 401 Unauthorized

{
    "detail": "Invalid credentials"
}
```

---

### Registration Page (`/register`)

**JavaScript fetch to registration API:**

```javascript
const response = await fetch('/auth/register', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
    },
    body: JSON.stringify({
        email: email,
        username: username,
        first_name: firstName,
        last_name: lastName,
        password: password,
        confirm_password: confirmPassword
    })
});

const data = await response.json();

if (response.ok) {
    // Store token in localStorage
    localStorage.setItem('token', data.access_token);
    // Optional: store additional data
    if (data.refresh_token) {
        localStorage.setItem('refresh_token', data.refresh_token);
    }
    if (data.user_id) {
        localStorage.setItem('user_id', data.user_id);
    }
    // Redirect to dashboard
    window.location.href = '/dashboard';
} else {
    // Show error message
    showError(data.detail || 'Registration failed');
}
```

**Request Example:**
```json
POST /auth/register
Content-Type: application/json

{
    "email": "newuser@example.com",
    "username": "johndoe",
    "first_name": "John",
    "last_name": "Doe",
    "password": "securepassword123",
    "confirm_password": "securepassword123"
}
```

**Response Example (Success):**
```json
HTTP 201 Created

{
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer",
    "user_id": "123e4567-e89b-12d3-a456-426614174000",
    "username": "johndoe",
    "email": "newuser@example.com"
}
```

**Response Example (Error - Duplicate Email):**
```json
HTTP 400 Bad Request

{
    "detail": "Email already exists"
}
```

**Response Example (Error - Duplicate Username):**
```json
HTTP 400 Bad Request

{
    "detail": "Username already exists"
}
```

---

## Quick Reference

### URL Path Structure

```
Server URLs:
├── Page Routes (HTML)
│   ├── GET /login              → Renders login.html
│   └── GET /register           → Renders register.html
│
└── API Routes (JSON)
    ├── POST /auth/login        → Authentication endpoint
    └── POST /auth/register     → Registration endpoint
```

### Key Points

1. **Page routes** use simple paths: `/login`, `/register`
2. **API routes** are prefixed with `/auth`: `/auth/login`, `/auth/register`
3. **JavaScript fetch** targets the API routes (with `/auth` prefix)
4. **Token storage** uses localStorage key: `"token"`
5. **Login field** uses `username` but accepts email address
6. **Success response** includes `access_token`, `refresh_token`, user info
7. **Error response** includes `detail` field with error message

### Testing URLs

When server is running at `http://localhost:8000`:

**Visit in browser:**
- http://localhost:8000/login
- http://localhost:8000/register

**API endpoints (called by JavaScript):**
- http://localhost:8000/auth/login
- http://localhost:8000/auth/register

### Token Usage

After successful login/register, use the token for authenticated requests:

```javascript
const token = localStorage.getItem('token');

const response = await fetch('/api/some-protected-endpoint', {
    method: 'GET',
    headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
    }
});
```

---

## Complete Flow Example

### Registration Flow

1. User visits: `http://localhost:8000/register`
2. Server returns: `register.html` template
3. User fills form and clicks "Register"
4. JavaScript validates input client-side
5. JavaScript sends: `POST /auth/register` with user data
6. Server validates, creates user, generates JWT
7. Server responds: `201 Created` with tokens
8. JavaScript stores: `localStorage.setItem('token', data.access_token)`
9. JavaScript redirects: `window.location.href = '/dashboard'`

### Login Flow

1. User visits: `http://localhost:8000/login`
2. Server returns: `login.html` template
3. User enters email and password
4. JavaScript validates input client-side
5. JavaScript sends: `POST /auth/login` with credentials
6. Server authenticates, generates JWT
7. Server responds: `200 OK` with tokens
8. JavaScript stores: `localStorage.setItem('token', data.access_token)`
9. JavaScript redirects: `window.location.href = '/dashboard'`

---

## Summary

✅ **Page URLs:** `/login` and `/register` (no `/auth` prefix)  
✅ **API URLs:** `/auth/login` and `/auth/register` (with `/auth` prefix)  
✅ **Fetch targets:** The API URLs (`/auth/login`, `/auth/register`)  
✅ **Token storage:** `localStorage.setItem('token', data.access_token)`  
✅ **Response format:** JSON with `access_token`, `refresh_token`, user data
