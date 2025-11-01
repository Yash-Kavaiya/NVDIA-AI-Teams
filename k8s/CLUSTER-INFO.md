# EKS Cluster Information

## Cluster Details

**Cluster Name**: `fabulous-alternative-potato`

**Region**: `us-east-1`

**AWS Account ID**: `661642944881`

**Created**: November 1, 2025 (35 minutes ago from initial setup)

**Platform Version**: `eks.20`

## Endpoints

**API Server Endpoint**:
```
https://10CC7E71CBCA51BED4FCA00D0AA8F52B.gr7.us-east-1.eks.amazonaws.com
```

**OpenID Connect Provider URL**:
```
https://oidc.eks.us-east-1.amazonaws.com/id/10CC7E71CBCA51BED4FCA00D0AA8F52B
```

## IAM Configuration

**Cluster IAM Role ARN**:
```
arn:aws:iam::661642944881:role/AmazonEKSAutoClusterRole
```

**Cluster ARN**:
```
arn:aws:eks:us-east-1:661642944881:cluster/fabulous-alternative-potato
```

## Certificate Authority

The cluster's certificate authority data is stored in `cluster-info.yaml`.

## Quick Access

### Option 1: Using AWS CLI to Update Kubeconfig

This is the recommended method as it automatically handles authentication:

```bash
aws eks update-kubeconfig \
  --name fabulous-alternative-potato \
  --region us-east-1
```

### Option 2: Using the Provided Kubeconfig

If you prefer to use the kubeconfig file directly:

```bash
export KUBECONFIG=/home/user/NVDIA-Retail-AI-Teams/k8s/cluster-info.yaml
kubectl get nodes
```

### Option 3: Merge with Existing Kubeconfig

```bash
KUBECONFIG=~/.kube/config:/home/user/NVDIA-Retail-AI-Teams/k8s/cluster-info.yaml \
kubectl config view --flatten > ~/.kube/config.new

mv ~/.kube/config.new ~/.kube/config
kubectl config use-context fabulous-alternative-potato
```

## Verify Connection

After configuring kubectl, verify the connection:

```bash
kubectl cluster-info
kubectl get nodes
kubectl get namespaces
```

Expected output should show:
- Kubernetes control plane running at the API endpoint above
- One or more worker nodes in Ready state
- Default namespaces including kube-system, default, etc.

## Network Configuration

The cluster is configured with:
- VPC with public and private subnets
- Security groups for cluster and node communication
- IAM roles for service accounts (IRSA) support via OIDC provider

## Authentication

The cluster uses AWS IAM for authentication. When you run kubectl commands, the AWS CLI (`aws eks get-token`) is called to obtain a time-limited authentication token.

**Requirements**:
- AWS CLI must be installed and configured
- Your AWS credentials must have appropriate EKS permissions
- Credentials must not be expired (especially important for session-based credentials)

## Common Operations

### Check Cluster Status

```bash
aws eks describe-cluster \
  --name fabulous-alternative-potato \
  --region us-east-1
```

### Update Kubernetes Version (when needed)

```bash
aws eks update-cluster-version \
  --name fabulous-alternative-potato \
  --kubernetes-version 1.31 \
  --region us-east-1
```

### List Node Groups

```bash
aws eks list-nodegroups \
  --cluster-name fabulous-alternative-potato \
  --region us-east-1
```

### Get Cluster Addons

```bash
aws eks list-addons \
  --cluster-name fabulous-alternative-potato \
  --region us-east-1
```

## Troubleshooting

### "error: You must be logged in to the server (Unauthorized)"

This usually means:
1. AWS credentials are not configured
2. AWS credentials have expired (session tokens)
3. IAM user/role doesn't have EKS permissions

**Solution**:
```bash
# Refresh AWS credentials
aws sts get-caller-identity  # Verify identity
aws eks update-kubeconfig --name fabulous-alternative-potato --region us-east-1
```

### "Unable to connect to the server"

This usually means:
1. Network connectivity issues
2. API endpoint is not accessible
3. VPC/Security group configuration issues

**Solution**:
```bash
# Test connectivity
curl -k https://10CC7E71CBCA51BED4FCA00D0AA8F52B.gr7.us-east-1.eks.amazonaws.com

# Check cluster status
aws eks describe-cluster --name fabulous-alternative-potato --region us-east-1
```

### "aws: command not found" when using kubectl

This means AWS CLI is not installed or not in PATH.

**Solution**:
```bash
# Install AWS CLI
pip install awscli --user
# OR
# Download from https://aws.amazon.com/cli/
```

## Security Best Practices

1. **Use IAM Roles**: Instead of long-term access keys, use IAM roles with temporary credentials
2. **Enable Audit Logging**: Configure CloudWatch logging for the EKS cluster
3. **Network Policies**: Implement Kubernetes network policies to restrict pod-to-pod communication
4. **Pod Security Standards**: Enable and enforce pod security standards
5. **Secrets Encryption**: Enable encryption of secrets at rest using AWS KMS
6. **Regular Updates**: Keep the cluster and worker nodes updated with latest patches

## Cost Monitoring

The cluster incurs costs for:
- EKS control plane: ~$0.10/hour
- EC2 worker nodes: Varies by instance type
- EBS volumes: ~$0.10/GB/month
- LoadBalancer: ~$0.025/hour + data transfer
- Data transfer: Varies

**Estimate**: The deployment with 2-3 small instances will cost approximately $100-200/month.

## Next Steps

1. Deploy the NVIDIA Retail AI application using the scripts in `k8s/scripts/`
2. Configure monitoring and logging
3. Set up autoscaling for worker nodes
4. Configure backup strategy for persistent volumes
5. Set up CI/CD pipeline for automated deployments

## References

- [EKS User Guide](https://docs.aws.amazon.com/eks/latest/userguide/)
- [kubectl Cheat Sheet](https://kubernetes.io/docs/reference/kubectl/cheatsheet/)
- [AWS EKS Best Practices](https://aws.github.io/aws-eks-best-practices/)
