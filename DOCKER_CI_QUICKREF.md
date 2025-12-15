# Docker CI Quick Reference

## 🚀 Quick Start Commands

### Development Environment
```bash
# Start with live reload
docker-compose up --build

# Stop and clean
docker-compose down -v
```

### CI Environment
```bash
# Start and wait for healthy status
docker-compose -f docker-compose.ci.yml up --build --wait

# Run tests
npm test

# Cleanup
docker-compose -f docker-compose.ci.yml down -v
```

## 📋 One-Line Test Cycle
```bash
docker-compose -f docker-compose.ci.yml down -v && \
docker-compose -f docker-compose.ci.yml up --build --wait && \
npm test && \
docker-compose -f docker-compose.ci.yml down -v
```

## 🔍 Health Check URLs

| Service | URL | Expected Response |
|---------|-----|-------------------|
| App | http://localhost:8000/health | `{"status":"healthy"}` |
| Database | `pg_isready -U postgres` | Exit code 0 |

## 🏗️ Configuration Differences

| Feature | docker-compose.yml | docker-compose.ci.yml |
|---------|-------------------|----------------------|
| **Purpose** | Development | CI/CD Testing |
| **Volumes** | ✅ Mounted | ❌ None |
| **PgAdmin** | ✅ Included | ❌ Excluded |
| **Health Interval** | 10s | 5s |
| **Bcrypt Rounds** | 12 | 4 |
| **Reload** | ✅ Auto | ❌ Manual |

## 🐛 Troubleshooting

### Check Service Status
```bash
docker-compose -f docker-compose.ci.yml ps
```

### View Logs
```bash
docker-compose -f docker-compose.ci.yml logs web
docker-compose -f docker-compose.ci.yml logs db
```

### Test Health Endpoint
```bash
curl -f http://localhost:8000/health
```

### Check Database
```bash
docker-compose -f docker-compose.ci.yml exec db psql -U postgres -c '\l'
```

## 🔧 GitHub Actions Template

```yaml
name: E2E Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - uses: actions/setup-node@v3
        with:
          node-version: '18'
      
      - name: Install dependencies
        run: |
          npm install
          npx playwright install --with-deps
      
      - name: Start services
        run: docker-compose -f docker-compose.ci.yml up --build --wait -d
      
      - name: Run tests
        run: npm test
      
      - name: Cleanup
        if: always()
        run: docker-compose -f docker-compose.ci.yml down -v
```

## 📊 Health Check Settings

### Web Service
```yaml
healthcheck:
  test: ["CMD-SHELL", "curl -f http://localhost:8000/health || exit 1"]
  interval: 5s      # CI: 5s, Dev: 10s
  timeout: 3s       # CI: 3s, Dev: 5s
  retries: 5
  start_period: 5s  # CI: 5s, Dev: 10s
```

### Database Service
```yaml
healthcheck:
  test: ["CMD-SHELL", "pg_isready -U postgres"]
  interval: 5s      # CI: 5s, Dev: 10s
  timeout: 3s       # CI: 3s, Dev: 5s
  retries: 5
```

## 🎯 Environment Variables

### Development
- `BCRYPT_ROUNDS=12` (secure)
- `JWT_SECRET_KEY=super-secret-key-for-jwt-min-32-chars`

### CI
- `BCRYPT_ROUNDS=4` (fast)
- `JWT_SECRET_KEY=ci-test-secret-key-for-jwt-min-32-chars`

## ⚡ Performance Tips

1. **Use --wait flag**: Automatically waits for healthy status
2. **Parallel tests**: `npx playwright test --workers=4`
3. **Layer caching**: Use Docker buildx with GitHub Actions cache
4. **Cleanup volumes**: Always use `-v` flag with `down`

## 📖 Full Documentation
See `DOCKER_CI_GUIDE.md` for complete documentation.
