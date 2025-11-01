# Quick Reference Card

## Cluster Access

```bash
# Configure kubectl
aws eks update-kubeconfig --name fabulous-alternative-potato --region us-east-1

# Verify connection
kubectl get nodes
```

## Deploy Application

```bash
cd k8s/scripts

# 1. Setup credentials
source aws-credentials.sh  # After creating from template

# 2. Run full deployment
./00-deploy-all.sh

# OR run steps individually:
./01-setup-aws.sh          # Configure kubectl
./02-build-and-push.sh     # Build & push images
./03-deploy.sh             # Deploy to EKS
./04-copy-data.sh          # Copy data files
```

## Check Status

```bash
# Quick status
./05-status.sh

# Manual checks
kubectl get all -n nvidia-retail-ai
kubectl get pods -n nvidia-retail-ai
kubectl get svc -n nvidia-retail-ai

# Get frontend URL
kubectl get svc frontend-service -n nvidia-retail-ai -o jsonpath='{.status.loadBalancer.ingress[0].hostname}'
```

## View Logs

```bash
# Agent logs
kubectl logs -f -n nvidia-retail-ai -l app=agent

# Frontend logs  
kubectl logs -f -n nvidia-retail-ai -l app=frontend

# Qdrant logs
kubectl logs -f -n nvidia-retail-ai -l app=qdrant

# Last 100 lines
kubectl logs -n nvidia-retail-ai -l app=agent --tail=100
```

## Troubleshooting

```bash
# Describe pod (see events and issues)
kubectl describe pod <pod-name> -n nvidia-retail-ai

# Get pod events
kubectl get events -n nvidia-retail-ai --sort-by='.lastTimestamp'

# Shell into a pod
kubectl exec -it <pod-name> -n nvidia-retail-ai -- /bin/sh

# Check resource usage
kubectl top pods -n nvidia-retail-ai
kubectl top nodes
```

## Update Deployment

```bash
# Rebuild and push new images
./02-build-and-push.sh

# Restart deployments to use new images
kubectl rollout restart deployment agent -n nvidia-retail-ai
kubectl rollout restart deployment frontend -n nvidia-retail-ai

# Watch rollout status
kubectl rollout status deployment agent -n nvidia-retail-ai
```

## Port Forwarding

```bash
# Access Qdrant dashboard
kubectl port-forward -n nvidia-retail-ai svc/qdrant 6333:6333
# Open http://localhost:6333/dashboard

# Access agent API directly
kubectl port-forward -n nvidia-retail-ai svc/agent-service 8000:8000
# Open http://localhost:8000

# Access frontend locally
kubectl port-forward -n nvidia-retail-ai svc/frontend-service 3000:80
# Open http://localhost:3000
```

## Configuration Updates

```bash
# Edit ConfigMap
kubectl edit configmap nvidia-retail-config -n nvidia-retail-ai

# Edit Secrets
kubectl edit secret nvidia-retail-secrets -n nvidia-retail-ai

# Apply updated manifest
kubectl apply -f k8s/manifests/01-configmap.yaml

# Restart pods to pick up changes
kubectl rollout restart deployment agent -n nvidia-retail-ai
```

## Scaling

```bash
# Scale deployments
kubectl scale deployment agent --replicas=3 -n nvidia-retail-ai
kubectl scale deployment frontend --replicas=3 -n nvidia-retail-ai

# Auto-scale based on CPU
kubectl autoscale deployment agent --cpu-percent=50 --min=2 --max=10 -n nvidia-retail-ai
```

## ECR Management

```bash
# Login to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 661642944881.dkr.ecr.us-east-1.amazonaws.com

# List images
aws ecr describe-images --repository-name nvidia-retail-agent --region us-east-1
aws ecr describe-images --repository-name nvidia-retail-frontend --region us-east-1

# Delete old images
aws ecr batch-delete-image --repository-name nvidia-retail-agent --image-ids imageTag=old-tag --region us-east-1
```

## Cleanup

```bash
# Delete entire deployment
./99-cleanup.sh

# Delete specific resources
kubectl delete deployment agent -n nvidia-retail-ai
kubectl delete svc frontend-service -n nvidia-retail-ai

# Delete namespace (deletes everything)
kubectl delete namespace nvidia-retail-ai
```

## Cluster Info

| Property | Value |
|----------|-------|
| Cluster Name | fabulous-alternative-potato |
| Region | us-east-1 |
| Account ID | 661642944881 |
| API Endpoint | https://10CC7E71CBCA51BED4FCA00D0AA8F52B.gr7.us-east-1.eks.amazonaws.com |
| Namespace | nvidia-retail-ai |

## ECR Repositories

- `661642944881.dkr.ecr.us-east-1.amazonaws.com/nvidia-retail-frontend:latest`
- `661642944881.dkr.ecr.us-east-1.amazonaws.com/nvidia-retail-agent:latest`

## Useful kubectl Commands

```bash
# Get everything in namespace
kubectl get all -n nvidia-retail-ai

# Wide output with more details
kubectl get pods -n nvidia-retail-ai -o wide

# JSON output
kubectl get pod <pod-name> -n nvidia-retail-ai -o json

# YAML output
kubectl get svc frontend-service -n nvidia-retail-ai -o yaml

# Watch for changes
kubectl get pods -n nvidia-retail-ai --watch

# Delete stuck pods
kubectl delete pod <pod-name> -n nvidia-retail-ai --force --grace-period=0

# Copy files to/from pod
kubectl cp local-file.txt nvidia-retail-ai/<pod-name>:/path/in/pod
kubectl cp nvidia-retail-ai/<pod-name>:/path/in/pod local-file.txt
```

## Common Issues

### ImagePullBackOff
```bash
# Check image name in deployment
kubectl describe pod <pod-name> -n nvidia-retail-ai

# Verify ECR authentication
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 661642944881.dkr.ecr.us-east-1.amazonaws.com

# Check if image exists
aws ecr describe-images --repository-name nvidia-retail-agent --region us-east-1
```

### CrashLoopBackOff
```bash
# Check logs
kubectl logs <pod-name> -n nvidia-retail-ai

# Check previous logs
kubectl logs <pod-name> -n nvidia-retail-ai --previous

# Describe pod to see restart count
kubectl describe pod <pod-name> -n nvidia-retail-ai
```

### Pending Pods
```bash
# Check events
kubectl describe pod <pod-name> -n nvidia-retail-ai

# Check node resources
kubectl top nodes

# Check PVC status
kubectl get pvc -n nvidia-retail-ai
```

## AWS CLI Commands

```bash
# Get cluster info
aws eks describe-cluster --name fabulous-alternative-potato --region us-east-1

# List node groups
aws eks list-nodegroups --cluster-name fabulous-alternative-potato --region us-east-1

# Describe node group
aws eks describe-nodegroup --cluster-name fabulous-alternative-potato --nodegroup-name <name> --region us-east-1

# List addons
aws eks list-addons --cluster-name fabulous-alternative-potato --region us-east-1

# Get caller identity
aws sts get-caller-identity
```

## Documentation

- Full Guide: `k8s/README.md`
- Cluster Info: `k8s/CLUSTER-INFO.md`
- Checklist: `k8s/DEPLOYMENT-CHECKLIST.md`
- Summary: `DEPLOYMENT-SUMMARY.md`
