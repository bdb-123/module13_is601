# Docker Compose CI/CD Guide

## Overview
This guide explains the Docker Compose configurations optimized for different environments and provides commands for reliable CI/CD execution.

## Configurations

### 1. `docker-compose.yml` (Development)
**Use Case**: Local development with live reload and debugging tools

**Features**:
- Volume mounts for live code reload
- PgAdmin for database inspection
- Moderate health check intervals (10s)
- Debug-friendly settings

**Start Command**:
```bash
docker-compose up --build
```

**Health Check Details**:
- **Web Service**: Checks `/health` endpoint every 10s
  - Timeout: 5s
  - Retries: 5
  - Start period: 10s
- **Database**: Uses `pg_isready` every 10s
  - Timeout: 5s
  - Retries: 5

---

### 2. `docker-compose.ci.yml` (CI/CD)
**Use Case**: Automated testing in CI/CD pipelines (GitHub Actions, GitLab CI, etc.)

**Features**:
- No volume mounts (ensures build consistency)
- Faster health checks (5s intervals)
- No PgAdmin (minimal services)
- Lower bcrypt rounds for faster tests (4 vs 12)
- Explicit database initialization in command

**Start Command**:
```bash
docker-compose -f docker-compose.ci.yml up --build --wait
```

**Health Check Details**:
- **Web Service**: Checks `/health` endpoint every 5s
  - Timeout: 3s
  - Retries: 5
  - Start period: 5s
- **Database**: Uses `pg_isready` every 5s
  - Timeout: 3s
  - Retries: 5

---

## CI/CD Workflow Examples

### GitHub Actions Workflow

```yaml
name: E2E Tests

on:
  push:
    branches: [ main, develop ]
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
      
      - name: Install Playwright dependencies
        run: |
          npm install
          npx playwright install --with-deps
      
      - name: Start services with health checks
        run: |
          docker-compose -f docker-compose.ci.yml up --build --wait --detach
      
      - name: Verify services are healthy
        run: |
          docker-compose -f docker-compose.ci.yml ps
          curl -f http://localhost:8000/health || exit 1
      
      - name: Run Playwright tests
        run: npm test
      
      - name: Upload test results
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: playwright-report
          path: playwright-report/
      
      - name: Cleanup
        if: always()
        run: docker-compose -f docker-compose.ci.yml down -v
```

### GitLab CI Pipeline

```yaml
stages:
  - test

e2e-tests:
  stage: test
  image: mcr.microsoft.com/playwright:v1.48.0-jammy
  services:
    - docker:dind
  variables:
    DOCKER_HOST: tcp://docker:2375
    DOCKER_TLS_CERTDIR: ""
  before_script:
    - npm install
  script:
    - docker-compose -f docker-compose.ci.yml up --build --wait --detach
    - docker-compose -f docker-compose.ci.yml ps
    - curl -f http://localhost:8000/health || exit 1
    - npm test
  after_script:
    - docker-compose -f docker-compose.ci.yml down -v
  artifacts:
    when: always
    paths:
      - playwright-report/
      - test-results/
```

---

## Manual CI Testing Commands

### Step-by-Step CI Simulation

```bash
# 1. Clean environment
docker-compose -f docker-compose.ci.yml down -v
docker system prune -f

# 2. Build and start services (wait for healthy status)
docker-compose -f docker-compose.ci.yml up --build --wait

# 3. Verify services are running and healthy
docker-compose -f docker-compose.ci.yml ps
curl -f http://localhost:8000/health

# 4. Check database connectivity
docker-compose -f docker-compose.ci.yml exec db psql -U postgres -c '\l'

# 5. Run tests
npm test

# 6. Cleanup
docker-compose -f docker-compose.ci.yml down -v
```

### Quick Test Cycle

```bash
# One-liner for rapid testing
docker-compose -f docker-compose.ci.yml down -v && \
docker-compose -f docker-compose.ci.yml up --build --wait && \
npm test && \
docker-compose -f docker-compose.ci.yml down -v
```

---

## Health Check Endpoints

### Application Health Check
**URL**: `http://localhost:8000/health`

**Expected Response**:
```json
{
  "status": "healthy"
}
```

**What it checks**:
- FastAPI application is running
- Uvicorn server is responding
- Application initialization completed

### Database Health Check
**Command**: `pg_isready -U postgres`

**What it checks**:
- PostgreSQL is accepting connections
- Database server is initialized
- Network connectivity is working

---

