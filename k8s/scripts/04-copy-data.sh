#!/bin/bash

# Script to copy inventory data to the agent persistent volume

set -e

NAMESPACE="nvidia-retail-ai"

echo "=== Copying Data to Persistent Volumes ==="

# Wait for agent pod to be ready
echo "Waiting for agent pod to be ready..."
kubectl wait --for=condition=ready pod -l app=agent -n $NAMESPACE --timeout=300s

# Get the first agent pod name
AGENT_POD=$(kubectl get pods -n $NAMESPACE -l app=agent -o jsonpath='{.items[0].metadata.name}')

echo "Copying inventory data to pod: $AGENT_POD"

# Copy inventory data
kubectl cp ../inventory_data $NAMESPACE/$AGENT_POD:/app/inventory_data

echo "✓ Data copied successfully!"
