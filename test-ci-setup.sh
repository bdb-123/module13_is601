#!/bin/bash

# CI Docker Setup Test Script
# This script tests the CI-optimized Docker Compose configuration

set -e  # Exit on any error

echo "========================================="
echo "CI Docker Setup Test"
echo "========================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${YELLOW}ℹ️  $1${NC}"
}

# Step 1: Cleanup any existing containers
print_info "Step 1: Cleaning up existing containers..."
docker-compose -f docker-compose.ci.yml down -v 2>/dev/null || true
print_success "Cleanup complete"
echo ""

# Step 2: Build and start services
print_info "Step 2: Building and starting services with health checks..."
if docker-compose -f docker-compose.ci.yml up --build --wait --detach; then
    print_success "Services started successfully"
else
    print_error "Failed to start services"
    docker-compose -f docker-compose.ci.yml logs
    exit 1
fi
echo ""

# Step 3: Verify service status
print_info "Step 3: Verifying service status..."
docker-compose -f docker-compose.ci.yml ps
echo ""

# Step 4: Test health endpoint
print_info "Step 4: Testing /health endpoint..."
sleep 2  # Give services a moment to stabilize
if curl -f http://localhost:8000/health 2>/dev/null; then
    echo ""
    print_success "Health endpoint responding correctly"
else
    print_error "Health endpoint not responding"
    docker-compose -f docker-compose.ci.yml logs web
    exit 1
fi
echo ""

# Step 5: Test database connectivity
print_info "Step 5: Testing database connectivity..."
if docker-compose -f docker-compose.ci.yml exec -T db psql -U postgres -c '\l' > /dev/null 2>&1; then
    print_success "Database is accessible"
else
    print_error "Database connection failed"
    docker-compose -f docker-compose.ci.yml logs db
    exit 1
fi
echo ""

# Step 6: Check if test database exists
print_info "Step 6: Checking for test database..."
if docker-compose -f docker-compose.ci.yml exec -T db psql -U postgres -lqt | cut -d \| -f 1 | grep -qw fastapi_test_db; then
    print_success "Test database 'fastapi_test_db' exists"
else
    print_error "Test database not found"
    exit 1
fi
echo ""

# Step 7: Run a quick API test
print_info "Step 7: Testing API root endpoint..."
if curl -f http://localhost:8000/ 2>/dev/null > /dev/null; then
    print_success "API root endpoint accessible"
else
    print_error "API root endpoint not accessible"
    exit 1
fi
echo ""

# Step 8: Cleanup
print_info "Step 8: Cleaning up..."
docker-compose -f docker-compose.ci.yml down -v
print_success "Cleanup complete"
echo ""

echo "========================================="
print_success "All tests passed!"
echo "========================================="
echo ""
echo "Your CI Docker setup is working correctly!"
echo ""
echo "Next steps:"
echo "1. Run Playwright tests: npm test"
echo "2. Push to GitHub to trigger CI workflow"
echo "3. Check .github/workflows/e2e-tests.yml for workflow results"
echo ""
