# NVIDIA Retail AI - EKS Deployment Guide

This directory contains all necessary files to deploy the NVIDIA Retail AI solution to Amazon EKS.

## Architecture Overview

The solution consists of three main components:

1. **UI Frontend** - Next.js 15 application with CopilotKit (Port 3000)
2. **Agent Backend** - Python FastAPI + Google ADK agents (Port 8000)
3. **Qdrant Vector Database** - Vector storage for embeddings (Ports 6333/6334)

```
┌─────────────────┐
│   Internet      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  ALB (Ingress)  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  UI Frontend    │────▶│  Agent Backend   │────▶│     Qdrant      │
│   (Next.js)     │     │    (FastAPI)     │     │  (Vector DB)    │
└─────────────────┘     └──────────────────┘     └─────────────────┘
                               │
                               ▼
                        ┌──────────────────┐
                        │  NVIDIA APIs     │
                        │  (Embeddings)    │
                        └──────────────────┘
```

## Prerequisites

### Required Tools

1. **AWS CLI** (v2.x or higher)
   ```bash
   aws --version
   ```

2. **kubectl** (v1.28 or higher)
   ```bash
   kubectl version --client
   ```

3. **eksctl** (v0.150 or higher)
   ```bash
   eksctl version
   ```

4. **Docker** (v20.x or higher)
   ```bash
   docker --version
   ```

5. **Helm** (v3.x or higher) - Optional but recommended
   ```bash
   helm version
   ```

### AWS Account Setup

1. **Configure AWS credentials** (DO NOT share these publicly)
   ```bash
   aws configure
   ```

2. **Verify AWS access**
   ```bash
   aws sts get-caller-identity
   ```

3. **Required IAM permissions:**
   - EKS cluster creation
   - ECR repository management
   - IAM role/policy creation
   - VPC and networking
   - Load Balancer management

### API Keys Required

- **Google API Key** - For Google ADK agents
- **NVIDIA API Key** - For NVIDIA NIM embeddings
- Get NVIDIA API key from: https://build.nvidia.com/

## Deployment Steps

### Step 1: Create EKS Cluster

```bash
cd k8s
chmod +x create-eks-cluster.sh
./create-eks-cluster.sh
```

This script will:
- Create an EKS cluster with managed node groups
- Install AWS Load Balancer Controller
- Install EBS CSI Driver for persistent volumes
- Configure OIDC provider for IAM roles

**Estimated time: 15-20 minutes**

### Step 2: Configure Secrets

**IMPORTANT: Never commit secrets to Git**

#### Option A: Using kubectl (Quick setup)

```bash
kubectl create namespace nvidia-retail-ai

kubectl create secret generic api-keys \
  --from-literal=google-api-key=YOUR_GOOGLE_API_KEY \
  --from-literal=nvidia-api-key=YOUR_NVIDIA_API_KEY \
  -n nvidia-retail-ai
```

#### Option B: Using AWS Secrets Manager (Production recommended)

1. Store secrets in AWS Secrets Manager:
   ```bash
   aws secretsmanager create-secret \
     --name nvidia-retail-ai/google-api-key \
     --secret-string "YOUR_GOOGLE_API_KEY"

   aws secretsmanager create-secret \
     --name nvidia-retail-ai/nvidia-api-key \
     --secret-string "YOUR_NVIDIA_API_KEY"
   ```

2. Install External Secrets Operator:
   ```bash
   helm repo add external-secrets https://charts.external-secrets.io
   helm install external-secrets \
     external-secrets/external-secrets \
     -n external-secrets-system \
     --create-namespace
   ```

3. Uncomment the External Secrets section in `base/secrets-template.yaml`

### Step 3: Deploy Application

```bash
chmod +x deploy.sh
./deploy.sh
```

This script will:
- Create ECR repositories
- Build Docker images for UI and Agent
- Push images to ECR
- Create IAM roles for service accounts
- Deploy all Kubernetes resources
- Wait for pods to be ready

**Estimated time: 10-15 minutes**

### Step 4: Verify Deployment

```bash
# Check all resources
kubectl get all -n nvidia-retail-ai

# Check pod status
kubectl get pods -n nvidia-retail-ai

# Check ingress
kubectl get ingress -n nvidia-retail-ai

# Get load balancer URL
kubectl get ingress nvidia-retail-ai-ingress -n nvidia-retail-ai -o jsonpath='{.status.loadBalancer.ingress[0].hostname}'
```

### Step 5: Access Application

1. Get the ALB DNS name:
   ```bash
   export LB_URL=$(kubectl get ingress nvidia-retail-ai-ingress -n nvidia-retail-ai -o jsonpath='{.status.loadBalancer.ingress[0].hostname}')
   echo "Application URL: http://${LB_URL}"
   ```

2. (Optional) Configure DNS:
   - Create a CNAME record pointing to the ALB DNS
   - Update the Ingress host in `base/ui-deployment.yaml`