## Troubleshooting

### Services Won't Start

**Check container logs**:
```bash
docker-compose -f docker-compose.ci.yml logs web
docker-compose -f docker-compose.ci.yml logs db
```

**Common issues**:
1. **Port conflicts**: Ensure ports 8000 and 5432 are available
   ```bash
   lsof -i :8000
   lsof -i :5432
   ```

2. **Database not ready**: Increase `start_period` in healthcheck
   ```yaml
   healthcheck:
     start_period: 15s  # Increase from 5s
   ```

3. **Application initialization fails**: Check database_init.py logs
   ```bash
   docker-compose -f docker-compose.ci.yml exec web python -m app.database_init
   ```

### Health Checks Failing

**Test health endpoint manually**:
```bash
# Wait for container to start
sleep 10

# Test health endpoint
curl -v http://localhost:8000/health

# Check if uvicorn is running
docker-compose -f docker-compose.ci.yml exec web ps aux | grep uvicorn
```

**Check database connectivity from app**:
```bash
docker-compose -f docker-compose.ci.yml exec web python -c "
from app.database import engine
print(engine.connect())
"
```

### Tests Hanging or Timing Out

**Increase Playwright timeouts**:
```javascript
// In playwright.config.js
timeout: 60000,  // 60 seconds
expect: {
  timeout: 10000  // 10 seconds
}
```

**Check application logs during test**:
```bash
# In another terminal while tests run
docker-compose -f docker-compose.ci.yml logs -f web
```

---

## Environment Variables

### Development (`docker-compose.yml`)
```env
DATABASE_URL=postgresql://postgres:postgres@db:5432/fastapi_db
JWT_SECRET_KEY=super-secret-key-for-jwt-min-32-chars
BCRYPT_ROUNDS=12
```

### CI (`docker-compose.ci.yml`)
```env
DATABASE_URL=postgresql://postgres:postgres@db:5432/fastapi_db
JWT_SECRET_KEY=ci-test-secret-key-for-jwt-min-32-chars
BCRYPT_ROUNDS=4  # Faster for testing
```

**Override in CI**:
```bash
# GitHub Actions
env:
  JWT_SECRET_KEY: ${{ secrets.JWT_SECRET_KEY }}

# Command line
JWT_SECRET_KEY="my-secret" docker-compose -f docker-compose.ci.yml up
```

---

## Performance Tips

### Faster CI Builds

1. **Use layer caching**:
   ```yaml
   # GitHub Actions
   - uses: docker/setup-buildx-action@v2
   - uses: docker/build-push-action@v4
     with:
       cache-from: type=gha
       cache-to: type=gha,mode=max
   ```

2. **Parallel test execution**:
   ```bash
   npx playwright test --workers=4
   ```

3. **Skip unnecessary installations**:
   ```dockerfile
   # Use multi-stage builds in Dockerfile
   FROM python:3.10-slim as base
   # ... dependencies
   FROM base as test
   # ... test-only dependencies
   ```

### Resource Limits (Optional)

```yaml
# In docker-compose.ci.yml
services:
  web:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
        reservations:
          cpus: '1'
          memory: 512M
```

---

## Security Considerations

### CI Secrets Management

**Never commit**:
- Production JWT secrets
- Real database passwords
- API keys

**Use CI secrets**:
```yaml
# GitHub Actions
env:
  JWT_SECRET_KEY: ${{ secrets.JWT_SECRET_KEY }}
  DATABASE_URL: ${{ secrets.DATABASE_URL }}
```

### Test Data Isolation

- CI uses separate `fastapi_test_db` database
- Database is destroyed after each run (`down -v`)
- No persistent volumes in CI configuration

---

## Quick Reference

| Command | Purpose |
|---------|---------|
| `docker-compose up` | Start dev environment |
| `docker-compose -f docker-compose.ci.yml up --wait` | Start CI environment and wait for healthy |
| `docker-compose ps` | Check service status |
| `docker-compose logs web` | View application logs |
| `docker-compose down -v` | Stop and remove volumes |
| `curl http://localhost:8000/health` | Test health endpoint |
| `npm test` | Run Playwright tests |
| `npx playwright test --ui` | Run tests with UI |

---

## Additional Resources

- [Docker Compose Health Checks](https://docs.docker.com/compose/compose-file/#healthcheck)
- [Playwright CI Guide](https://playwright.dev/docs/ci)
- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/)
- [PostgreSQL Docker](https://hub.docker.com/_/postgres)
