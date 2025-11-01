# EKS Deployment Checklist

Use this checklist to ensure a smooth deployment process.

## Pre-Deployment

- [ ] AWS CLI installed and configured
- [ ] kubectl installed
- [ ] Docker installed and running
- [ ] AWS credentials configured with appropriate permissions
- [ ] EKS cluster is running and accessible
- [ ] NVIDIA API key obtained
- [ ] Google API key obtained

## Cluster Configuration

- [ ] EKS cluster name: `fabulous-alternative-potato`
- [ ] Region: `us-east-1`
- [ ] AWS Account ID: `661642944881`
- [ ] kubectl configured for EKS cluster
- [ ] Can run `kubectl get nodes` successfully

## Secrets Configuration

- [ ] Updated `k8s/manifests/02-secrets.yaml` with real API keys
- [ ] Or created secret using kubectl command
- [ ] Verified secrets are not committed to Git

## Build and Push

- [ ] ECR repositories created
  - [ ] `nvidia-retail-frontend`
  - [ ] `nvidia-retail-agent`
- [ ] Docker authenticated to ECR
- [ ] Frontend Docker image built successfully
- [ ] Agent Docker image built successfully
- [ ] Frontend image pushed to ECR
- [ ] Agent image pushed to ECR

## Deployment

- [ ] Namespace created: `nvidia-retail-ai`
- [ ] ConfigMap applied
- [ ] Secrets applied
- [ ] PersistentVolumeClaims created and bound
- [ ] Qdrant deployed and running
- [ ] Agent deployed and running
- [ ] Frontend deployed and running
- [ ] All pods are in `Running` state

## Data Migration

- [ ] Inventory data copied to agent persistent volume
- [ ] Image embeddings indexed in Qdrant (if applicable)
- [ ] Document embeddings indexed in Qdrant (if applicable)

## Verification

- [ ] All pods are healthy
- [ ] Services are accessible within cluster
- [ ] LoadBalancer has external IP assigned
- [ ] Frontend accessible via browser
- [ ] Agent API responding to health checks
- [ ] Qdrant dashboard accessible (port-forward if needed)
- [ ] Test AI agents functionality:
  - [ ] Product search agent
  - [ ] Inventory agent
  - [ ] Review analysis agent

## Post-Deployment

- [ ] Monitor pod logs for errors
- [ ] Set up CloudWatch logging (optional)
- [ ] Configure autoscaling (optional)
- [ ] Set up monitoring/alerting (optional)
- [ ] Document LoadBalancer URL
- [ ] Configure custom domain (optional)
- [ ] Set up SSL/TLS certificate (optional)

## Commands Reference

### Quick Status Check
```bash
cd k8s/scripts
./05-status.sh
```

### Get Frontend URL
```bash
kubectl get svc frontend-service -n nvidia-retail-ai -o jsonpath='{.status.loadBalancer.ingress[0].hostname}'
```

### View Logs
```bash
kubectl logs -f -n nvidia-retail-ai -l app=agent
kubectl logs -f -n nvidia-retail-ai -l app=frontend
```

### Restart Deployments
```bash
kubectl rollout restart deployment agent -n nvidia-retail-ai
kubectl rollout restart deployment frontend -n nvidia-retail-ai
```

### Port Forward to Qdrant Dashboard
```bash
kubectl port-forward -n nvidia-retail-ai svc/qdrant 6333:6333
# Access at http://localhost:6333/dashboard
```

## Troubleshooting Checklist

If something goes wrong:

- [ ] Check pod status: `kubectl get pods -n nvidia-retail-ai`
- [ ] Describe problematic pod: `kubectl describe pod <pod-name> -n nvidia-retail-ai`
- [ ] Check pod logs: `kubectl logs <pod-name> -n nvidia-retail-ai`
- [ ] Verify secrets exist: `kubectl get secrets -n nvidia-retail-ai`
- [ ] Check PVC status: `kubectl get pvc -n nvidia-retail-ai`
- [ ] Verify ConfigMap: `kubectl get configmap nvidia-retail-config -n nvidia-retail-ai -o yaml`
- [ ] Check service endpoints: `kubectl get endpoints -n nvidia-retail-ai`
- [ ] Review recent events: `kubectl get events -n nvidia-retail-ai --sort-by='.lastTimestamp'`

## Rollback Plan

If deployment fails:

1. Save logs for debugging:
   ```bash
   kubectl logs -n nvidia-retail-ai -l app=agent > agent-logs.txt
   kubectl logs -n nvidia-retail-ai -l app=frontend > frontend-logs.txt
   ```

2. Run cleanup script:
   ```bash
   cd k8s/scripts
   ./99-cleanup.sh
   ```

3. Fix issues and redeploy

## Success Criteria

Deployment is successful when:

- ✅ All pods are in `Running` state
- ✅ All health checks passing
- ✅ Frontend accessible via LoadBalancer URL
- ✅ Can interact with AI agents through UI
- ✅ Product search returns results
- ✅ Inventory analysis works
- ✅ Review analysis functional
- ✅ No errors in logs

## Notes

- LoadBalancer provisioning can take 5-10 minutes
- First-time image pull may take several minutes
- PersistentVolume binding should be quick on EKS
- Session tokens expire - refresh AWS credentials if needed
