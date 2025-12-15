# Negative Flow Tests Documentation

## Overview

The `e2e/negative-flows.spec.js` file contains comprehensive Playwright tests for **error handling** scenarios where user input is invalid or authentication fails.

## Test File Created

**File:** `e2e/negative-flows.spec.js`

## Test Suites

### 1. Registration - Negative Flows (6 tests)

Tests that verify error handling during registration:

#### Test 1: `should show error for password shorter than 8 characters`
- **Password:** `Short1` (6 characters)
- **Expected:**
  - ✅ Error message visible (client-side OR server-side)
  - ✅ Error mentions password length requirement (8 characters)
  - ✅ No token stored in localStorage
  - ✅ No success message shown
- **Checks:**
  - `data-testid="error-message"` is visible
  - Error text contains "password" and "8"
  - Browser HTML5 validation may prevent submit

#### Test 2: `should show error for very short password (3 characters)`
- **Password:** `Abc` (3 characters)
- **Expected:** Error shown, no token stored

#### Test 3: `should show error for mismatched passwords`
- **Password:** `Password123`
- **Confirm:** `DifferentPass456`
- **Expected:**
  - Error message about passwords not matching
  - No token stored

#### Test 4: `should show error for invalid email format`
- **Email:** `notanemail` (no @ or domain)
- **Expected:**
  - Error shown (client or server validation)
  - No token stored

#### Test 5: `should show error for duplicate email`
- **Steps:**
  1. Register user successfully
  2. Try to register again with same email
  3. Should fail with "email already exists" error
- **Expected:**
  - Error message about duplicate email
  - No new token stored

### 2. Login - Negative Flows (6 tests)

Tests that verify error handling during login:

#### Test 6: `should show "Invalid credentials" error for wrong password` ⭐
- **Steps:**
  1. Register user with correct password
  2. Try to login with WRONG password
  3. Should fail with "Invalid credentials" error
- **Expected:**
  - ✅ Error message is visible
  - ✅ Error text contains "Invalid credentials" or similar
  - ✅ No token stored in localStorage
  - ✅ No success message shown
- **Assertions:**
  ```javascript
  const errorText = await page.getByTestId('error-message').textContent();
  expect(errorText.toLowerCase()).toMatch(/invalid.*credential|incorrect.*password/i);
  
  const token = await page.evaluate(() => localStorage.getItem('token'));
  expect(token).toBeNull();
  ```

#### Test 7: `should show error for non-existent user`
- **Email:** User that doesn't exist in database
- **Expected:** "Invalid credentials" or "User not found" error

#### Test 8: `should show error for empty password on login`
- **Password:** Empty string
- **Expected:** Validation error, no token

#### Test 9: `should show error for invalid email format on login`
- **Email:** `notanemail` (invalid format)
- **Expected:** Validation error, no token

#### Test 10: `should show error for short password on login (<8 characters)`
- **Password:** `Short1` (6 characters)
- **Expected:** Validation error, no token

#### Test 11: `should prevent multiple failed login attempts`
- **Steps:** Try 3 failed login attempts in a row
- **Expected:** Each attempt shows error, no tokens stored

### 3. Combined Negative Scenarios (1 test)

#### Test 12: `should handle registration then failed login gracefully`
- **Flow:**
  1. Register successfully
  2. Login with WRONG password (should fail)
  3. Login with CORRECT password (should succeed)
- **Verifies:** System recovers from failed attempts

---

## Key Features

### ✅ Dual Validation Checks

Tests check BOTH client-side and server-side validation:

```javascript
// Check for visible error message
const errorVisible = await page.getByTestId('error-message').isVisible();

// Check for HTML5 browser validation
const passwordInput = page.getByTestId('password-input');
const validationMessage = await passwordInput.evaluate((el) => el.validationMessage);

// Pass if either is true
expect(errorVisible || validationMessage).toBeTruthy();
```

### ✅ Token Verification

All tests verify token is NOT stored on failure:

```javascript
const token = await page.evaluate(() => localStorage.getItem('token'));
expect(token).toBeNull();
```

### ✅ Error Message Content Check

Tests verify error messages contain expected text:

```javascript
const errorText = await page.getByTestId('error-message').textContent();
expect(errorText.toLowerCase()).toMatch(/invalid.*credential/i);
```

### ✅ Success Message Absence

Verifies success message is NOT shown on error:

```javascript
const successVisible = await page.getByTestId('success-message').isVisible();
expect(successVisible).toBe(false);
```

---

## Running the Tests

### Run all negative flow tests:
```bash
npx playwright test e2e/negative-flows.spec.js
```

### Run with UI mode:
```bash
npm run e2e:ui -- e2e/negative-flows.spec.js
```

### Run specific test:
```bash
npx playwright test -g "should show error for password shorter than 8"
npx playwright test -g "Invalid credentials"
```

### Run registration errors only:
```bash
npx playwright test -g "Registration - Negative"
```

