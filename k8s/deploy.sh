#!/bin/bash

# NVIDIA Retail AI - EKS Deployment Script
# This script deploys the entire solution to AWS EKS

set -e

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
CLUSTER_NAME="nvidia-retail-ai-cluster"
REGION="us-east-1"  # Change to your preferred region
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
ECR_REGISTRY="${AWS_ACCOUNT_ID}.dkr.ecr.${REGION}.amazonaws.com"
NAMESPACE="nvidia-retail-ai"

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}NVIDIA Retail AI - EKS Deployment${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check prerequisites
echo -e "${YELLOW}Checking prerequisites...${NC}"
if ! command_exists aws; then
    echo -e "${RED}ERROR: AWS CLI is not installed${NC}"
    exit 1
fi

if ! command_exists kubectl; then
    echo -e "${RED}ERROR: kubectl is not installed${NC}"
    exit 1
fi

if ! command_exists docker; then
    echo -e "${RED}ERROR: Docker is not installed${NC}"
    exit 1
fi

echo -e "${GREEN}All prerequisites installed${NC}"
echo ""

# Step 1: Create ECR Repositories
echo -e "${YELLOW}Step 1: Creating ECR repositories...${NC}"
aws ecr create-repository \
    --repository-name nvidia-retail-ai/ui-frontend \
    --region ${REGION} \
    --image-scanning-configuration scanOnPush=true \
    || echo "Repository already exists"

aws ecr create-repository \
    --repository-name nvidia-retail-ai/agent-backend \
    --region ${REGION} \
    --image-scanning-configuration scanOnPush=true \
    || echo "Repository already exists"

echo -e "${GREEN}ECR repositories created${NC}"
echo ""

# Step 2: Build and Push Docker Images
echo -e "${YELLOW}Step 2: Building and pushing Docker images...${NC}"

# Login to ECR
aws ecr get-login-password --region ${REGION} | \
    docker login --username AWS --password-stdin ${ECR_REGISTRY}

# Build and push UI frontend
echo "Building UI frontend..."
cd ../nvdia-ag-ui
docker build -t ${ECR_REGISTRY}/nvidia-retail-ai/ui-frontend:latest \
    -f Dockerfile .
docker push ${ECR_REGISTRY}/nvidia-retail-ai/ui-frontend:latest

# Build and push Agent backend
echo "Building Agent backend..."
cd agent
docker build -t ${ECR_REGISTRY}/nvidia-retail-ai/agent-backend:latest \
    -f Dockerfile .
docker push ${ECR_REGISTRY}/nvidia-retail-ai/agent-backend:latest

cd ../../k8s

echo -e "${GREEN}Docker images built and pushed${NC}"
echo ""

# Step 3: Update Kubernetes manifests with actual values
echo -e "${YELLOW}Step 3: Updating Kubernetes manifests...${NC}"

# Create a working copy of manifests
mkdir -p deploy
cp -r base/* deploy/

# Replace placeholders
find deploy/ -type f -name "*.yaml" -exec sed -i \
    -e "s|<AWS_ACCOUNT_ID>|${AWS_ACCOUNT_ID}|g" \
    -e "s|<AWS_REGION>|${REGION}|g" {} \;

echo -e "${GREEN}Manifests updated${NC}"
echo ""

# Step 4: Create IAM Role for Service Account (IRSA)
echo -e "${YELLOW}Step 4: Creating IAM role for service account...${NC}"

# Create IAM policy
POLICY_ARN=$(aws iam create-policy \
    --policy-name nvidia-retail-ai-agent-policy \
    --policy-document file://iam-policy.json \
    --query 'Policy.Arn' \
    --output text 2>/dev/null || \
    aws iam list-policies --query 'Policies[?PolicyName==`nvidia-retail-ai-agent-policy`].Arn' --output text)

echo "IAM Policy ARN: ${POLICY_ARN}"

# Create IRSA
eksctl create iamserviceaccount \
    --name agent-backend-sa \
    --namespace ${NAMESPACE} \
    --cluster ${CLUSTER_NAME} \
    --region ${REGION} \
    --attach-policy-arn ${POLICY_ARN} \
    --approve \
    --override-existing-serviceaccounts \
    || echo "IRSA already exists"

echo -e "${GREEN}IAM role created${NC}"
echo ""

# Step 5: Create secrets
echo -e "${YELLOW}Step 5: Setting up secrets...${NC}"
echo -e "${RED}WARNING: You need to create secrets manually!${NC}"
echo "Run the following commands:"
echo ""
echo "kubectl create secret generic api-keys \\"
echo "  --from-literal=google-api-key=YOUR_GOOGLE_API_KEY \\"
echo "  --from-literal=nvidia-api-key=YOUR_NVIDIA_API_KEY \\"
echo "  -n ${NAMESPACE}"
echo ""
read -p "Press enter once secrets are created..."

# Step 6: Deploy to Kubernetes
echo -e "${YELLOW}Step 6: Deploying to Kubernetes...${NC}"

# Update kubeconfig
aws eks update-kubeconfig --name ${CLUSTER_NAME} --region ${REGION}

# Create namespace
kubectl apply -f deploy/namespace.yaml

# Deploy ConfigMap
kubectl apply -f deploy/configmap.yaml

# Deploy Qdrant
kubectl apply -f deploy/qdrant-deployment.yaml

# Wait for Qdrant to be ready
echo "Waiting for Qdrant to be ready..."
kubectl wait --for=condition=ready pod -l app=qdrant -n ${NAMESPACE} --timeout=300s

# Deploy Agent Backend
kubectl apply -f deploy/agent-deployment.yaml

# Wait for Agent to be ready
echo "Waiting for Agent backend to be ready..."
kubectl wait --for=condition=ready pod -l app=agent-backend -n ${NAMESPACE} --timeout=300s

# Deploy UI Frontend
kubectl apply -f deploy/ui-deployment.yaml

echo -e "${GREEN}All components deployed${NC}"
echo ""

# Step 7: Display status
echo -e "${YELLOW}Step 7: Deployment status${NC}"
kubectl get all -n ${NAMESPACE}

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Deployment Complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "To get the load balancer URL:"
echo "kubectl get ingress -n ${NAMESPACE}"
echo ""
echo "To view logs:"
echo "kubectl logs -f deployment/agent-backend -n ${NAMESPACE}"
echo "kubectl logs -f deployment/ui-frontend -n ${NAMESPACE}"
echo ""
echo "To access Qdrant dashboard (port-forward):"
echo "kubectl port-forward svc/qdrant 6333:6333 -n ${NAMESPACE}"
