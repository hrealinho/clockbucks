#!/bin/bash

# Clock Bucks Kubernetes Deployment Script

set -e

echo "🚀 Deploying Clock Bucks to Kubernetes..."

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if kubectl is installed
if ! command -v kubectl &> /dev/null; then
    print_error "kubectl is not installed. Please install kubectl first."
    exit 1
fi

# Check if cluster is accessible
if ! kubectl cluster-info &> /dev/null; then
    print_error "Cannot connect to Kubernetes cluster. Please check your kubeconfig."
    exit 1
fi

print_status "Connected to Kubernetes cluster"

# Create namespace
print_status "Creating namespace..."
kubectl apply -f k8s/namespace.yaml

# Apply ConfigMap and Secrets
print_status "Applying ConfigMap and Secrets..."
kubectl apply -f k8s/configmap.yaml

# Deploy PostgreSQL
print_status "Deploying PostgreSQL..."
kubectl apply -f k8s/postgres.yaml

# Wait for PostgreSQL to be ready
print_status "Waiting for PostgreSQL to be ready..."
kubectl wait --for=condition=ready pod -l app=postgres -n clockbucks --timeout=300s

# Deploy the API
print_status "Deploying Clock Bucks API..."
kubectl apply -f k8s/deployment.yaml

# Create services
print_status "Creating services..."
kubectl apply -f k8s/service.yaml

# Apply HPA
print_status "Setting up Horizontal Pod Autoscaler..."
kubectl apply -f k8s/hpa.yaml

# Apply Ingress (optional)
if [[ "$1" == "--with-ingress" ]]; then
    print_status "Applying Ingress..."
    kubectl apply -f k8s/ingress.yaml
fi

# Wait for deployment to be ready
print_status "Waiting for deployment to be ready..."
kubectl wait --for=condition=available deployment/clockbucks-api -n clockbucks --timeout=300s

print_success "Clock Bucks deployed successfully!"

# Show status
echo ""
print_status "Deployment Status:"
kubectl get pods -n clockbucks
echo ""
kubectl get services -n clockbucks
echo ""

# Get service URL
if kubectl get service clockbucks-api-nodeport -n clockbucks &> /dev/null; then
    NODE_PORT=$(kubectl get service clockbucks-api-nodeport -n clockbucks -o jsonpath='{.spec.ports[0].nodePort}')
    NODE_IP=$(kubectl get nodes -o jsonpath='{.items[0].status.addresses[?(@.type=="ExternalIP")].address}')
    if [[ -z "$NODE_IP" ]]; then
        NODE_IP=$(kubectl get nodes -o jsonpath='{.items[0].status.addresses[?(@.type=="InternalIP")].address}')
    fi
    
    print_success "API is accessible at: http://$NODE_IP:$NODE_PORT"
    print_success "API Documentation: http://$NODE_IP:$NODE_PORT/docs"
    print_success "Health Check: http://$NODE_IP:$NODE_PORT/health"
fi

echo ""
print_status "To check logs: kubectl logs -f deployment/clockbucks-api -n clockbucks"
print_status "To delete deployment: kubectl delete namespace clockbucks"
