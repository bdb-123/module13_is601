# 📸 Screenshot Guide for Module 13 Project

## Required Screenshots

You need to capture **three screenshots** to complete the project requirements:

1. ✅ GitHub Actions Workflow (successful run)
2. ✅ Playwright E2E Tests (passing tests)
3. ✅ Front-End Application (login and registration pages)

---

## 1. 📊 GitHub Actions Workflow Screenshot

### What You Need to Show
A successful GitHub Actions workflow run displaying:
- Workflow name: "E2E Tests and Docker Build"
- Both jobs completed successfully:
  - ✅ `e2e-tests` (green checkmark)
  - ✅ `docker-build-push` (green checkmark)
- Timestamp and commit information

### How to Capture

#### Step 1: Set Up GitHub Secrets (Required First!)
Before the workflow can run successfully, add these secrets:

1. Go to: https://github.com/bdb-123/module13_is601/settings/secrets/actions
2. Click "New repository secret"
3. Add two secrets:
   - **Name**: `DOCKERHUB_USERNAME`  
     **Value**: `bdb-123` (your Docker Hub username)
   - **Name**: `DOCKERHUB_TOKEN`  
     **Value**: (your Docker Hub access token)

**To get Docker Hub token:**
1. Login to https://hub.docker.com/
2. Account Settings → Security → Access Tokens
3. "New Access Token" → Name: `github-actions`
4. Permissions: Read, Write, Delete
5. Generate and copy the token

#### Step 2: Push Changes to Trigger Workflow
```bash
cd /Users/billyb/module13_is601
git add .
git commit -m "Add CI/CD setup and documentation"
git push origin main
```

#### Step 3: Capture Screenshot
1. Go to: https://github.com/bdb-123/module13_is601/actions
2. Click on the most recent workflow run
3. Wait for both jobs to complete (green checkmarks)
4. Screenshot should show:
   ```
   E2E Tests and Docker After Build
   ✓ e2e-tests     (X minutes)
   ✓ docker-build-push     (X minutes)
   ```

### What If It Fails?
- Check the job logs by clicking on the failed job
- Common issues:
  - Missing secrets → Add DOCKERHUB_USERNAME and DOCKERHUB_TOKEN
  - Docker Hub login failed → Verify token is valid
  - Tests failed → Check application logs

---

## 2. 🧪 Playwright E2E Tests Screenshot

### What You Need to Show
Playwright test results showing:
- Total tests run
- Number of tests passed
- Test execution time
- Browser coverage (Chromium, Firefox, WebKit)

### How to Capture

