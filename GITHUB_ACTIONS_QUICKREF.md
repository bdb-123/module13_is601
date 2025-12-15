# GitHub Actions Docker Hub - Quick Reference

## 🎯 What Changed

**New Job Added:** `docker-build-push`
- Runs **only on push to main** (not PRs)
- Waits for E2E tests to pass
- Builds and pushes Docker image to Docker Hub

## 🔐 Required Secrets

Add these in GitHub Settings → Secrets → Actions:

| Secret Name | Value |
|------------|-------|
| `DOCKERHUB_USERNAME` | Your Docker Hub username |
| `DOCKERHUB_TOKEN` | Docker Hub access token |

### How to Get Docker Hub Token

1. Go to [hub.docker.com](https://hub.docker.com/)
2. Account Settings → Security → Access Tokens
3. New Access Token → Name: `github-actions`
4. Permissions: Read, Write, Delete
5. Copy the token (you won't see it again!)

## 📦 Image Tags

Every push to main creates **two tags**:

```
<username>/module13_is601:latest
<username>/module13_is601:<git_sha>
```

**Example:**
```
johndoe/module13_is601:latest
johndoe/module13_is601:abc1234
```

## 🔄 Workflow Behavior

### Push to Main
```
Push → Tests → Build & Push Docker Image
```

### Pull Request
```
PR → Tests → Done (no Docker build)
```

### Push to Other Branch
```
Push → Tests → Done (no Docker build)
```

## 📝 Key Workflow Sections

### Conditional Job Execution
```yaml
docker-build-push:
  if: github.event_name == 'push' && github.ref == 'refs/heads/main'
  needs: e2e-tests
```

### Docker Hub Login
```yaml
- uses: docker/login-action@v2
  with:
    username: ${{ secrets.DOCKERHUB_USERNAME }}
    password: ${{ secrets.DOCKERHUB_TOKEN }}
```

### Image Tagging
```yaml
- uses: docker/metadata-action@v4
  with:
    images: ${{ secrets.DOCKERHUB_USERNAME }}/${{ github.event.repository.name }}
    tags: |
      type=raw,value=latest
      type=sha,prefix=,format=short
```

### Build and Push
```yaml
- uses: docker/build-push-action@v4
  with:
    context: .
    push: true
    tags: ${{ steps.meta.outputs.tags }}
    cache-from: type=gha
    cache-to: type=gha,mode=max
```

## 🚀 Using the Images

### Pull Latest
```bash
docker pull <username>/module13_is601:latest
```

### Pull Specific Version
```bash
docker pull <username>/module13_is601:abc1234
```

### Run Locally
```bash
docker run -p 8000:8000 \
  -e DATABASE_URL=postgresql://user:pass@host:5432/db \
  -e JWT_SECRET_KEY=your-secret-key \
  <username>/module13_is601:latest
```

## ✅ Testing Checklist

- [ ] Add `DOCKERHUB_USERNAME` secret to GitHub
- [ ] Add `DOCKERHUB_TOKEN` secret to GitHub
- [ ] Commit and push changes to main
- [ ] Check Actions tab for workflow progress
- [ ] Verify images appear on Docker Hub
- [ ] Test pulling and running the image

## 🔧 Troubleshooting

| Problem | Solution |
|---------|----------|
| "No such secret" | Add secrets in GitHub repo settings |
| Docker login failed | Verify token is valid and has correct permissions |
| Image not pushed | Check if push is to main and tests passed |
| Build failed | Verify `docker build .` works locally |

## 📊 Complete Workflow Summary

```yaml
name: E2E Tests and Docker Build

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  # Job 1: Run tests (always)
  e2e-tests:
    # ... test steps ...
  
  # Job 2: Build & push (main only)
  docker-build-push:
    if: github.event_name == 'push' && github.ref == 'refs/heads/main'
    needs: e2e-tests
    steps:
      - Checkout
      - Setup Docker Buildx
      - Login to Docker Hub
      - Extract metadata (tags)
      - Build and push
```

## 📖 Full Documentation

See `GITHUB_ACTIONS_DOCKER_HUB.md` for complete details.

## ✨ Benefits

✅ Automated image publishing on every main push  
✅ Only tested code gets published  
✅ Version control with Git SHA tags  
✅ Fast builds with GitHub Actions cache  
✅ No Docker push on pull requests  
