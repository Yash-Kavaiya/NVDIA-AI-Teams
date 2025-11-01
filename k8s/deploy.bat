@echo off
REM NVIDIA Retail AI - EKS Deployment Script for Windows
REM This script deploys the entire solution to AWS EKS

setlocal enabledelayedexpansion

REM Configuration
set CLUSTER_NAME=nvidia-retail-ai-cluster
set REGION=us-east-1
set NAMESPACE=nvidia-retail-ai

echo ========================================
echo NVIDIA Retail AI - EKS Deployment
echo ========================================
echo.

REM Get AWS Account ID
for /f "tokens=*" %%i in ('aws sts get-caller-identity --query Account --output text') do set AWS_ACCOUNT_ID=%%i
set ECR_REGISTRY=%AWS_ACCOUNT_ID%.dkr.ecr.%REGION%.amazonaws.com

echo AWS Account ID: %AWS_ACCOUNT_ID%
echo ECR Registry: %ECR_REGISTRY%
echo.

REM Check prerequisites
echo Checking prerequisites...
where aws >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: AWS CLI is not installed
    exit /b 1
)

where kubectl >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: kubectl is not installed
    exit /b 1
)

where docker >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Docker is not installed
    exit /b 1
)

echo All prerequisites installed
echo.

REM Step 1: Create ECR Repositories
echo Step 1: Creating ECR repositories...
aws ecr create-repository --repository-name nvidia-retail-ai/ui-frontend --region %REGION% --image-scanning-configuration scanOnPush=true 2>nul || echo Repository already exists

aws ecr create-repository --repository-name nvidia-retail-ai/agent-backend --region %REGION% --image-scanning-configuration scanOnPush=true 2>nul || echo Repository already exists

echo ECR repositories created
echo.

REM Step 2: Build and Push Docker Images
echo Step 2: Building and pushing Docker images...

REM Login to ECR
aws ecr get-login-password --region %REGION% | docker login --username AWS --password-stdin %ECR_REGISTRY%

REM Build and push UI frontend
echo Building UI frontend...
cd ..\nvdia-ag-ui
docker build -t %ECR_REGISTRY%/nvidia-retail-ai/ui-frontend:latest -f Dockerfile .
docker push %ECR_REGISTRY%/nvidia-retail-ai/ui-frontend:latest

REM Build and push Agent backend
echo Building Agent backend...
cd agent
docker build -t %ECR_REGISTRY%/nvidia-retail-ai/agent-backend:latest -f Dockerfile .
docker push %ECR_REGISTRY%/nvidia-retail-ai/agent-backend:latest

cd ..\..\k8s

echo Docker images built and pushed
echo.

REM Step 3: Update Kubernetes manifests
echo Step 3: Updating Kubernetes manifests...

REM Create deploy directory
if not exist deploy mkdir deploy
xcopy /E /I /Y base deploy >nul

REM Replace placeholders (using PowerShell for easier text replacement)
powershell -Command "(Get-ChildItem -Path deploy -Filter *.yaml -Recurse) | ForEach-Object { (Get-Content $_.FullName) -replace '<AWS_ACCOUNT_ID>', '%AWS_ACCOUNT_ID%' -replace '<AWS_REGION>', '%REGION%' | Set-Content $_.FullName }"

echo Manifests updated
echo.

REM Step 4: Create IAM Role
echo Step 4: Creating IAM role for service account...
REM Note: This requires eksctl and is complex on Windows
REM Run the Linux script using WSL or Git Bash if available

echo SKIPPING IAM role creation on Windows
echo Please run this on Linux/Mac or use WSL:
echo eksctl create iamserviceaccount --name agent-backend-sa --namespace %NAMESPACE% --cluster %CLUSTER_NAME% --region %REGION% --attach-policy-arn POLICY_ARN --approve
echo.

REM Step 5: Create secrets
echo Step 5: Setting up secrets...
echo WARNING: You need to create secrets manually!
echo.
echo Run the following command:
echo kubectl create secret generic api-keys --from-literal=google-api-key=YOUR_GOOGLE_API_KEY --from-literal=nvidia-api-key=YOUR_NVIDIA_API_KEY -n %NAMESPACE%
echo.
pause

REM Step 6: Deploy to Kubernetes
echo Step 6: Deploying to Kubernetes...

REM Update kubeconfig
aws eks update-kubeconfig --name %CLUSTER_NAME% --region %REGION%

REM Create namespace
kubectl apply -f deploy\namespace.yaml

REM Deploy ConfigMap
kubectl apply -f deploy\configmap.yaml

REM Deploy Qdrant
kubectl apply -f deploy\qdrant-deployment.yaml

REM Wait for Qdrant
echo Waiting for Qdrant to be ready...
kubectl wait --for=condition=ready pod -l app=qdrant -n %NAMESPACE% --timeout=300s

REM Deploy Agent Backend
kubectl apply -f deploy\agent-deployment.yaml

REM Wait for Agent
echo Waiting for Agent backend to be ready...
kubectl wait --for=condition=ready pod -l app=agent-backend -n %NAMESPACE% --timeout=300s

REM Deploy UI Frontend
kubectl apply -f deploy\ui-deployment.yaml

echo All components deployed
echo.

REM Step 7: Display status
echo Step 7: Deployment status
kubectl get all -n %NAMESPACE%

echo.
echo ========================================
echo Deployment Complete!
echo ========================================
echo.
echo To get the load balancer URL:
echo kubectl get ingress -n %NAMESPACE%
echo.
echo To view logs:
echo kubectl logs -f deployment/agent-backend -n %NAMESPACE%
echo kubectl logs -f deployment/ui-frontend -n %NAMESPACE%
echo.

endlocal