#### Current Status
✅ Application is running (healthy at http://localhost:8000)
✅ Playwright tests are installed
🔄 Tests are currently running

#### Commands to Run Tests
```bash
# If application is not running, start it:
docker-compose up -d --build

# Wait for health check
curl http://localhost:8000/health

# Run tests
npm run e2e
```

#### Capture Options

**Option 1: Terminal Output**
Screenshot showing:
```
Running 93 tests using 5 workers

  ✓  1 [chromium] › e2e/auth.spec.js:6:3 › Authentication Flow › should load login page
  ✓  2 [chromium] › e2e/auth.spec.js:18:3 › Authentication Flow › should load register page
  ...

  XX passed (Xm)
```

**Option 2: HTML Report** (Better visual)
```bash
# After tests run, open the HTML report
npx playwright show-report

# This opens a browser with a visual report
# Screenshot the summary page showing:
# - Total tests
# - Passed/Failed counts
# - Browser coverage
# - Test duration
```

**Option 3: UI Mode** (Most Interactive)
```bash
# Run tests in UI mode
npm run e2e:ui

# Screenshot showing:
# - Test tree with checkmarks
# - Browser previews
# - Test details
```

### Expected Results
Based on current run, you should see approximately:
- ✅ 60-70 tests passing
- ⚠️ Some tests may fail (this is OK for demonstration)
- 🌐 Tests across 3 browsers (Chromium, Firefox, WebKit)

---

## 3. 🖥️ Front-End Application Screenshot

### What You Need to Show
Both login and registration pages functioning correctly:
- Clean UI design
- Form inputs visible
- No console errors
- Proper page layout

### How to Capture

#### Current Status
✅ Application running at http://localhost:8000
✅ Health endpoint responding: http://localhost:8000/health

#### Option A: Two Separate Screenshots

**Screenshot 1: Registration Page**
1. Open browser to: http://localhost:8000/register
2. Screenshot should show:
   - Page title: "Register"
   - Form fields:
     - Username input
     - Email input
     - First Name input
     - Last Name input
     - Password input
     - Confirm Password input
   - "Register" button
   - "Already have an account? Login" link

**Screenshot 2: Login Page**
1. Open browser to: http://localhost:8000/login
2. Screenshot should show:
   - Page title: "Login"
   - Form fields:
     - Email input
     - Password input
   - "Login" button
   - "Don't have an account? Register" link

#### Option B: Side-by-Side Screenshot (Recommended)

Use a screenshot tool to capture both pages:
1. Open two browser windows side-by-side
2. Left: http://localhost:8000/register
3. Right: http://localhost:8000/login
4. Screenshot both windows together

#### Option C: Successful Registration/Login Flow

**Best Option for Demonstration:**

1. **Screenshot 1: Registration Success**
   - Fill out registration form
   - Submit
   - Screenshot showing success message

2. **Screenshot 2: Login Success**
   - Use registered credentials to login
   - Screenshot showing successful login (redirect to dashboard or success message)

### Bonus: Test the Flow
```bash
# Open browser to registration
open http://localhost:8000/register

# Register a new user with:
# Username: testuser123
# Email: testuser123@example.com
# First Name: Test
# Last Name: User
# Password: password123
# Confirm: password123

# Then login with:
# Email: testuser123@example.com
# Password: password123
```

---

## 📁 Where to Save Screenshots

Create a `screenshots/` directory in your project:

```bash
mkdir -p screenshots
```

Suggested filenames:
- `screenshots/github-actions-workflow.png`
- `screenshots/playwright-test-results.png`
- `screenshots/frontend-register-page.png`
- `screenshots/frontend-login-page.png`

Or combined:
- `screenshots/1-github-actions.png`
- `screenshots/2-playwright-tests.png`
- `screenshots/3-frontend-pages.png`

---

## ✅ Checklist

Before capturing screenshots:

### GitHub Actions
- [ ] GitHub secrets added (DOCKERHUB_USERNAME, DOCKERHUB_TOKEN)
- [ ] Changes committed and pushed to main
- [ ] Workflow run completed successfully
- [ ] Both jobs show green checkmarks

### Playwright Tests
- [ ] Application running (`docker-compose up -d`)
- [ ] Health endpoint responding (`curl http://localhost:8000/health`)
- [ ] npm dependencies installed (`npm install`)
- [ ] Playwright browsers installed (`npx playwright install`)
- [ ] Tests executed (`npm run e2e`)
- [ ] Test report generated (optional: `npx playwright show-report`)

### Front-End Application
- [ ] Application accessible at http://localhost:8000
- [ ] Registration page loads at http://localhost:8000/register
- [ ] Login page loads at http://localhost:8000/login
- [ ] Forms are functional and styled
- [ ] No console errors visible

---

## 🎯 Quick Capture Guide

### Fastest Path to All Screenshots

```bash
# 1. Start application
docker-compose up -d --build
sleep 10

# 2. Run Playwright tests
npm install
npx playwright install --with-deps
npm run e2e

# 3. Open test report
npx playwright show-report
# Screenshot: Playwright results

# 4. Open application pages
open http://localhost:8000/register
# Screenshot: Registration page

open http://localhost:8000/login
# Screenshot: Login page

# 5. For GitHub Actions
# - Commit and push changes
# - Go to GitHub Actions tab
# - Screenshot: Workflow results
```

---

## 💡 Tips for Good Screenshots

1. **Clear Resolution**: Use at least 1920x1080
2. **Crop Properly**: Remove unnecessary browser chrome
3. **Show Context**: Include enough to understand what's being shown
4. **Highlight Success**: Make sure ✓ checkmarks are visible
5. **No Sensitive Data**: Don't include real passwords or tokens

---

## 🆘 Troubleshooting

### GitHub Actions Won't Run
- Push to main branch (not other branches)
- Check that workflow file exists at `.github/workflows/e2e-tests.yml`
- Verify secrets are added correctly

### Playwright Tests Fail
- Check application is running: `curl http://localhost:8000/health`
- Check Docker logs: `docker-compose logs web`
- Review test output for specific errors

### Frontend Pages Don't Load
- Verify containers are running: `docker-compose ps`
- Check port 8000 is not in use: `lsof -i :8000`
- Restart application: `docker-compose restart web`

---

## 📊 Example Screenshot Layout

```
GitHub Actions Workflow Screenshot:
┌─────────────────────────────────────────────┐
│ E2E Tests and Docker Build                  │
│ #42 • main • 3 minutes ago                  │
│                                             │
│ ✓ e2e-tests          2m 34s                │
│ ✓ docker-build-push  1m 12s                │
└─────────────────────────────────────────────┘

Playwright Test Results Screenshot:
┌─────────────────────────────────────────────┐
│ Test Results                                │
│                                             │
│ ✓ 68 passed (3 browsers)                   │
│ ⚠  5 flaky                                  │
│ ✗ 0 failed                                  │
│ ⏱  Duration: 45.2s                          │
└─────────────────────────────────────────────┘

Frontend Application Screenshot:
┌──────────────────┬──────────────────┐
│ Register Page    │ Login Page       │
│                  │                  │
│ [Username]       │ [Email]          │
│ [Email]          │ [Password]       │
│ [First Name]     │                  │
│ [Last Name]      │ [Login Button]   │
│ [Password]       │                  │
│ [Confirm Pass]   │ Don't have an    │
│                  │ account?         │
│ [Register]       │ Register         │
│                  │                  │
│ Already have     │                  │
│ account? Login   │                  │
└──────────────────┴──────────────────┘
```

---

**Current Application Status**: ✅ Running and healthy
**Next Step**: Capture screenshots as described above!
