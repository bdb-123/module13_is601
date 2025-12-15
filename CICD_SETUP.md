# GitHub Actions Setup Guide

## Required GitHub Secrets Configuration

To enable the CI/CD pipeline to build and push Docker images to Docker Hub, you need to configure the following secrets in your GitHub repository.

### Step-by-Step Instructions

#### 1. Create Docker Hub Access Token

1. Log in to [Docker Hub](https://hub.docker.com/)
2. Click on your username in the top right corner
3. Select **"Account Settings"**
4. Go to **"Security"** tab
5. Click **"New Access Token"**
6. Give it a description (e.g., "GitHub Actions CI/CD")
7. Set permissions to **"Read, Write, Delete"** (or at minimum "Read & Write")
8. Click **"Generate"**
9. **IMPORTANT**: Copy the token immediately - you won't be able to see it again!

#### 2. Add Secrets to GitHub Repository

1. Go to your GitHub repository
2. Click on **"Settings"** tab
3. In the left sidebar, click **"Secrets and variables"** → **"Actions"**
4. Click **"New repository secret"**

##### Add DOCKER_HUB_USERNAME

- **Name**: `DOCKER_HUB_USERNAME`
- **Value**: Your Docker Hub username (e.g., `johndoe`)
- Click **"Add secret"**

##### Add DOCKER_HUB_TOKEN

- Click **"New repository secret"** again
- **Name**: `DOCKER_HUB_TOKEN`
- **Value**: Paste the access token you copied from Docker Hub
- Click **"Add secret"**

### Verification

After adding both secrets, you should see them listed under "Repository secrets":
- `DOCKER_HUB_USERNAME`
- `DOCKER_HUB_TOKEN`

### Testing the Workflow

Once the secrets are configured:

1. Push code to the `main` branch
2. Go to the **"Actions"** tab in your GitHub repository
3. You should see the workflow running
4. The workflow will:
   - Run unit tests
   - Run integration tests
   - Run Playwright E2E tests
   - Perform security scanning with Trivy
   - Build Docker image
   - Push to Docker Hub (only on `main` branch)

### Expected Docker Hub Images

After a successful workflow run on the `main` branch, you should see two new tags in your Docker Hub repository:

- `<username>/module13_is601:latest` - Always points to the latest main branch build
- `<username>/module13_is601:<commit-sha>` - Specific version tagged with the git commit SHA

### Troubleshooting

#### Error: "unauthorized: authentication required"
- Double-check that `DOCKER_HUB_USERNAME` is your exact Docker Hub username
- Verify that `DOCKER_HUB_TOKEN` is the access token (not your password)
- Ensure the token has "Read & Write" permissions

#### Error: "repository does not exist"
- The repository will be created automatically on first push
- Ensure your Docker Hub username is correct
- Make sure you have permission to create repositories in your Docker Hub account

#### Workflow fails at "Build and push Docker image"
- Check the workflow logs in the Actions tab
- Verify both secrets are set correctly
- Ensure you're pushing to the `main` branch (the build-and-push job only runs on main)

### Security Best Practices

1. **Never commit secrets to your repository**
2. **Use Access Tokens instead of passwords** - Tokens can be revoked without changing your password
3. **Limit token permissions** - Only grant the minimum required permissions
4. **Rotate tokens periodically** - Update your tokens every few months
5. **Use separate tokens for different purposes** - Don't reuse the same token across multiple projects

### Additional Configuration (Optional)

If you want to customize the Docker image name, edit `.github/workflows/test.yml`:

```yaml
# Change this line (appears multiple times):
${{ secrets.DOCKER_HUB_USERNAME }}/module13_is601:latest

# To your preferred image name:
${{ secrets.DOCKER_HUB_USERNAME }}/your-custom-name:latest
```

## Workflow Overview

The CI/CD pipeline consists of three jobs:

### 1. Test Job
- Installs Python dependencies
- Installs Playwright browsers
- Starts Docker Compose services (PostgreSQL + FastAPI)
- Waits for services to be healthy
- Runs unit tests with coverage
- Runs integration tests
- Runs Playwright E2E tests
- Uploads test results as artifacts
- Cleans up Docker Compose services

### 2. Security Job
- Builds Docker image
- Scans for vulnerabilities using Trivy
- Fails if CRITICAL or HIGH vulnerabilities are found

### 3. Build and Push Job (only on main branch)
- Only runs if tests and security checks pass
- Only runs on pushes to `main` branch
- Builds multi-platform Docker image (amd64, arm64)
- Tags with `latest` and commit SHA
- Pushes to Docker Hub
- Uses layer caching for faster builds

## Running Tests Locally

### Run all tests locally with Docker Compose:

```bash
# Start services
docker-compose up -d

# Wait for services to be ready
sleep 10

# Run unit tests
pytest tests/unit/ -v

# Run integration tests
pytest tests/integration/ -v

# Run E2E tests with Playwright
pytest tests/e2e/ -v -m e2e

# Stop services
docker-compose down -v
```

### Run Playwright tests in headed mode (with browser visible):

```bash
pytest tests/e2e/test_auth_playwright.py -v --headed
```

### Run a specific test:

```bash
pytest tests/e2e/test_auth_playwright.py::test_login_success_positive -v
```

## Environment Variables

The following environment variables are used in the workflow:

- `DATABASE_URL`: PostgreSQL connection string for main database
- `TEST_DATABASE_URL`: PostgreSQL connection string for test database
- `JWT_SECRET_KEY`: Secret key for JWT access tokens
- `JWT_REFRESH_SECRET_KEY`: Secret key for JWT refresh tokens
- `DOCKER_HUB_USERNAME`: Docker Hub username (from secrets)
- `DOCKER_HUB_TOKEN`: Docker Hub access token (from secrets)

## Contact & Support

If you encounter issues with the CI/CD pipeline:

1. Check the workflow logs in GitHub Actions
2. Review this documentation
3. Verify all secrets are configured correctly
4. Test locally using Docker Compose
5. Check Docker Hub for successful image pushes

---

**Last Updated**: December 14, 2025
