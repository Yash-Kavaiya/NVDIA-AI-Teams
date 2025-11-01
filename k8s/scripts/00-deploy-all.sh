#!/bin/bash

# Master deployment script - runs all deployment steps in order

set -e

echo "╔════════════════════════════════════════════════════════════╗"
echo "║     NVIDIA Retail AI - EKS Deployment Master Script       ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_step() {
    echo -e "${GREEN}[STEP]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check prerequisites
print_step "Checking prerequisites..."

command -v aws >/dev/null 2>&1 || { print_error "AWS CLI is required but not installed. Aborting."; exit 1; }
command -v kubectl >/dev/null 2>&1 || { print_error "kubectl is required but not installed. Aborting."; exit 1; }
command -v docker >/dev/null 2>&1 || { print_error "Docker is required but not installed. Aborting."; exit 1; }

print_step "✓ All prerequisites met"
echo ""

# Step 1: Setup AWS and kubectl
print_step "Step 1/5: Setting up AWS credentials and kubectl..."
./01-setup-aws.sh
if [ $? -ne 0 ]; then
    print_error "AWS setup failed. Aborting."
    exit 1
fi
echo ""

# Step 2: Build and push images
print_step "Step 2/5: Building and pushing Docker images to ECR..."
print_warning "This may take 10-15 minutes depending on your internet connection."
./02-build-and-push.sh
if [ $? -ne 0 ]; then
    print_error "Build and push failed. Aborting."
    exit 1
fi
echo ""

# Step 3: Deploy to Kubernetes
print_step "Step 3/5: Deploying to EKS..."
./03-deploy.sh
if [ $? -ne 0 ]; then
    print_error "Deployment failed. Aborting."
    exit 1
fi
echo ""

# Step 4: Copy data
print_step "Step 4/5: Copying data to persistent volumes..."
./04-copy-data.sh
if [ $? -ne 0 ]; then
    print_warning "Data copy failed, but deployment continues. You may need to copy data manually."
fi
echo ""

# Step 5: Check status
print_step "Step 5/5: Checking deployment status..."
./05-status.sh
echo ""

# Final summary
echo "╔════════════════════════════════════════════════════════════╗"
echo "║                  Deployment Complete! 🎉                   ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
echo "Next steps:"
echo "1. Wait for LoadBalancer to provision (may take 5-10 minutes)"
echo "2. Get frontend URL:"
echo "   kubectl get svc frontend-service -n nvidia-retail-ai"
echo ""
echo "3. Access the application in your browser"
echo ""
echo "To monitor the deployment:"
echo "   ./05-status.sh"
echo ""
echo "To view logs:"
echo "   kubectl logs -f -n nvidia-retail-ai -l app=agent"
echo "   kubectl logs -f -n nvidia-retail-ai -l app=frontend"
echo ""

