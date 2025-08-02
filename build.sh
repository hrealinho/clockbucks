#!/bin/bash

# Clock Bucks Build and Test Script

set -e

echo "🔨 Building Clock Bucks..."

# Color codes
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

# Build Docker image
print_status "Building Docker image..."
docker build -t clockbucks-api:latest .

print_success "Docker image built successfully"

# Run tests in container
print_status "Running tests..."
docker run --rm clockbucks-api:latest python dev_test.py

print_success "Tests completed successfully"

# Build production image
print_status "Building production image..."
docker build -f Dockerfile.prod -t clockbucks-api:prod .

print_success "Production image built successfully"

echo ""
print_status "Available images:"
docker images | grep clockbucks-api

echo ""
print_success "Build completed! 🎉"
echo ""
echo "Next steps:"
echo "1. Test locally: docker run -p 8000:8000 clockbucks-api:latest"
echo "2. Deploy to Kubernetes: ./deploy-k8s.sh"
echo "3. View API docs: http://localhost:8000/docs"
