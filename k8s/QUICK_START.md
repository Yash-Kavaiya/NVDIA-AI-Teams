# Quick Start Guide - NVIDIA Retail AI on EKS

This guide will get you up and running in 30 minutes.

## Prerequisites Checklist

- [ ] AWS CLI installed and configured
- [ ] kubectl installed
- [ ] eksctl installed
- [ ] Docker installed and running
- [ ] Google API key obtained
- [ ] NVIDIA API key obtained from https://build.nvidia.com/
- [ ] **AWS credentials rotated** (if you exposed them earlier!)

## Step-by-Step Deployment

### 1. Clone Repository

```bash
cd c:\Users\yashk\Downloads\NVDIA-Retail-AI-Teams
```

### 2. Create EKS Cluster (15-20 min)

```bash
cd k8s
chmod +x create-eks-cluster.sh
./create-eks-cluster.sh
```

**What this does:**
- Creates EKS cluster with 3 t3.xlarge nodes
- Installs AWS Load Balancer Controller
- Installs EBS CSI Driver
- Configures OIDC provider

### 3. Configure Secrets

**IMPORTANT: Replace with your actual API keys**

```bash
# Create namespace
kubectl create namespace nvidia-retail-ai

# Create secrets
kubectl create secret generic api-keys \
  --from-literal=google-api-key=YOUR_GOOGLE_API_KEY_HERE \
  --from-literal=nvidia-api-key=YOUR_NVIDIA_API_KEY_HERE \
  -n nvidia-retail-ai

# Verify secrets created
kubectl get secrets -n nvidia-retail-ai
```

### 4. Deploy Application (10-15 min)

```bash
chmod +x deploy.sh
./deploy.sh
```

**What this does:**
- Creates ECR repositories
- Builds Docker images
- Pushes to ECR
- Deploys Kubernetes resources
- Waits for pods to be ready

### 5. Access Your Application

```bash
# Get load balancer URL
kubectl get ingress -n nvidia-retail-ai

# Wait for ADDRESS to be populated (may take 2-3 minutes)
export LB_URL=$(kubectl get ingress nvidia-retail-ai-ingress -n nvidia-retail-ai -o jsonpath='{.status.loadBalancer.ingress[0].hostname}')

echo "Access your application at: http://${LB_URL}"
```

## Verify Deployment

```bash
# Check all pods are running
kubectl get pods -n nvidia-retail-ai

# Expected output:
# NAME                             READY   STATUS    RESTARTS   AGE
# agent-backend-xxxxxxxxxx-xxxxx   1/1     Running   0          5m
# agent-backend-xxxxxxxxxx-xxxxx   1/1     Running   0          5m
# qdrant-xxxxxxxxxx-xxxxx          1/1     Running   0          6m
# ui-frontend-xxxxxxxxxx-xxxxx     1/1     Running   0          5m
# ui-frontend-xxxxxxxxxx-xxxxx     1/1     Running   0          5m

# Check services
kubectl get svc -n nvidia-retail-ai

# Check ingress
kubectl get ingress -n nvidia-retail-ai
```

## Common Issues

### Pods stuck in ImagePullBackOff

```bash
# Check ECR login
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <ACCOUNT_ID>.dkr.ecr.us-east-1.amazonaws.com

# Rebuild and push images
cd k8s
./deploy.sh
```

### Pods stuck in CrashLoopBackOff

```bash
# Check logs
kubectl logs deployment/agent-backend -n nvidia-retail-ai

# Common issues:
# - Missing secrets (check step 3)
# - Cannot connect to Qdrant (wait for Qdrant to be ready)
# - Invalid API keys (check secrets)
```

### Load balancer not provisioning

```bash
# Check ALB controller logs
kubectl logs -n kube-system deployment/aws-load-balancer-controller

# Verify ALB controller is installed
kubectl get deployment -n kube-system aws-load-balancer-controller
```

## Quick Commands

```bash
# View logs
kubectl logs -f deployment/agent-backend -n nvidia-retail-ai
kubectl logs -f deployment/ui-frontend -n nvidia-retail-ai

# Port forward to access locally
kubectl port-forward svc/ui-frontend 3000:3000 -n nvidia-retail-ai
kubectl port-forward svc/qdrant 6333:6333 -n nvidia-retail-ai

# Restart deployments
kubectl rollout restart deployment/agent-backend -n nvidia-retail-ai

# Scale up/down
kubectl scale deployment agent-backend --replicas=4 -n nvidia-retail-ai

# Delete everything
kubectl delete namespace nvidia-retail-ai
```

## Next Steps

1. **Configure DNS**: Point your domain to the load balancer
2. **Add SSL**: Request ACM certificate and update Ingress
3. **Set up monitoring**: Apply CloudWatch Container Insights
4. **Configure auto-scaling**: Set up HPA based on CPU/memory
5. **Backup Qdrant**: Implement regular backup strategy

## Cleanup

When you're done:

```bash
cd k8s
chmod +x cleanup.sh
./cleanup.sh
```

This will guide you through deleting:
- Namespace and all resources
- ECR repositories
- EKS cluster
- IAM policies

---

## Estimated Costs

**Running 24/7:**
- EKS control plane: $73/month
- 3x t3.xlarge nodes: ~$220/month
- Load balancer: ~$20/month
- EBS storage: ~$2/month
- **Total: ~$315/month**

**Cost saving tips:**
- Stop cluster outside business hours: ~50% reduction
- Use Spot instances: ~70% reduction on compute
- Scale down to 2 nodes: ~30% reduction

---

**Need help?** Check the full [README.md](./README.md) for detailed documentation.
