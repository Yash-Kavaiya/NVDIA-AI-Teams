#!/bin/bash

# Script to configure AWS credentials and kubectl for EKS

set -e

echo "=== Setting up AWS Credentials ==="

# Check if AWS credentials are already configured
if [ -z "$AWS_ACCESS_KEY_ID" ] && [ -z "$AWS_PROFILE" ]; then
    echo "AWS credentials not found in environment."
    echo ""
    echo "Please configure AWS credentials using one of these methods:"
    echo ""
    echo "1. Set environment variables:"
    echo "   export AWS_ACCESS_KEY_ID=your-access-key"
    echo "   export AWS_SECRET_ACCESS_KEY=your-secret-key"
    echo "   export AWS_SESSION_TOKEN=your-session-token  # If using temporary credentials"
    echo "   export AWS_REGION=us-east-1"
    echo ""
    echo "2. Use AWS CLI configure:"
    echo "   aws configure"
    echo ""
    echo "3. Use AWS CLI SSO:"
    echo "   aws sso login --profile your-profile"
    echo "   export AWS_PROFILE=your-profile"
    echo ""
    exit 1
fi

# Set default region if not already set
export AWS_REGION="${AWS_REGION:-us-east-1}"

echo "Using AWS Region: $AWS_REGION"

# EKS Cluster details
CLUSTER_NAME="fabulous-alternative-potato"
CLUSTER_ARN="arn:aws:eks:us-east-1:661642944881:cluster/fabulous-alternative-potato"
API_ENDPOINT="https://10CC7E71CBCA51BED4FCA00D0AA8F52B.gr7.us-east-1.eks.amazonaws.com"
REGION="us-east-1"
ACCOUNT_ID="661642944881"

echo ""
echo "EKS Cluster Information:"
echo "  Name:     $CLUSTER_NAME"
echo "  Region:   $REGION"
echo "  Account:  $ACCOUNT_ID"
echo "  Endpoint: $API_ENDPOINT"
echo ""

# Verify AWS identity
echo "Verifying AWS identity..."
aws sts get-caller-identity

echo ""
echo "Configuring kubectl for EKS cluster: $CLUSTER_NAME"

# Update kubeconfig
aws eks update-kubeconfig --name $CLUSTER_NAME --region $REGION

# Verify connection
echo ""
echo "Verifying cluster connection..."
kubectl cluster-info

echo ""
echo "Checking cluster nodes..."
kubectl get nodes

echo ""
echo "Available namespaces:"
kubectl get namespaces

echo ""
echo "✓ AWS and kubectl setup complete!"
echo ""
echo "You can now deploy the application by running:"
echo "  ./03-deploy.sh"