3. (Optional) Configure SSL/TLS:
   - Request ACM certificate
   - Update `<ACM_CERTIFICATE_ARN>` in `base/ui-deployment.yaml`

## Files Structure

```
k8s/
├── README.md                      # This file
├── create-eks-cluster.sh          # EKS cluster creation script
├── deploy.sh                      # Application deployment script
├── iam-policy.json                # IAM policy for service accounts
├── base/                          # Kubernetes manifests
│   ├── namespace.yaml             # Namespace definition
│   ├── configmap.yaml             # Application configuration
│   ├── secrets-template.yaml      # Secrets template (DO NOT COMMIT REAL SECRETS)
│   ├── qdrant-deployment.yaml     # Qdrant vector database
│   ├── agent-deployment.yaml      # Agent backend service
│   └── ui-deployment.yaml         # UI frontend + Ingress
└── deploy/                        # Generated (gitignored)
```

## Configuration

### Environment Variables

All configuration is managed through ConfigMaps and Secrets:

**ConfigMap (base/configmap.yaml):**
- `QDRANT_URL`: Qdrant service URL
- `NVIDIA_EMBEDDING_URL`: NVIDIA API endpoint
- `EMBEDDING_DIM`: Vector dimensions (4096)

**Secrets (base/secrets-template.yaml):**
- `google-api-key`: Google AI API key
- `nvidia-api-key`: NVIDIA NIM API key

### Resource Limits

**Agent Backend:**
- Requests: 1Gi RAM, 500m CPU
- Limits: 2Gi RAM, 1000m CPU
- Replicas: 2

**UI Frontend:**
- Requests: 512Mi RAM, 250m CPU
- Limits: 1Gi RAM, 500m CPU
- Replicas: 2

**Qdrant:**
- Requests: 2Gi RAM, 1000m CPU
- Limits: 4Gi RAM, 2000m CPU
- Storage: 20Gi (EBS gp3)

### Scaling

#### Manual Scaling

```bash
# Scale agent backend
kubectl scale deployment agent-backend -n nvidia-retail-ai --replicas=4

# Scale UI frontend
kubectl scale deployment ui-frontend -n nvidia-retail-ai --replicas=3
```

#### Auto-scaling (HPA)

Create HPA for agent backend:

```bash
kubectl autoscale deployment agent-backend \
  -n nvidia-retail-ai \
  --cpu-percent=70 \
  --min=2 \
  --max=10
```

## Monitoring and Logging

### View Logs

```bash
# Agent backend logs
kubectl logs -f deployment/agent-backend -n nvidia-retail-ai

# UI frontend logs
kubectl logs -f deployment/ui-frontend -n nvidia-retail-ai

# Qdrant logs
kubectl logs -f deployment/qdrant -n nvidia-retail-ai

# All logs
kubectl logs -f -l app=agent-backend -n nvidia-retail-ai --all-containers
```

### Port Forwarding

Access services locally for debugging:

```bash
# Qdrant dashboard
kubectl port-forward svc/qdrant 6333:6333 -n nvidia-retail-ai
# Access at: http://localhost:6333/dashboard

# Agent backend
kubectl port-forward svc/agent-backend 8000:8000 -n nvidia-retail-ai

# UI frontend
kubectl port-forward svc/ui-frontend 3000:3000 -n nvidia-retail-ai
```

### Health Checks

```bash
# Check pod health
kubectl describe pod -l app=agent-backend -n nvidia-retail-ai

# Check events
kubectl get events -n nvidia-retail-ai --sort-by='.lastTimestamp'
```

## Troubleshooting

### Common Issues

#### 1. Pods not starting

```bash
# Check pod status
kubectl get pods -n nvidia-retail-ai

# Describe pod
kubectl describe pod <pod-name> -n nvidia-retail-ai

# Check logs
kubectl logs <pod-name> -n nvidia-retail-ai
```

**Common causes:**
- Missing secrets (api-keys)
- Image pull errors (check ECR permissions)
- Resource constraints (check node capacity)

#### 2. Qdrant storage issues

```bash
# Check PVC status
kubectl get pvc -n nvidia-retail-ai

# Describe PVC
kubectl describe pvc qdrant-storage-pvc -n nvidia-retail-ai
```

**Solution:** Ensure EBS CSI driver is installed

#### 3. Load balancer not provisioning

```bash
# Check ingress status
kubectl describe ingress nvidia-retail-ai-ingress -n nvidia-retail-ai

# Check ALB controller logs
kubectl logs -n kube-system deployment/aws-load-balancer-controller
```

**Common causes:**
- ALB controller not installed
- Incorrect subnet tags
- Security group issues

#### 4. Agent backend crashes

```bash
# Check logs for errors
kubectl logs deployment/agent-backend -n nvidia-retail-ai --tail=100

# Common issues:
# - Missing environment variables
# - Cannot connect to Qdrant
# - Invalid API keys
```

