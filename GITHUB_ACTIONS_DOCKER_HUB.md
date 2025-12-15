# GitHub Actions Workflow - Docker Hub Integration

## 📋 Overview

The GitHub Actions workflow has been extended to include Docker Hub image building and publishing, but **only on push to main branch** (not on pull requests).

## 🔄 Workflow Structure

### Two Jobs

1. **e2e-tests** - Runs on all pushes and PRs
2. **docker-build-push** - Runs **only on push to main** after tests pass

## 📝 Workflow Changes

### Job 1: E2E Tests (Runs Always)
```yaml
e2e-tests:
  runs-on: ubuntu-latest
  # Runs on:
  # - Push to main
  # - Pull requests to main
```

**Steps:**
1. Checkout code
2. Setup Node.js
3. Install Playwright
4. Start Docker services with health checks
5. Verify services are healthy
6. Run E2E tests
7. Upload test reports (always, even on failure)
8. Cleanup

---

### Job 2: Docker Build & Push (Main Branch Only)
```yaml
docker-build-push:
  # Only runs when:
  # - Event is 'push' (not 'pull_request')
  # - Branch is 'main'
  if: github.event_name == 'push' && github.ref == 'refs/heads/main'
  needs: e2e-tests  # Waits for tests to pass
```

**Steps:**

#### 1. Checkout Code
```yaml
- name: Checkout code
  uses: actions/checkout@v3
```

#### 2. Set up Docker Buildx
```yaml
- name: Set up Docker Buildx
  uses: docker/setup-buildx-action@v2
```
- Enables multi-platform builds
- Enables layer caching

#### 3. Log in to Docker Hub
```yaml
- name: Log in to Docker Hub
  uses: docker/login-action@v2
  with:
    username: ${{ secrets.DOCKERHUB_USERNAME }}
    password: ${{ secrets.DOCKERHUB_TOKEN }}
```

**Required Secrets:**
- `DOCKERHUB_USERNAME` - Your Docker Hub username
- `DOCKERHUB_TOKEN` - Docker Hub access token (not password!)

#### 4. Extract Metadata
```yaml
- name: Extract metadata for Docker
  id: meta
  uses: docker/metadata-action@v4
  with:
    images: ${{ secrets.DOCKERHUB_USERNAME }}/${{ github.event.repository.name }}
    tags: |
      type=raw,value=latest
      type=sha,prefix=,format=short
```

**Generated Tags:**
- `<username>/module13_is601:latest`
- `<username>/module13_is601:<git_sha>` (e.g., `abc1234`)

#### 5. Build and Push
```yaml
- name: Build and push Docker image
  uses: docker/build-push-action@v4
  with:
    context: .
    push: true
    tags: ${{ steps.meta.outputs.tags }}
    labels: ${{ steps.meta.outputs.labels }}
    cache-from: type=gha
    cache-to: type=gha,mode=max
```

**Features:**
- Builds from Dockerfile in repo root
- Pushes to Docker Hub automatically
- Uses GitHub Actions cache for faster builds
- Applies both tags (latest + SHA)

#### 6. Show Digest
```yaml
- name: Image digest
  run: echo "Image pushed with digest ${{ steps.meta.outputs.digest }}"
```

---

## 🔐 Setting Up Secrets

### Step 1: Create Docker Hub Access Token

