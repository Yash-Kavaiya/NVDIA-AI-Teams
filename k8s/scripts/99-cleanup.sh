#!/bin/bash

# Script to clean up all deployed resources

set -e

NAMESPACE="nvidia-retail-ai"

echo "⚠️  WARNING: This will delete all resources in namespace: $NAMESPACE"
read -p "Are you sure you want to continue? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Cleanup cancelled."
    exit 1
fi

echo "=== Cleaning up resources ==="

# Delete in reverse order
echo "Deleting Ingress..."
kubectl delete -f ../manifests/07-ingress.yaml --ignore-not-found=true

echo "Deleting Frontend..."
kubectl delete -f ../manifests/06-frontend.yaml --ignore-not-found=true

echo "Deleting Agent..."
kubectl delete -f ../manifests/05-agent.yaml --ignore-not-found=true

echo "Deleting Qdrant..."
kubectl delete -f ../manifests/04-qdrant.yaml --ignore-not-found=true

echo "Deleting PVCs..."
kubectl delete -f ../manifests/03-pvc.yaml --ignore-not-found=true

echo "Deleting Secrets..."
kubectl delete -f ../manifests/02-secrets.yaml --ignore-not-found=true

echo "Deleting ConfigMap..."
kubectl delete -f ../manifests/01-configmap.yaml --ignore-not-found=true

echo "Deleting Namespace..."
kubectl delete -f ../manifests/00-namespace.yaml --ignore-not-found=true

echo ""
echo "✓ Cleanup complete!"
