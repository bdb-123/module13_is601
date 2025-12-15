# CI/CD Docker Setup - Quick Start

## 🚀 What's New?

Your Docker Compose setup now has:

✅ **Health Checks** - Services wait until truly ready  
✅ **CI-Optimized Config** - Faster startup, minimal services  
✅ **GitHub Actions** - Ready-to-use E2E test workflow  
✅ **Health Endpoint** - `/health` endpoint for monitoring  
✅ **Complete Docs** - Full guide + quick reference  

## ⚡ Quick Test (30 seconds)

```bash
# Run the automated test script
./test-ci-setup.sh
```

This script will:
1. ✅ Clean up existing containers
2. ✅ Start services with health checks
3. ✅ Verify all services are healthy
4. ✅ Test the `/health` endpoint
5. ✅ Check database connectivity
6. ✅ Clean up automatically

## 📋 Manual Commands

### Start CI Environment
```bash
docker-compose -f docker-compose.ci.yml up --build --wait
```

### Run Tests
```bash
npm test
```

### Cleanup
```bash
docker-compose -f docker-compose.ci.yml down -v
```

### One-Line Full Test
```bash
docker-compose -f docker-compose.ci.yml down -v && \
docker-compose -f docker-compose.ci.yml up --build --wait && \
npm test && \
docker-compose -f docker-compose.ci.yml down -v
```

## 🔍 Health Check

### Test Manually
```bash
curl http://localhost:8000/health
```

### Expected Response
```json
{"status":"healthy"}
```

## 📁 New Files

| File | Purpose |
|------|---------|
| `docker-compose.ci.yml` | CI-optimized configuration |
| `.github/workflows/e2e-tests.yml` | GitHub Actions workflow |
| `test-ci-setup.sh` | Automated test script |
| `DOCKER_CI_GUIDE.md` | Complete documentation |
| `DOCKER_CI_QUICKREF.md` | Quick reference card |
| `DOCKER_CI_UPDATES_SUMMARY.md` | Changes summary |
| `CI_QUICKSTART.md` | This file |

## 🏗️ Development vs CI

### Development (`docker-compose.yml`)
```bash
docker-compose up --build
```
- Live code reload
- PgAdmin included
- Slower health checks (10s)
- Higher security (bcrypt 12 rounds)

### CI (`docker-compose.ci.yml`)
```bash
docker-compose -f docker-compose.ci.yml up --build --wait
```
- No volume mounts (consistent builds)
- Minimal services (faster)
- Fast health checks (5s)
- Fast tests (bcrypt 4 rounds)

## 🧪 GitHub Actions

### Workflow File
`.github/workflows/e2e-tests.yml`

### Triggers
- Push to `main` or `develop`
- Pull requests to `main`

### Steps
1. Checkout code
2. Setup Node.js
3. Install Playwright
4. Start Docker services (`--wait`)
5. Run E2E tests
6. Upload test reports
7. Cleanup

### Test Locally
```bash
# Simulate CI workflow
./test-ci-setup.sh
npm test
```

## 📖 Full Documentation

- **Complete Guide**: `DOCKER_CI_GUIDE.md`
- **Quick Reference**: `DOCKER_CI_QUICKREF.md`
- **Summary**: `DOCKER_CI_UPDATES_SUMMARY.md`

## 🎯 Benefits

### Before
❌ Services might not be ready when tests start  
❌ Race conditions in CI  
❌ Flaky tests  
❌ Manual wait times  

### After
✅ Services guaranteed healthy before tests  
✅ Reliable CI/CD execution  
✅ No race conditions  
✅ Automatic wait with `--wait` flag  

## 🔧 Troubleshooting

### Services won't start?
```bash
docker-compose -f docker-compose.ci.yml logs
```

### Health check failing?
```bash
curl -v http://localhost:8000/health
docker-compose -f docker-compose.ci.yml ps
```

### Port already in use?
```bash
lsof -i :8000
lsof -i :5432
```

## ✨ Next Steps

1. ✅ Run test script: `./test-ci-setup.sh`
2. ✅ Run E2E tests: `npm test`
3. ✅ Push to GitHub
4. ✅ Check Actions tab for workflow results

---

**Ready to test? Run:**
```bash
./test-ci-setup.sh
```
