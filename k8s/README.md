# NVIDIA Retail AI - EKS Deployment Guide

This directory contains all the necessary files to deploy the NVIDIA Retail AI system to Amazon EKS (Elastic Kubernetes Service).

## 📋 Prerequisites

Before deploying, ensure you have the following installed:

- **AWS CLI** (v2 or later) - [Installation Guide](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html)
- **kubectl** (v1.28 or later) - [Installation Guide](https://kubernetes.io/docs/tasks/tools/)
- **Docker** (v20 or later) - [Installation Guide](https://docs.docker.com/get-docker/)

## 🏗️ Architecture Overview

The deployment consists of the following components:

1. **Qdrant Vector Database** - Stores image and document embeddings
2. **Python Agent Backend** - Multi-agent system with product search, inventory, and review analysis
3. **Next.js Frontend** - User interface for interacting with AI agents
4. **Persistent Storage** - AWS EBS volumes for data persistence

### Service Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    AWS EKS Cluster                       │
│                                                          │
│  ┌──────────────┐      ┌──────────────┐                │
│  │   Frontend   │◄─────┤ Load Balancer│◄─── Internet   │
│  │  (Next.js)   │      └──────────────┘                │
│  └───────┬──────┘                                       │
│          │                                               │
│          ▼                                               │
│  ┌──────────────┐      ┌──────────────┐                │
│  │    Agent     │◄────►│   Qdrant     │                │
│  │  (FastAPI)   │      │  (Vector DB) │                │
│  └──────┬───────┘      └──────┬───────┘                │
│         │                     │                          │
│         ▼                     ▼                          │
│  ┌──────────────┐      ┌──────────────┐                │
│  │ Agent Data   │      │ Qdrant Data  │                │
│  │    (EBS)     │      │    (EBS)     │                │
│  └──────────────┘      └──────────────┘                │
└─────────────────────────────────────────────────────────┘
```

## 📁 Directory Structure

```
k8s/
├── manifests/          # Kubernetes manifests
│   ├── 00-namespace.yaml
│   ├── 01-configmap.yaml
│   ├── 02-secrets.yaml
│   ├── 03-pvc.yaml
│   ├── 04-qdrant.yaml
│   ├── 05-agent.yaml
│   ├── 06-frontend.yaml
│   └── 07-ingress.yaml
├── scripts/            # Deployment scripts
│   ├── 01-setup-aws.sh
│   ├── 02-build-and-push.sh
│   ├── 03-deploy.sh
│   ├── 04-copy-data.sh
│   ├── 05-status.sh
│   └── 99-cleanup.sh
└── README.md          # This file
```

## 🚀 Quick Start Deployment

### Step 1: Configure AWS and kubectl

```bash
cd k8s/scripts
./01-setup-aws.sh
```

This script will:
- Set up AWS credentials
- Configure kubectl to connect to your EKS cluster
- Verify the connection

### Step 2: Update Secrets

**IMPORTANT:** Before deploying, update the API keys in `k8s/manifests/02-secrets.yaml`:

```yaml
stringData:
  NVIDIA_API_KEY: "your-actual-nvidia-api-key"
  GOOGLE_API_KEY: "your-actual-google-api-key"
```

Or create the secret using kubectl:

```bash
kubectl create secret generic nvidia-retail-secrets \
  --from-literal=NVIDIA_API_KEY=your-nvidia-api-key \
  --from-literal=GOOGLE_API_KEY=your-google-api-key \
  -n nvidia-retail-ai
```

### Step 3: Build and Push Docker Images

```bash
./02-build-and-push.sh
```

This script will:
- Authenticate to Amazon ECR
- Create ECR repositories (if they don't exist)
- Build Docker images for frontend and agent
- Push images to ECR

**Note:** This requires Docker to be running on your machine.

### Step 4: Deploy to EKS

```bash
./03-deploy.sh
```

This script will:
- Create the namespace
- Apply all Kubernetes manifests
- Wait for services to be ready
- Display deployment status

### Step 5: Copy Data to Persistent Volumes

```bash
./04-copy-data.sh
```

This script copies the inventory data to the agent's persistent volume.

### Step 6: Check Deployment Status

```bash
./05-status.sh
```

This script displays:
- Pod status
- Service endpoints
- Frontend URL
- Recent logs

## 🔍 Verifying the Deployment

### Check Pod Status

```bash
kubectl get pods -n nvidia-retail-ai
```

All pods should be in `Running` state:
```
NAME                        READY   STATUS    RESTARTS   AGE
agent-xxxxxxxxx-xxxxx       1/1     Running   0          5m
frontend-xxxxxxxxx-xxxxx    1/1     Running   0          5m
qdrant-xxxxxxxxx-xxxxx      1/1     Running   0          5m
```

### Get Frontend URL

```bash
kubectl get svc frontend-service -n nvidia-retail-ai
```

The `EXTERNAL-IP` column will show your Load Balancer URL. It may take a few minutes to provision.

### Access the Application

Once the LoadBalancer is ready, open your browser and navigate to:
```
http://<EXTERNAL-IP>
```

## 📊 Monitoring and Logs

### View Logs

```bash
# Agent logs
kubectl logs -f -n nvidia-retail-ai -l app=agent

# Frontend logs
kubectl logs -f -n nvidia-retail-ai -l app=frontend

# Qdrant logs
kubectl logs -f -n nvidia-retail-ai -l app=qdrant
```

### Describe Pods

```bash
kubectl describe pod -n nvidia-retail-ai <pod-name>
```

### Check Resource Usage

```bash
kubectl top pods -n nvidia-retail-ai
kubectl top nodes
```

## 🔧 Troubleshooting

### Pods Not Starting

1. Check pod events:
   ```bash
   kubectl describe pod -n nvidia-retail-ai <pod-name>
   ```

2. Check logs:
   ```bash
   kubectl logs -n nvidia-retail-ai <pod-name>
   ```

3. Common issues:
   - **ImagePullBackOff**: Check ECR authentication and image names
   - **CrashLoopBackOff**: Check application logs and environment variables
   - **Pending**: Check PVC status and node resources

### LoadBalancer Not Getting External IP

```bash
# Check service status
kubectl describe svc frontend-service -n nvidia-retail-ai

# Check AWS Load Balancer Controller logs
kubectl logs -n kube-system -l app.kubernetes.io/name=aws-load-balancer-controller
```

### Qdrant Connection Issues

```bash
# Check if Qdrant is running
kubectl exec -it -n nvidia-retail-ai <agent-pod> -- curl http://qdrant:6333

# Check Qdrant logs
kubectl logs -n nvidia-retail-ai -l app=qdrant
```

## 🔄 Updating the Deployment

### Update Docker Images

```bash
# Build and push new images
cd k8s/scripts
./02-build-and-push.sh

# Restart deployments to use new images
kubectl rollout restart deployment agent -n nvidia-retail-ai
kubectl rollout restart deployment frontend -n nvidia-retail-ai
```

### Update Configuration

```bash
# Edit ConfigMap
kubectl edit configmap nvidia-retail-config -n nvidia-retail-ai

# Restart pods to pick up changes
kubectl rollout restart deployment agent -n nvidia-retail-ai
kubectl rollout restart deployment frontend -n nvidia-retail-ai
```

### Update Secrets

```bash
# Update secrets
kubectl delete secret nvidia-retail-secrets -n nvidia-retail-ai
kubectl create secret generic nvidia-retail-secrets \
  --from-literal=NVIDIA_API_KEY=new-key \
  --from-literal=GOOGLE_API_KEY=new-key \
  -n nvidia-retail-ai

# Restart pods
kubectl rollout restart deployment agent -n nvidia-retail-ai
```

## 🧹 Cleanup

To remove all deployed resources:

```bash
cd k8s/scripts
./99-cleanup.sh
```

**WARNING:** This will delete all resources including persistent volumes and data!

## 📝 Configuration Details

### Resource Limits

| Service  | CPU Request | CPU Limit | Memory Request | Memory Limit |
|----------|-------------|-----------|----------------|--------------|
| Frontend | 100m        | 250m      | 256Mi          | 512Mi        |
| Agent    | 250m        | 500m      | 512Mi          | 1Gi          |
| Qdrant   | 500m        | 1000m     | 1Gi            | 2Gi          |

### Storage

| PVC          | Size | Storage Class |
|--------------|------|---------------|
| qdrant-storage | 10Gi | gp2           |
| agent-data   | 5Gi  | gp2           |

### Replicas

- **Frontend**: 2 replicas (for high availability)
- **Agent**: 2 replicas (for load balancing)
- **Qdrant**: 1 replica (stateful)

## 🔐 Security Best Practices

1. **Never commit secrets to Git** - Use AWS Secrets Manager or Kubernetes Secrets
2. **Use RBAC** - Limit access to the namespace
3. **Enable network policies** - Restrict pod-to-pod communication
4. **Use HTTPS** - Configure TLS certificates for the LoadBalancer
5. **Regular updates** - Keep Docker images and dependencies updated

## 📚 Additional Resources

- [EKS User Guide](https://docs.aws.amazon.com/eks/latest/userguide/)
- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [AWS Load Balancer Controller](https://docs.aws.amazon.com/eks/latest/userguide/aws-load-balancer-controller.html)
- [Qdrant Documentation](https://qdrant.tech/documentation/)

## 🆘 Support

For issues or questions:
1. Check the troubleshooting section above
2. Review pod logs using `kubectl logs`
3. Check AWS EKS console for cluster-level issues
4. Review application-specific logs in CloudWatch (if configured)

## 🎯 Next Steps

After deployment:
1. Set up monitoring with CloudWatch or Prometheus
2. Configure autoscaling for frontend and agent
3. Set up CI/CD pipeline for automated deployments
4. Configure backup strategy for Qdrant data
5. Set up custom domain and SSL certificate