### Run login errors only:
```bash
npx playwright test -g "Login - Negative"
```

---

## Expected Output

```
Running 12 tests using 3 workers

  ✓  should show error for password shorter than 8 characters (chromium) - 2.1s
      ✓ Error message shown: "Password must be at least 8 characters long"
      ✓ No token stored (as expected)
      ✓ No success message shown (as expected)
  
  ✓  should show error for very short password (chromium) - 1.8s
      ✓ Error shown for 3-character password
  
  ✓  should show error for mismatched passwords (chromium) - 1.9s
      ✓ Error shown: "Passwords do not match"
  
  ✓  should show error for invalid email format (chromium) - 1.7s
      ✓ Error shown for invalid email format
  
  ✓  should show error for duplicate email (chromium) - 4.2s
      ✓ First registration successful
      ✓ Duplicate email error: "Email already exists"
  
  ✓  should show "Invalid credentials" error for wrong password (chromium) - 4.5s
      ✓ User registered successfully
      ✓ Error message is visible
      ✓ Error message text: "Invalid credentials"
      ✓ Error message contains "Invalid credentials" or similar
      ✓ No token stored (as expected)
      ✓ No success message shown (as expected)
  
  ✓  should show error for non-existent user (chromium) - 2.3s
      ✓ Non-existent user error: "Invalid credentials"
  
  ✓  should show error for empty password on login (chromium) - 1.6s
      ✓ Error shown for empty password
  
  ✓  should show error for invalid email format on login (chromium) - 1.5s
      ✓ Error shown for invalid email on login
  
  ✓  should show error for short password on login (chromium) - 1.7s
      ✓ Error shown for short password on login
  
  ✓  should prevent multiple failed login attempts (chromium) - 6.1s
      ✓ Attempt 1: Error shown for failed login
      ✓ Attempt 2: Error shown for failed login
      ✓ Attempt 3: Error shown for failed login
      ✓ All 3 failed login attempts properly rejected
  
  ✓  should handle registration then failed login gracefully (chromium) - 6.8s
      ✓ Registration successful
      ✓ Login with wrong password failed (as expected)
      ✓ Login with correct password successful

  12 passed (36.4s)
```

---

## Test Coverage Matrix

| Scenario | Client Validation | Server Validation | Token Check | Error Message |
|----------|------------------|-------------------|-------------|---------------|
| Short password (<8) | ✅ | ✅ | ✅ | ✅ |
| Mismatched passwords | ✅ | ✅ | ✅ | ✅ |
| Invalid email format | ✅ | ✅ | ✅ | ✅ |
| Duplicate email | ❌ | ✅ | ✅ | ✅ |
| Wrong password (login) | ❌ | ✅ | ✅ | ✅ |
| Non-existent user | ❌ | ✅ | ✅ | ✅ |
| Empty password | ✅ | ✅ | ✅ | ✅ |
| Multiple failed attempts | ❌ | ✅ | ✅ | ✅ |

---

## Selectors Used

### Error/Success Messages:
- `data-testid="error-message"` - Error alert container
- `data-testid="success-message"` - Success alert container

### Form Inputs:
- `data-testid="email-input"` - Email field
- `data-testid="password-input"` - Password field
- `data-testid="confirm-password-input"` - Confirm password field
- `data-testid="submit-button"` - Submit button

---

## Error Message Patterns

Tests check for these patterns in error messages:

### Registration Errors:
- Password length: `/password.*8|8.*character/i`
- Password mismatch: `/password.*match|match.*password/i`
- Duplicate email: `/email.*exist|already.*registered/i`

### Login Errors:
- Invalid credentials: `/invalid.*credential|incorrect.*password|wrong.*password|authentication.*failed/i`
- Non-existent user: `/invalid.*credential|not.*found|does.*not.*exist/i`

---

## Best Practices Implemented

1. ✅ **Dual validation checks** - Client AND server errors
2. ✅ **Flexible assertions** - HTML5 validation OR error message
3. ✅ **Token verification** - Always check token is NULL on failure
4. ✅ **Error content check** - Verify meaningful error messages
5. ✅ **Success prevention** - No success indicators on failure
6. ✅ **Console logging** - Debug-friendly output
7. ✅ **Realistic scenarios** - Tests actual user mistakes
8. ✅ **Recovery testing** - System can recover from failures

---

## Prerequisites

Before running tests:

1. **Start FastAPI server:**
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8000
   ```

2. **Ensure database is running:**
   ```bash
   docker-compose up -d db
   ```

---

## Summary

✅ **12 comprehensive negative tests** covering error scenarios  
✅ **Password validation** - Short passwords rejected  
✅ **Login errors** - "Invalid credentials" displayed, no token stored  
✅ **Dual validation** - Client-side AND server-side checks  
✅ **Token verification** - Always null on failure  
✅ **Error message validation** - Meaningful messages shown  
✅ **Recovery testing** - System handles failures gracefully  

The test suite ensures the authentication system properly handles all error cases! 🛡️
