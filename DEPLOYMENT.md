# NVIDIA Retail AI - EKS Deployment

This document provides an overview of the EKS deployment setup for the NVIDIA Retail AI solution.

## Quick Links

- **[Quick Start Guide](k8s/QUICK_START.md)** - Get started in 30 minutes
- **[Complete Documentation](k8s/README.md)** - Full deployment guide with troubleshooting
- **[Deployment Summary](k8s/DEPLOYMENT_SUMMARY.md)** - Architecture and costs overview

## What's Included

This repository contains everything needed to deploy the NVIDIA Retail AI solution to Amazon EKS:

### 📦 Docker Images
- Next.js UI Frontend
- Python FastAPI Agent Backend
- Configured for production with security best practices

### ☸️ Kubernetes Resources
- Complete manifests for all components
- High-availability configuration (2+ replicas)
- Persistent storage for Qdrant vector database
- Auto-scaling ready

### 🔧 Deployment Scripts
- `create-eks-cluster.sh` - One-command cluster creation
- `deploy.sh` / `deploy.bat` - Cross-platform deployment
- `cleanup.sh` - Safe cleanup with prompts

### 📚 Documentation
- Step-by-step deployment guides
- Troubleshooting documentation
- Cost breakdown and optimization tips
- Security best practices

## Architecture

```
Internet → ALB Ingress → UI Frontend (Next.js)
                              ↓
                        Agent Backend (FastAPI)
                              ↓
                        Qdrant Vector DB → NVIDIA APIs
```

**Components:**
- **UI Frontend**: 2 replicas, port 3000
- **Agent Backend**: 2 replicas, port 8000
- **Qdrant DB**: 1 replica with 20GB persistent storage

## Prerequisites

