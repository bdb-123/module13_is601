# E2E Testing Quick Start

## 🚀 Setup (One-Time)

```bash
# Install Node.js dependencies
npm install

# Install Playwright browsers
npm run e2e:install
```

## ▶️ Run Tests

### Start the server first (in a separate terminal):

```bash
# Option 1: Direct Python
uvicorn app.main:app --host 0.0.0.0 --port 8000

# Option 2: Docker Compose
docker-compose up
```

### Then run tests:

```bash
# Run all tests (headless)
npm run e2e

# Run with interactive UI
npm run e2e:ui

# Run with visible browser
npm run e2e:headed

# Debug tests
npm run e2e:debug

# View report after tests
npm run e2e:report
```

## 📁 Files Created

```
├── package.json              # NPM config with Playwright dependency
├── playwright.config.js      # Playwright configuration
├── .gitignore               # Updated with node_modules/, playwright-report/
└── e2e/                     # Test directory
    ├── example.spec.js      # Setup verification tests
    ├── auth.spec.js         # Authentication tests
    └── home.spec.js         # Home page tests
```

## 🧪 What's Tested

- ✅ Server health check
- ✅ Login page loads and validates
- ✅ Register page loads and validates
- ✅ Email validation
- ✅ Password validation
- ✅ Password mismatch detection
- ✅ Navigation between pages

## 📝 Available Scripts

| Command | Description |
|---------|-------------|
| `npm run e2e` | Run all tests |
| `npm run e2e:ui` | Interactive UI mode |
| `npm run e2e:headed` | See browser while testing |
| `npm run e2e:debug` | Debug with Playwright Inspector |
| `npm run e2e:report` | View HTML report |

## 🔍 Run Specific Tests

```bash
# Run one file
npx playwright test e2e/auth.spec.js

# Run one browser
npx playwright test --project=chromium

# Run by test name
npx playwright test -g "should load login page"
```

## 📚 Documentation

See [E2E_SETUP.md](./E2E_SETUP.md) for complete documentation.
