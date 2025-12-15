# CI/CD & Testing Quick Reference

## 🚀 Quick Start

### Run Tests Locally

```bash
# Start services
docker-compose up -d

# Run all tests
pytest -v

# Run specific test types
pytest tests/unit/ -v                    # Unit tests only
pytest tests/integration/ -v              # Integration tests only
pytest tests/e2e/ -v -m e2e              # E2E tests only

# Run Playwright tests with browser visible
pytest tests/e2e/test_auth_playwright.py -v --headed

# Stop services
docker-compose down -v
```

### Test Coverage

```bash
# Run with coverage report
pytest --cov=app --cov-report=html

# View coverage report
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
```

## 🧪 Test Files Created

### E2E Auth Tests (`tests/e2e/test_auth_playwright.py`)

**Positive Tests:**
- ✅ `test_registration_success_positive` - Valid registration
- ✅ `test_registration_with_optional_confirm_password` - Password confirmation
- ✅ `test_login_success_positive` - Valid login
- ✅ `test_login_stores_jwt_in_localstorage_positive` - JWT storage verification
- ✅ `test_login_redirects_to_dashboard_positive` - Redirect after login
- ✅ `test_logout_clears_tokens_positive` - Token cleanup

**Negative Tests:**
- ❌ `test_registration_password_mismatch_negative` - Passwords don't match
- ❌ `test_registration_weak_password_negative` - Password too weak
- ❌ `test_registration_invalid_email_negative` - Invalid email format
- ❌ `test_registration_duplicate_username_negative` - Username exists
- ❌ `test_registration_missing_required_fields_negative` - Missing fields
- ❌ `test_login_invalid_credentials_negative` - Wrong credentials
- ❌ `test_login_wrong_password_negative` - Correct user, wrong password
- ❌ `test_login_nonexistent_user_negative` - User doesn't exist
- ❌ `test_login_empty_fields_negative` - Empty login form

## 📋 Pydantic Schemas Created (`app/schemas/auth.py`)

### `UserRegister`
- Email validation (EmailStr)
- Password strength requirements
- Optional confirm_password validation
- Auto returns 422 for validation errors

### `UserLogin`
- Email/username field
- Password field (min 8 chars)

### `TokenResponse`
- access_token
- token_type (default: "bearer")
- refresh_token (optional)

### `ErrorResponse`
- Consistent error message format

## 🔧 GitHub Actions Workflow (`.github/workflows/test.yml`)

### Jobs:

**1. Test Job**
- Install Python & dependencies
- Install Playwright browsers
- Start Docker Compose (DB + web)
- Wait for services to be healthy
- Run unit tests
- Run integration tests
- Run Playwright E2E tests
- Upload test results
- Cleanup services

**2. Security Job**
- Build Docker image
- Scan with Trivy for vulnerabilities
- Fail on CRITICAL/HIGH vulnerabilities

**3. Build and Push Job** (only on `main` branch)
- Build multi-platform image (amd64, arm64)
- Tag with `latest` and commit SHA
- Push to Docker Hub
- Use layer caching

## 🔐 Required GitHub Secrets

Set these in: **Settings** → **Secrets and variables** → **Actions**

- `DOCKER_HUB_USERNAME` - Your Docker Hub username
- `DOCKER_HUB_TOKEN` - Docker Hub access token

📖 **Full setup guide**: See [CICD_SETUP.md](./CICD_SETUP.md)

## 📦 Dependencies Updated

### `requirements.txt` changes:
- `passlib[bcrypt]==1.7.4` - Added bcrypt support for password hashing
- `python-jose==3.3.0` - JWT handling (already present)
- `playwright==1.50.0` - E2E testing (already present)

## 🏗️ Project Structure

```
module13_is601/
├── .github/
│   └── workflows/
│       └── test.yml                    # ✨ Updated CI/CD pipeline
├── app/
│   ├── schemas/
│   │   ├── auth.py                     # ✨ New auth schemas
│   │   └── __init__.py                 # Updated exports
│   ├── main.py                         # Auth routes (already exist)
│   └── ...
├── tests/
│   ├── e2e/
│   │   └── test_auth_playwright.py     # ✨ New E2E tests
│   ├── integration/
│   ├── unit/
│   └── conftest.py
├── CICD_SETUP.md                       # ✨ New setup documentation
├── TESTING.md                          # ✨ This file
├── docker-compose.yml
├── Dockerfile
├── requirements.txt                    # ✨ Updated
└── README.md
```

## 🎯 What Was Implemented

### ✅ Completed Items:

1. **JWT + Hashing Dependencies**
   - Updated `passlib[bcrypt]` for secure password hashing
   - `python-jose` for JWT token handling

2. **Pydantic Auth Schemas**
   - `UserRegister` with validation (email, password strength, confirmation)
   - `UserLogin` for authentication
   - `TokenResponse` for JWT responses
   - `ErrorResponse` for consistent errors
   - FastAPI automatically returns 422 for validation errors

3. **Playwright E2E Tests**
   - 15 comprehensive tests (9 positive + 6 negative)
   - Registration flow testing
   - Login flow testing
   - JWT localStorage verification
   - Redirect behavior testing

4. **GitHub Actions CI/CD**
   - Docker Compose integration
   - Playwright browser installation
   - Service health checks
   - Unit + Integration + E2E test execution
   - Security scanning with Trivy
   - Multi-platform Docker image build
   - Automated push to Docker Hub
   - Proper cleanup and error handling

5. **Documentation**
   - Complete setup guide for GitHub secrets
   - Local testing instructions
   - Troubleshooting guide
   - Quick reference documentation

## 🚨 Before Pushing to GitHub

1. **Configure GitHub Secrets:**
   ```
   DOCKER_HUB_USERNAME=<your-username>
   DOCKER_HUB_TOKEN=<your-access-token>
   ```

2. **Test locally first:**
   ```bash
   docker-compose up -d
   pytest tests/e2e/ -v -m e2e
   docker-compose down -v
   ```

3. **Verify Docker Hub repository exists** or will be auto-created

## 📊 Expected Workflow Output

When you push to `main`:

```
✅ Test Job
   ├── ✅ Install dependencies
   ├── ✅ Install Playwright
   ├── ✅ Start Docker Compose
   ├── ✅ Run unit tests (with coverage)
   ├── ✅ Run integration tests
   ├── ✅ Run Playwright E2E tests
   └── ✅ Cleanup

✅ Security Job
   ├── ✅ Build image
   └── ✅ Scan with Trivy

✅ Build and Push Job
   ├── ✅ Build multi-platform image
   ├── ✅ Tag: latest + SHA
   └── ✅ Push to Docker Hub
```

## 🔍 Debugging Tips

### E2E Tests Failing?

```bash
# Run in headed mode to see the browser
pytest tests/e2e/test_auth_playwright.py::test_login_success_positive -v --headed

# Check if services are running
docker-compose ps

# Check web service logs
docker-compose logs web

# Check if health endpoint works
curl http://localhost:8000/health
```

### GitHub Actions Failing?

1. Check the Actions tab for detailed logs
2. Verify secrets are configured
3. Look for specific error messages
4. Test the same steps locally

## 📚 Additional Resources

- [Playwright Documentation](https://playwright.dev/python/)
- [FastAPI Testing Guide](https://fastapi.tiangolo.com/tutorial/testing/)
- [Pydantic Validation](https://docs.pydantic.dev/latest/concepts/validators/)
- [GitHub Actions Docs](https://docs.github.com/en/actions)
- [Docker Hub](https://hub.docker.com/)

---

**All TODO items completed! 🎉**
