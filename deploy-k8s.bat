@echo off
REM Clock Bucks Kubernetes Deployment Script for Windows

echo 🚀 Deploying Clock Bucks to Kubernetes...

REM Check if kubectl is installed
kubectl version --client >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] kubectl is not installed. Please install kubectl first.
    exit /b 1
)

REM Check if cluster is accessible
kubectl cluster-info >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Cannot connect to Kubernetes cluster. Please check your kubeconfig.
    exit /b 1
)

echo [INFO] Connected to Kubernetes cluster

REM Create namespace
echo [INFO] Creating namespace...
kubectl apply -f k8s/namespace.yaml

REM Apply ConfigMap and Secrets
echo [INFO] Applying ConfigMap and Secrets...
kubectl apply -f k8s/configmap.yaml

REM Deploy PostgreSQL
echo [INFO] Deploying PostgreSQL...
kubectl apply -f k8s/postgres.yaml

REM Wait for PostgreSQL to be ready
echo [INFO] Waiting for PostgreSQL to be ready...
kubectl wait --for=condition=ready pod -l app=postgres -n clockbucks --timeout=300s

REM Deploy the API
echo [INFO] Deploying Clock Bucks API...
kubectl apply -f k8s/deployment.yaml

REM Create services
echo [INFO] Creating services...
kubectl apply -f k8s/service.yaml

REM Apply HPA
echo [INFO] Setting up Horizontal Pod Autoscaler...
kubectl apply -f k8s/hpa.yaml

REM Apply Ingress if requested
if "%1"=="--with-ingress" (
    echo [INFO] Applying Ingress...
    kubectl apply -f k8s/ingress.yaml
)

REM Wait for deployment to be ready
echo [INFO] Waiting for deployment to be ready...
kubectl wait --for=condition=available deployment/clockbucks-api -n clockbucks --timeout=300s

echo [SUCCESS] Clock Bucks deployed successfully!

echo.
echo [INFO] Deployment Status:
kubectl get pods -n clockbucks
echo.
kubectl get services -n clockbucks
echo.

echo [INFO] To check logs: kubectl logs -f deployment/clockbucks-api -n clockbucks
echo [INFO] To delete deployment: kubectl delete namespace clockbucks

pause
