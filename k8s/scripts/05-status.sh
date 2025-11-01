#!/bin/bash

# Script to check deployment status

NAMESPACE="nvidia-retail-ai"

echo "=== Deployment Status ==="
echo ""

echo "Pods:"
kubectl get pods -n $NAMESPACE -o wide

echo ""
echo "Services:"
kubectl get svc -n $NAMESPACE

echo ""
echo "Persistent Volume Claims:"
kubectl get pvc -n $NAMESPACE

echo ""
echo "Ingress:"
kubectl get ingress -n $NAMESPACE 2>/dev/null || echo "No ingress configured"

echo ""
echo "=== Frontend URL ==="
FRONTEND_URL=$(kubectl get svc frontend-service -n $NAMESPACE -o jsonpath='{.status.loadBalancer.ingress[0].hostname}' 2>/dev/null)
if [ -n "$FRONTEND_URL" ]; then
    echo "Frontend: http://$FRONTEND_URL"
else
    echo "Frontend LoadBalancer is still provisioning..."
fi

echo ""
echo "=== Recent Pod Events ==="
kubectl get events -n $NAMESPACE --sort-by='.lastTimestamp' | tail -10

echo ""
echo "=== Pod Logs (last 20 lines) ==="
echo "Agent logs:"
kubectl logs -n $NAMESPACE -l app=agent --tail=20 2>/dev/null || echo "Agent not ready"
echo ""
echo "Frontend logs:"
kubectl logs -n $NAMESPACE -l app=frontend --tail=20 2>/dev/null || echo "Frontend not ready"
