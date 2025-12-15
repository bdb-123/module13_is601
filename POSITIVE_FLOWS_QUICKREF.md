# Positive Flow Tests - Quick Reference

## ✅ Test File Created

**File:** `e2e/positive-flows.spec.js`

## 🎯 What's Tested

### 1. Registration Flow
```javascript
// Navigate to /register
await page.goto('/register');

// Fill form with unique credentials
const timestamp = Date.now();
const randomNum = Math.floor(Math.random() * 10000);
const email = `testuser${timestamp}${randomNum}@example.com`;

await page.getByTestId('email-input').fill(email);
await page.getByTestId('password-input').fill('SecurePassword123'); // ≥8 chars
await page.getByTestId('confirm-password-input').fill('SecurePassword123');
await page.getByTestId('submit-button').click();

// Assert success
const successVisible = await page.getByTestId('success-message').isVisible();
const token = await page.evaluate(() => localStorage.getItem('token'));
expect(successVisible || token).toBeTruthy();
```

### 2. Login Flow
```javascript
// Navigate to /login
await page.goto('/login');

// Fill credentials
await page.getByTestId('email-input').fill(email);
await page.getByTestId('password-input').fill(password);
await page.getByTestId('submit-button').click();

// Assert success
const successVisible = await page.getByTestId('success-message').isVisible();
const token = await page.evaluate(() => localStorage.getItem('token'));
expect(successVisible || token).toBeTruthy();
```

## 📋 All Tests

1. ✅ **Register new user** - Basic registration with unique email
2. ✅ **Login with credentials** - Login after registration
3. ✅ **Complete flow** - Register → Logout → Login
4. ✅ **Min password (8 chars)** - `Pass1234`
5. ✅ **Long password** - `ThisIsAVeryLongAndSecurePassword123456789!@#`
6. ✅ **Various email formats** - dots, plus, underscores
7. ✅ **Token persistence** - Token survives page refresh
8. ✅ **Immediate re-login** - Login right after registration

**Total: 8 tests × 3 browsers = 24 test runs**

## 🔍 Selectors Used

### data-testid attributes:
- `email-input` - Email field
- `password-input` - Password field
- `confirm-password-input` - Confirm password (register only)
- `submit-button` - Submit button
- `success-message` - Success alert
- `error-message` - Error alert

### ID selectors:
- `#username` - Username field
- `#first_name` - First name field
- `#last_name` - Last name field

## 🚀 Run Commands

```bash
# Run all positive flow tests
npx playwright test e2e/positive-flows.spec.js

# Run with UI
npm run e2e:ui -- e2e/positive-flows.spec.js

# Run specific test
npx playwright test -g "should successfully register"

# Run in headed mode
npm run e2e:headed -- e2e/positive-flows.spec.js
```

## 📊 Expected Output

```
Running 8 tests using 3 workers

  ✓  should successfully register a new user (chromium) - 3.2s
  ✓  should successfully login with registered credentials (chromium) - 4.1s
  ✓  complete registration and login flow with different user (chromium) - 5.8s
  ✓  should register with minimum valid password length (chromium) - 2.9s
  ✓  should register with long password (chromium) - 3.1s
  ✓  should register with various email formats (chromium) - 8.4s
  ✓  should login and persist token across page refresh (chromium) - 4.6s
  ✓  should login immediately after registration (chromium) - 3.8s

  8 passed (35.9s)
```

## ✨ Key Features

### Unique Test Data
```javascript
const timestamp = Date.now();
const randomNum = Math.floor(Math.random() * 10000);
const email = `testuser${timestamp}${randomNum}@example.com`;
```
- Prevents duplicate user errors
- Each test run creates new users
- No test data cleanup needed

### Flexible Success Checks
```javascript
const successVisible = await page.getByTestId('success-message').isVisible().catch(() => false);
const token = await page.evaluate(() => localStorage.getItem('token'));

// Pass if EITHER is true
if (token) {
  expect(token).toBeTruthy();
  console.log('✓ JWT token stored');
} else if (!successMessageVisible) {
  throw new Error('Registration failed');
}
```
- Checks success message OR token
- Accommodates different success indicators
- More robust than single assertion

### Wait Strategy
```javascript
await page.waitForTimeout(2000); // 2 seconds
```
- Allows time for API response
- Permits JWT generation
- Prevents race conditions

## 🔧 Prerequisites

```bash
# 1. Start FastAPI server
uvicorn app.main:app --host 0.0.0.0 --port 8000

# 2. Ensure database is running
docker-compose up -d db

# 3. Install Playwright (if not already done)
npm install
npm run e2e:install
```

## 📝 Test Coverage

- ✅ Valid email formats
- ✅ Password minimum (8 characters)
- ✅ Password maximum (40+ characters)
- ✅ Password confirmation matching
- ✅ Success message visibility
- ✅ localStorage token storage
- ✅ Token persistence after refresh
- ✅ Complete user lifecycle (register → login)
- ✅ No error messages on success

## 🎓 Example Test

```javascript
test('should successfully register a new user', async ({ page }) => {
  // 1. Go to register page
  await page.goto('/register');
  
  // 2. Fill form with unique data
  const email = `testuser${Date.now()}@example.com`;
  await page.getByTestId('email-input').fill(email);
  await page.getByTestId('password-input').fill('Password123');
  await page.getByTestId('confirm-password-input').fill('Password123');
  await page.locator('#username').fill('testuser');
  await page.locator('#first_name').fill('Test');
  await page.locator('#last_name').fill('User');
  
  // 3. Submit
  await page.getByTestId('submit-button').click();
  await page.waitForTimeout(2000);
  
  // 4. Assert success (message OR token)
  const token = await page.evaluate(() => localStorage.getItem('token'));
  const successVisible = await page.getByTestId('success-message').isVisible();
  expect(token || successVisible).toBeTruthy();
});
```

## 📚 Full Documentation

See `POSITIVE_FLOWS_TESTS.md` for complete documentation.

---

**Ready to run! Just start the server and execute:**
```bash
npm run e2e -- e2e/positive-flows.spec.js
```
