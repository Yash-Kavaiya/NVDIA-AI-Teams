#!/bin/bash

# Script to build Docker images and push to Amazon ECR

set -e

# Configuration
AWS_ACCOUNT_ID="661642944881"
AWS_REGION="us-east-1"
ECR_REGISTRY="${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com"

# Repository names
FRONTEND_REPO="nvidia-retail-frontend"
AGENT_REPO="nvidia-retail-agent"

echo "=== Building and Pushing Docker Images to ECR ==="

# Authenticate Docker to ECR
echo "Authenticating to ECR..."
aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $ECR_REGISTRY

# Create ECR repositories if they don't exist
echo "Creating ECR repositories..."
aws ecr create-repository --repository-name $FRONTEND_REPO --region $AWS_REGION 2>/dev/null || echo "Repository $FRONTEND_REPO already exists"
aws ecr create-repository --repository-name $AGENT_REPO --region $AWS_REGION 2>/dev/null || echo "Repository $AGENT_REPO already exists"

# Build and push frontend image
echo "Building frontend image..."
cd ../nvdia-ag-ui
docker build -t $FRONTEND_REPO:latest .
docker tag $FRONTEND_REPO:latest $ECR_REGISTRY/$FRONTEND_REPO:latest
echo "Pushing frontend image to ECR..."
docker push $ECR_REGISTRY/$FRONTEND_REPO:latest

# Build and push agent image
echo "Building agent image..."
cd agent
docker build -t $AGENT_REPO:latest .
docker tag $AGENT_REPO:latest $ECR_REGISTRY/$AGENT_REPO:latest
echo "Pushing agent image to ECR..."
docker push $ECR_REGISTRY/$AGENT_REPO:latest

echo "✓ All images built and pushed successfully!"
echo ""
echo "Frontend image: $ECR_REGISTRY/$FRONTEND_REPO:latest"
echo "Agent image: $ECR_REGISTRY/$AGENT_REPO:latest"