1. **AWS CLI** - Configured with credentials
2. **kubectl** - Kubernetes CLI
3. **eksctl** - EKS cluster management
4. **Docker** - Container runtime
5. **API Keys**:
   - Google API key (for ADK agents)
   - NVIDIA API key (from https://build.nvidia.com/)

## Quick Start

### Linux/Mac/WSL

```bash
# 1. Create EKS cluster (15-20 min)
cd k8s
./create-eks-cluster.sh

# 2. Configure secrets
kubectl create namespace nvidia-retail-ai
kubectl create secret generic api-keys \
  --from-literal=google-api-key=YOUR_KEY \
  --from-literal=nvidia-api-key=YOUR_KEY \
  -n nvidia-retail-ai

# 3. Deploy application (10-15 min)
./deploy.sh

# 4. Get URL
kubectl get ingress -n nvidia-retail-ai
```

### Windows

```cmd
REM 1. Create EKS cluster using WSL or Git Bash
bash create-eks-cluster.sh

REM 2. Configure secrets
kubectl create namespace nvidia-retail-ai
kubectl create secret generic api-keys --from-literal=google-api-key=YOUR_KEY --from-literal=nvidia-api-key=YOUR_KEY -n nvidia-retail-ai

REM 3. Deploy application
deploy.bat

REM 4. Get URL
kubectl get ingress -n nvidia-retail-ai
```

## Files Structure

```
NVDIA-Retail-AI-Teams/
├── DEPLOYMENT.md                    # This file
├── .dockerignore
├── nvdia-ag-ui/
│   ├── Dockerfile                   # UI frontend image
│   ├── next.config.js               # Next.js config
│   └── agent/
│       └── Dockerfile               # Agent backend image
└── k8s/
    ├── README.md                    # Complete guide
    ├── QUICK_START.md               # 30-min guide
    ├── DEPLOYMENT_SUMMARY.md        # Architecture overview
    ├── create-eks-cluster.sh        # Cluster setup
    ├── deploy.sh                    # Linux/Mac deployment
    ├── deploy.bat                   # Windows deployment
    ├── cleanup.sh                   # Cleanup script
    ├── iam-policy.json              # IAM permissions
    ├── base/                        # K8s manifests
    │   ├── namespace.yaml
    │   ├── configmap.yaml
    │   ├── secrets-template.yaml
    │   ├── qdrant-deployment.yaml
    │   ├── agent-deployment.yaml
    │   └── ui-deployment.yaml
    └── monitoring/
        └── cloudwatch-insights.yaml # Monitoring setup
```

## Cost Estimate

Running 24/7 in `us-east-1`:

| Component | Cost/Month |
|-----------|------------|
| EKS Control Plane | $73 |
| 3x t3.xlarge nodes | $220 |
| Application Load Balancer | $20 |
| EBS Storage (20GB) | $2 |
| **Total** | **~$315** |

*Plus NVIDIA API usage and data transfer costs*

### Cost Optimization

- **50% savings**: Auto-scale to 0 during off-hours
- **70% savings**: Use Spot instances for nodes
- **30% savings**: Scale down to 2 nodes minimum

## Security Checklist

Before deploying to production:

- [ ] **Rotate AWS credentials** if exposed
- [ ] Use AWS Secrets Manager for API keys
- [ ] Request ACM certificate for HTTPS
- [ ] Enable Pod Security Standards
- [ ] Configure Network Policies
- [ ] Enable EKS audit logging
- [ ] Set up CloudWatch alarms
- [ ] Configure budget alerts
- [ ] Review IAM permissions (principle of least privilege)
- [ ] Enable encryption for EBS volumes

## Common Commands

```bash
# View all resources
kubectl get all -n nvidia-retail-ai

# Check logs
kubectl logs -f deployment/agent-backend -n nvidia-retail-ai
kubectl logs -f deployment/ui-frontend -n nvidia-retail-ai

# Port forward for debugging
kubectl port-forward svc/qdrant 6333:6333 -n nvidia-retail-ai

# Scale deployment
kubectl scale deployment agent-backend --replicas=4 -n nvidia-retail-ai

# Update image
kubectl set image deployment/agent-backend \
  agent-backend=YOUR_ECR/agent-backend:v2 \
  -n nvidia-retail-ai

# Delete everything
kubectl delete namespace nvidia-retail-ai
```

## Monitoring

### CloudWatch Container Insights

```bash
# Install monitoring
kubectl apply -f k8s/monitoring/cloudwatch-insights.yaml

# View in AWS Console
# CloudWatch → Container Insights → Performance monitoring
```

### View Metrics

```bash
# Pod CPU/Memory
kubectl top pods -n nvidia-retail-ai

# Node resources
kubectl top nodes
```

## Troubleshooting

### Pods not starting

```bash
kubectl describe pod POD_NAME -n nvidia-retail-ai
kubectl logs POD_NAME -n nvidia-retail-ai
```

**Common causes:**
- Missing secrets
- Image pull errors
- Insufficient resources

### Cannot access application

```bash
# Check ingress
kubectl describe ingress nvidia-retail-ai-ingress -n nvidia-retail-ai

# Check ALB controller
kubectl logs -n kube-system deployment/aws-load-balancer-controller
```

### Qdrant issues

```bash
# Check PVC
kubectl get pvc -n nvidia-retail-ai

# Check Qdrant logs
kubectl logs deployment/qdrant -n nvidia-retail-ai
```

See [k8s/README.md#troubleshooting](k8s/README.md#troubleshooting) for detailed solutions.

## Next Steps After Deployment

1. **Configure DNS**: Point your domain to ALB
2. **Add SSL/TLS**: Use ACM certificate
3. **Set up monitoring**: CloudWatch Container Insights
4. **Configure backups**: Qdrant data backup strategy
5. **Implement CI/CD**: GitHub Actions or CodePipeline
6. **Load testing**: Verify performance at scale
7. **Documentation**: Create runbooks for operations

## Support Resources

- **AWS EKS**: https://docs.aws.amazon.com/eks/
- **Kubernetes**: https://kubernetes.io/docs/
- **NVIDIA NIM**: https://build.nvidia.com/
- **Qdrant**: https://qdrant.tech/documentation/

## Getting Help

1. Check the logs: `kubectl logs -f deployment/NAME -n nvidia-retail-ai`
2. Review events: `kubectl get events -n nvidia-retail-ai`
3. See [k8s/README.md](k8s/README.md) for detailed troubleshooting
4. Check pod status: `kubectl describe pod POD_NAME -n nvidia-retail-ai`

## Cleanup

To remove all resources:

```bash
cd k8s
./cleanup.sh
```

This will safely remove:
- Kubernetes namespace and all resources
- ECR repositories (optional)
- EKS cluster (optional)
- IAM policies (optional)

---

## Important Security Notice

**If you exposed AWS credentials earlier, IMMEDIATELY:**

1. Go to AWS Console → IAM → Security Credentials
2. Delete the exposed access key
3. Generate new credentials
4. Update `~/.aws/credentials`

**Never commit secrets to Git:**
- Use AWS Secrets Manager
- Use External Secrets Operator
- Use `kubectl create secret` for development

---

**Ready to deploy?** → Start with [k8s/QUICK_START.md](k8s/QUICK_START.md)

**Need more details?** → See [k8s/README.md](k8s/README.md)

**Questions about architecture?** → Check [k8s/DEPLOYMENT_SUMMARY.md](k8s/DEPLOYMENT_SUMMARY.md)
