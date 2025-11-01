#!/bin/bash

# Cleanup script for NVIDIA Retail AI EKS deployment

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

CLUSTER_NAME="nvidia-retail-ai-cluster"
REGION="us-east-1"
NAMESPACE="nvidia-retail-ai"

echo -e "${RED}========================================${NC}"
echo -e "${RED}NVIDIA Retail AI - Cleanup${NC}"
echo -e "${RED}========================================${NC}"
echo ""
echo -e "${YELLOW}This will delete:${NC}"
echo "  - Kubernetes namespace and all resources"
echo "  - ECR repositories (optional)"
echo "  - EKS cluster (optional)"
echo ""
read -p "Are you sure you want to continue? (yes/no): " CONFIRM

if [ "$CONFIRM" != "yes" ]; then
    echo "Cleanup cancelled"
    exit 0
fi

# Delete namespace (this deletes all resources in the namespace)
echo -e "${YELLOW}Deleting namespace: ${NAMESPACE}${NC}"
kubectl delete namespace ${NAMESPACE} --ignore-not-found=true

echo -e "${GREEN}Namespace deleted${NC}"
echo ""

# Ask about ECR repositories
read -p "Delete ECR repositories? (yes/no): " DELETE_ECR
if [ "$DELETE_ECR" == "yes" ]; then
    echo -e "${YELLOW}Deleting ECR repositories...${NC}"

    aws ecr delete-repository \
        --repository-name nvidia-retail-ai/ui-frontend \
        --region ${REGION} \
        --force \
        2>/dev/null || echo "UI repository not found or already deleted"

    aws ecr delete-repository \
        --repository-name nvidia-retail-ai/agent-backend \
        --region ${REGION} \
        --force \
        2>/dev/null || echo "Agent repository not found or already deleted"

    echo -e "${GREEN}ECR repositories deleted${NC}"
fi

echo ""

# Ask about EKS cluster
read -p "Delete EKS cluster? This will take 10-15 minutes. (yes/no): " DELETE_CLUSTER
if [ "$DELETE_CLUSTER" == "yes" ]; then
    echo -e "${YELLOW}Deleting EKS cluster: ${CLUSTER_NAME}${NC}"
    echo "This may take 10-15 minutes..."

    eksctl delete cluster \
        --name ${CLUSTER_NAME} \
        --region ${REGION} \
        --wait

    echo -e "${GREEN}EKS cluster deleted${NC}"
fi

echo ""

# Ask about IAM resources
read -p "Delete IAM policy? (yes/no): " DELETE_IAM
if [ "$DELETE_IAM" == "yes" ]; then
    echo -e "${YELLOW}Deleting IAM policy...${NC}"

    POLICY_ARN=$(aws iam list-policies \
        --query 'Policies[?PolicyName==`nvidia-retail-ai-agent-policy`].Arn' \
        --output text 2>/dev/null)

    if [ -n "$POLICY_ARN" ]; then
        # Detach policy from all roles first
        ATTACHED_ROLES=$(aws iam list-entities-for-policy \
            --policy-arn ${POLICY_ARN} \
            --query 'PolicyRoles[].RoleName' \
            --output text 2>/dev/null)

        for ROLE in ${ATTACHED_ROLES}; do
            echo "Detaching policy from role: ${ROLE}"
            aws iam detach-role-policy \
                --role-name ${ROLE} \
                --policy-arn ${POLICY_ARN} \
                2>/dev/null || true
        done

        # Delete policy
        aws iam delete-policy \
            --policy-arn ${POLICY_ARN} \
            2>/dev/null || echo "Could not delete policy"

        echo -e "${GREEN}IAM policy deleted${NC}"
    else
        echo "IAM policy not found"
    fi
fi

echo ""

# Ask about secrets in AWS Secrets Manager
read -p "Delete secrets from AWS Secrets Manager? (yes/no): " DELETE_SECRETS
if [ "$DELETE_SECRETS" == "yes" ]; then
    echo -e "${YELLOW}Deleting secrets...${NC}"

    aws secretsmanager delete-secret \
        --secret-id nvidia-retail-ai/google-api-key \
        --force-delete-without-recovery \
        --region ${REGION} \
        2>/dev/null || echo "Google API key secret not found"

    aws secretsmanager delete-secret \
        --secret-id nvidia-retail-ai/nvidia-api-key \
        --force-delete-without-recovery \
        --region ${REGION} \
        2>/dev/null || echo "NVIDIA API key secret not found"

    echo -e "${GREEN}Secrets deleted${NC}"
fi

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Cleanup Complete${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "Remaining resources to check manually:"
echo "  - VPC (if created by eksctl)"
echo "  - CloudWatch Log Groups"
echo "  - EBS snapshots"
echo "  - Load Balancers (should be deleted automatically)"
echo ""
echo "You can check for remaining resources:"
echo "  aws ec2 describe-vpcs --filters Name=tag:alpha.eksctl.io/cluster-name,Values=${CLUSTER_NAME}"
echo "  aws logs describe-log-groups --log-group-name-prefix /aws/eks/${CLUSTER_NAME}"
