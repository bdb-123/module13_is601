# Playwright E2E Testing Setup

## Overview

This repository now includes end-to-end (E2E) testing using Playwright for testing the FastAPI application's web interface.

## Files Created

### Configuration Files

1. **package.json** - Node.js package configuration with Playwright dependencies and scripts
2. **playwright.config.js** - Playwright test configuration
   - Base URL: `http://localhost:8000`
   - Test directory: `./e2e`
   - Browsers: Chromium, Firefox, WebKit
   - Reports: HTML, List, JSON

3. **.gitignore** - Updated to exclude:
   - `node_modules/`
   - `playwright-report/`
   - `test-results/`
   - `playwright/.cache/`

### Test Files (e2e/ directory)

1. **e2e/example.spec.js** - Basic setup verification tests
   - Server running check
   - Health endpoint test

2. **e2e/auth.spec.js** - Authentication flow tests
   - Login page load
   - Register page load
   - Email validation
   - Password validation
   - Password mismatch detection
   - Navigation between auth pages

3. **e2e/home.spec.js** - Home page tests
   - Home page loads
   - Navigation links present

## Installation Steps

### 1. Install Node.js Dependencies

```bash
npm install
```

This will install:
- `@playwright/test` (version ^1.48.0)

### 2. Install Playwright Browsers

```bash
npm run e2e:install
```

Or manually:
```bash
npx playwright install
```

This downloads Chromium, Firefox, and WebKit browsers.

## Running Tests

### Prerequisites

**Start the FastAPI server first:**

```bash
# Option 1: Using uvicorn directly
uvicorn app.main:app --host 0.0.0.0 --port 8000

# Option 2: Using Docker Compose
docker-compose up
```

The server must be running at `http://localhost:8000` before running E2E tests.

### Run All Tests

```bash
npm run e2e
```

### Run Tests with UI Mode (Interactive)

```bash
npm run e2e:ui
```

This opens the Playwright UI for:
- Selecting specific tests to run
- Watching test execution in real-time
- Debugging test failures

### Run Tests in Headed Mode (See Browser)

```bash
npm run e2e:headed
```

### Debug Tests

```bash
npm run e2e:debug
```

Opens Playwright Inspector for step-by-step debugging.

### View Test Report

```bash
npm run e2e:report
```

Opens the HTML report in your browser after tests complete.

## Test Structure

### Example Test

```javascript
const { test, expect } = require('@playwright/test');

test('should load login page', async ({ page }) => {
  await page.goto('/login');
  
  await expect(page).toHaveTitle(/Login/);
  await expect(page.getByTestId('email-input')).toBeVisible();
  await expect(page.getByTestId('password-input')).toBeVisible();
  await expect(page.getByTestId('submit-button')).toBeVisible();
});
```

## Available NPM Scripts

| Script | Command | Description |
|--------|---------|-------------|
| `e2e` | `playwright test` | Run all tests headless |
| `e2e:ui` | `playwright test --ui` | Run tests in interactive UI mode |
| `e2e:headed` | `playwright test --headed` | Run tests with visible browser |
| `e2e:debug` | `playwright test --debug` | Run tests with debugger |
| `e2e:report` | `playwright show-report` | Show HTML test report |
| `e2e:install` | `playwright install` | Install Playwright browsers |

## Running Specific Tests

### Run a specific test file

```bash
npx playwright test e2e/auth.spec.js
```

### Run a specific test by name

```bash
npx playwright test -g "should load login page"
```

### Run tests in a specific browser

```bash
npx playwright test --project=chromium
npx playwright test --project=firefox
npx playwright test --project=webkit
```

## Test Data and Selectors

The tests use `data-testid` attributes for stable element selection:

### Login Page
- `data-testid="email-input"` - Email input
- `data-testid="password-input"` - Password input
- `data-testid="submit-button"` - Submit button
- `data-testid="success-message"` - Success alert
- `data-testid="error-message"` - Error alert