1. Log in to [Docker Hub](https://hub.docker.com/)
2. Click your username → **Account Settings**
3. Go to **Security** → **Access Tokens**
4. Click **New Access Token**
5. Name: `github-actions`
6. Permissions: **Read, Write, Delete**
7. Click **Generate**
8. **Copy the token** (you won't see it again!)

### Step 2: Add Secrets to GitHub

1. Go to your GitHub repository
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**

**Add two secrets:**

| Name | Value |
|------|-------|
| `DOCKERHUB_USERNAME` | Your Docker Hub username |
| `DOCKERHUB_TOKEN` | The access token from Step 1 |

---

## 🎯 Image Tagging Strategy

### Example

If your Docker Hub username is `johndoe` and you push commit `abc1234` to main:

**Images pushed:**
```
johndoe/module13_is601:latest
johndoe/module13_is601:abc1234
```

### Why Two Tags?

- **`latest`**: Always points to the most recent build
  - Easy for deployment: `docker pull johndoe/module13_is601:latest`
  
- **`<git_sha>`**: Specific version tied to exact code
  - Reproducible: `docker pull johndoe/module13_is601:abc1234`
  - Rollback capability
  - Immutable reference

---

## 🔍 Workflow Behavior

### Scenario 1: Push to Main
```
Push to main → Run tests → Tests pass → Build & push Docker image
                        → Tests fail → Stop (no Docker build)
```

### Scenario 2: Pull Request
```
Pull request → Run tests → Tests pass → Done (no Docker build)
                        → Tests fail → PR shows failure
```

### Scenario 3: Push to Other Branch
```
Push to develop → Run tests → Done (no Docker build)
```

---

## 📊 Full Workflow YAML

```yaml
name: E2E Tests and Docker Build

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  e2e-tests:
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v3
      
      - name: Set up Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
          cache: 'npm'
      
      - name: Install Playwright and dependencies
        run: |
          npm ci
          npx playwright install --with-deps
      
      - name: Start Docker services
        run: |
          docker-compose -f docker-compose.ci.yml up --build --wait --detach
      
      - name: Verify services are healthy
        run: |
          echo "Checking service status..."
          docker-compose -f docker-compose.ci.yml ps
          echo "Testing health endpoint..."
          curl -f http://localhost:8000/health || exit 1
          echo "All services are healthy!"
      
      - name: Run Playwright E2E tests
        run: npm test
      
      - name: Upload Playwright report
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: playwright-report
          path: playwright-report/
          retention-days: 30
      
      - name: Upload test results
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: test-results
          path: test-results/
          retention-days: 30
      
      - name: Stop and cleanup services
        if: always()
        run: docker-compose -f docker-compose.ci.yml down -v

  docker-build-push:
    # Only run on push to main (not on PRs)
    if: github.event_name == 'push' && github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    # Wait for tests to pass before building
    needs: e2e-tests
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v3
      
      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v2
      
      - name: Log in to Docker Hub
        uses: docker/login-action@v2
        with:
          username: ${{ secrets.DOCKERHUB_USERNAME }}
          password: ${{ secrets.DOCKERHUB_TOKEN }}
      
      - name: Extract metadata for Docker
        id: meta
        uses: docker/metadata-action@v4
        with:
          images: ${{ secrets.DOCKERHUB_USERNAME }}/${{ github.event.repository.name }}
          tags: |
            type=raw,value=latest
            type=sha,prefix=,format=short
      
      - name: Build and push Docker image
        uses: docker/build-push-action@v4
        with:
          context: .
          push: true
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}
          cache-from: type=gha
          cache-to: type=gha,mode=max
      
      - name: Image digest
        run: echo "Image pushed with digest ${{ steps.meta.outputs.digest }}"
```

---

## 🧪 Testing the Workflow

### Local Testing (Without Docker Push)

```bash
# Test the Docker build locally
docker build -t test-image .

# Verify it works
docker run -p 8000:8000 test-image
curl http://localhost:8000/health
```

### GitHub Testing

1. **Set up secrets** (see above)
2. **Create a PR** → Tests run, no Docker push
3. **Merge to main** → Tests run, then Docker push
4. **Check Actions tab** → See workflow progress
5. **Check Docker Hub** → See your images

---

## 🚀 Using the Published Images

### Pull Latest
```bash
docker pull <username>/module13_is601:latest
```

### Pull Specific Version
```bash
docker pull <username>/module13_is601:abc1234
```

### Run Container
```bash
docker run -p 8000:8000 \
  -e DATABASE_URL=postgresql://user:pass@host:5432/db \
  -e JWT_SECRET_KEY=your-secret-key \
  <username>/module13_is601:latest
```

### Use in Docker Compose
```yaml
services:
  web:
    image: <username>/module13_is601:latest
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql://postgres:postgres@db:5432/fastapi_db
      JWT_SECRET_KEY: your-secret-key
```

---

## 🔧 Troubleshooting

### "No such secret" Error
**Fix:** Add secrets in GitHub repo settings (Settings → Secrets → Actions)

### Docker Login Failed
**Fix:** 
- Verify Docker Hub token is valid
- Ensure token has Read/Write/Delete permissions
- Token might have expired (create new one)

### Image Not Pushed
**Check:**
- Is this a push to main? (Not a PR?)
- Did tests pass?
- Check Actions tab for errors
- Verify secret names match exactly

### Build Failed
**Check:**
- Does `docker build .` work locally?
- Is Dockerfile in repo root?
- Check Dockerfile syntax

---

## 📈 Benefits

✅ **Automated Publishing** - Every main push creates new image  
✅ **Quality Gate** - Only tested code gets published  
✅ **Version Control** - Git SHA tags for reproducibility  
✅ **Fast Builds** - GitHub Actions cache speeds up builds  
✅ **Security** - Uses tokens (not passwords)  
✅ **No PR Pollution** - PRs don't trigger Docker push  

---

## 📖 Key Differences from Original

| Aspect | Before | After |
|--------|--------|-------|
| **Workflow Name** | "E2E Tests" | "E2E Tests and Docker Build" |
| **Jobs** | 1 (e2e-tests) | 2 (e2e-tests + docker-build-push) |
| **Docker Push** | ❌ None | ✅ On main push only |
| **Push Triggers** | main, develop | main only |
| **Image Tags** | N/A | latest + git SHA |
| **Caching** | ❌ None | ✅ GitHub Actions cache |
| **Dependencies** | None | docker-build-push needs e2e-tests |

---

## ✨ Summary

The workflow now:

1. ✅ **Runs E2E tests** on all pushes and PRs
2. ✅ **Builds Docker image** only on main push
3. ✅ **Pushes to Docker Hub** with two tags (latest + SHA)
4. ✅ **Uses GitHub Actions cache** for fast builds
5. ✅ **Waits for tests to pass** before building image
6. ✅ **Requires secrets** DOCKERHUB_USERNAME and DOCKERHUB_TOKEN

**Next Steps:**
1. Add Docker Hub secrets to GitHub
2. Push to main branch
3. Check Actions tab for workflow
4. Verify images on Docker Hub