### Rolling Back

```bash
# Check deployment history
kubectl rollout history deployment/agent-backend -n nvidia-retail-ai

# Rollback to previous version
kubectl rollout undo deployment/agent-backend -n nvidia-retail-ai
```

## Data Management

### Backup Qdrant Data

```bash
# Create snapshot (exec into pod)
kubectl exec -it deployment/qdrant -n nvidia-retail-ai -- \
  curl -X POST 'http://localhost:6333/collections/image_embeddings/snapshots'

# Download snapshot
kubectl cp nvidia-retail-ai/qdrant-pod:/qdrant/storage/snapshots ./backups/
```

### Restore Qdrant Data

```bash
# Upload snapshot to new cluster
kubectl cp ./backups/snapshot.tar.gz nvidia-retail-ai/qdrant-pod:/qdrant/storage/snapshots/

# Restore via API
kubectl exec -it deployment/qdrant -n nvidia-retail-ai -- \
  curl -X PUT 'http://localhost:6333/collections/image_embeddings/snapshots/upload' \
  --data-binary @/qdrant/storage/snapshots/snapshot.tar.gz
```

## Updating the Application

### Update Docker Images

```bash
# Build new images
cd ../nvdia-ag-ui
docker build -t ${ECR_REGISTRY}/nvidia-retail-ai/ui-frontend:v2 .

cd agent
docker build -t ${ECR_REGISTRY}/nvidia-retail-ai/agent-backend:v2 .

# Push to ECR
docker push ${ECR_REGISTRY}/nvidia-retail-ai/ui-frontend:v2
docker push ${ECR_REGISTRY}/nvidia-retail-ai/agent-backend:v2

# Update deployment
kubectl set image deployment/ui-frontend \
  ui-frontend=${ECR_REGISTRY}/nvidia-retail-ai/ui-frontend:v2 \
  -n nvidia-retail-ai

kubectl set image deployment/agent-backend \
  agent-backend=${ECR_REGISTRY}/nvidia-retail-ai/agent-backend:v2 \
  -n nvidia-retail-ai
```

### Update Configuration

```bash
# Edit ConfigMap
kubectl edit configmap app-config -n nvidia-retail-ai

# Restart pods to pick up changes
kubectl rollout restart deployment/agent-backend -n nvidia-retail-ai
```

## Cost Optimization

### Estimated Monthly Costs (us-east-1)

- **EKS Cluster**: $73/month (control plane)
- **EC2 Nodes**: ~$220/month (3x t3.xlarge)
- **EBS Storage**: ~$2/month (20GB gp3)
- **Load Balancer**: ~$20/month
- **Data Transfer**: Variable

**Total**: ~$315/month (excluding data transfer and NVIDIA API costs)

### Cost Reduction Tips

1. **Use Spot Instances** for non-critical workloads
2. **Enable Cluster Autoscaler** to scale down during off-hours
3. **Use Fargate** for agent backend (pay per pod)
4. **Optimize image sizes** to reduce pull time and storage

## Security Best Practices

1. **Use AWS Secrets Manager** instead of Kubernetes secrets
2. **Enable Pod Security Standards**
3. **Use Network Policies** to restrict pod communication
4. **Enable audit logging** on EKS
5. **Regularly update** container images
6. **Use IRSA** instead of storing AWS credentials
7. **Enable encryption** for EBS volumes
8. **Use private subnets** for nodes

## Cleanup

### Delete Application

```bash
kubectl delete namespace nvidia-retail-ai
```

### Delete EKS Cluster

```bash
eksctl delete cluster --name nvidia-retail-ai-cluster --region us-east-1
```

### Delete ECR Repositories

```bash
aws ecr delete-repository \
  --repository-name nvidia-retail-ai/ui-frontend \
  --region us-east-1 \
  --force

aws ecr delete-repository \
  --repository-name nvidia-retail-ai/agent-backend \
  --region us-east-1 \
  --force
```

## Support and Resources

- **EKS Documentation**: https://docs.aws.amazon.com/eks/
- **kubectl Cheat Sheet**: https://kubernetes.io/docs/reference/kubectl/cheatsheet/
- **NVIDIA NIM**: https://build.nvidia.com/
- **Qdrant Documentation**: https://qdrant.tech/documentation/

## Next Steps

1. **Set up monitoring** with CloudWatch Container Insights
2. **Configure CI/CD** with GitHub Actions or AWS CodePipeline
3. **Add SSL/TLS** certificate from ACM
4. **Set up custom domain** with Route 53
5. **Implement backup strategy** for Qdrant data
6. **Configure auto-scaling** based on metrics
7. **Set up alerts** for critical failures

---

**Questions or Issues?**
Refer to the troubleshooting section or check pod logs for detailed error messages.