### Register Page
- `data-testid="email-input"` - Email input
- `data-testid="password-input"` - Password input
- `data-testid="confirm-password-input"` - Confirm password input
- `data-testid="submit-button"` - Submit button
- `data-testid="success-message"` - Success alert
- `data-testid="error-message"` - Error alert

## CI/CD Integration

### Uncomment webServer in playwright.config.js

To automatically start the server during tests:

```javascript
webServer: {
  command: 'uvicorn app.main:app --host 0.0.0.0 --port 8000',
  url: 'http://localhost:8000',
  reuseExistingServer: !process.env.CI,
  timeout: 120 * 1000,
},
```

### GitHub Actions Example

```yaml
name: E2E Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install Python dependencies
        run: |
          pip install -r requirements.txt
      
      - name: Set up Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
      
      - name: Install Node dependencies
        run: npm install
      
      - name: Install Playwright browsers
        run: npx playwright install --with-deps
      
      - name: Start FastAPI server
        run: |
          uvicorn app.main:app --host 0.0.0.0 --port 8000 &
          sleep 5
      
      - name: Run Playwright tests
        run: npm run e2e
      
      - name: Upload test report
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: playwright-report
          path: playwright-report/
```

## Troubleshooting

### Server not running

**Error:** `Error: page.goto: net::ERR_CONNECTION_REFUSED`

**Solution:** Make sure the FastAPI server is running at `http://localhost:8000`

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Port already in use

**Error:** `Address already in use`

**Solution:** Check if another process is using port 8000

```bash
# Find process on port 8000
lsof -i :8000

# Kill the process
kill -9 <PID>
```

### Browsers not installed

**Error:** `Executable doesn't exist at /path/to/browser`

**Solution:** Install Playwright browsers

```bash
npm run e2e:install
```

### Tests failing due to timing

**Solution:** Add explicit waits

```javascript
await page.waitForSelector('[data-testid="email-input"]');
await page.waitForLoadState('networkidle');
```

## Writing New Tests

### Create a new test file

```bash
touch e2e/dashboard.spec.js
```

### Test template

```javascript
// @ts-check
const { test, expect } = require('@playwright/test');

test.describe('Feature Name', () => {
  
  test.beforeEach(async ({ page }) => {
    // Setup before each test
    await page.goto('/');
  });
  
  test('should do something', async ({ page }) => {
    // Test implementation
    await expect(page).toHaveURL('/');
  });
});
```

## Best Practices

1. **Use data-testid attributes** for stable selectors
2. **Wait for elements** before interacting with them
3. **Use page object models** for complex pages
4. **Keep tests independent** - each test should work in isolation
5. **Clean up after tests** - reset state if needed
6. **Use meaningful test names** - describe what is being tested
7. **Group related tests** with `test.describe()`
8. **Use fixtures** for common setup/teardown

## Resources

- [Playwright Documentation](https://playwright.dev)
- [Playwright API Reference](https://playwright.dev/docs/api/class-playwright)
- [Best Practices](https://playwright.dev/docs/best-practices)
- [Test Generators](https://playwright.dev/docs/codegen)

## Quick Start Commands

```bash
# 1. Install dependencies
npm install

# 2. Install browsers
npm run e2e:install

# 3. Start FastAPI server (in another terminal)
uvicorn app.main:app --host 0.0.0.0 --port 8000

# 4. Run tests
npm run e2e

# 5. View report
npm run e2e:report
```

## Summary

✅ **Playwright configured** with baseURL `http://localhost:8000`  
✅ **3 test files created** in `e2e/` directory  
✅ **5 NPM scripts added** for running tests  
✅ **Data-testid selectors** ready for stable testing  
✅ **Multi-browser support** (Chromium, Firefox, WebKit)  
✅ **Reports configured** (HTML, List, JSON)  

Your E2E testing setup is complete! 🎭
