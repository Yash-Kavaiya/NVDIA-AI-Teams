#!/bin/bash

# Script to deploy all resources to EKS

set -e

NAMESPACE="nvidia-retail-ai"

echo "=== Deploying to EKS ==="

# Apply manifests in order
echo "Creating namespace..."
kubectl apply -f ../manifests/00-namespace.yaml

echo "Creating ConfigMap..."
kubectl apply -f ../manifests/01-configmap.yaml

echo "Creating Secrets..."
echo "⚠️  WARNING: Update the secrets in 02-secrets.yaml with your actual API keys before deploying!"
read -p "Have you updated the secrets? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Please update the secrets and run this script again."
    exit 1
fi
kubectl apply -f ../manifests/02-secrets.yaml

echo "Creating PersistentVolumeClaims..."
kubectl apply -f ../manifests/03-pvc.yaml

echo "Deploying Qdrant..."
kubectl apply -f ../manifests/04-qdrant.yaml

echo "Waiting for Qdrant to be ready..."
kubectl wait --for=condition=ready pod -l app=qdrant -n $NAMESPACE --timeout=300s

echo "Deploying Agent..."
kubectl apply -f ../manifests/05-agent.yaml

echo "Deploying Frontend..."
kubectl apply -f ../manifests/06-frontend.yaml

echo "Creating Ingress (optional)..."
kubectl apply -f ../manifests/07-ingress.yaml 2>/dev/null || echo "Skipping Ingress (may require AWS Load Balancer Controller)"

echo ""
echo "✓ Deployment complete!"
echo ""
echo "Checking deployment status..."
kubectl get all -n $NAMESPACE

echo ""
echo "To get the frontend URL, run:"
echo "kubectl get svc frontend-service -n $NAMESPACE -o jsonpath='{.status.loadBalancer.ingress[0].hostname}'"
