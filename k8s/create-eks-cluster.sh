#!/bin/bash

# EKS Cluster Creation Script for NVIDIA Retail AI

set -e

# Configuration
CLUSTER_NAME="nvidia-retail-ai-cluster"
REGION="us-east-1"  # Change to your preferred region
NODE_TYPE="t3.xlarge"  # 4 vCPU, 16 GB RAM
MIN_NODES=2
MAX_NODES=5
DESIRED_NODES=3

echo "========================================="
echo "Creating EKS Cluster: ${CLUSTER_NAME}"
echo "Region: ${REGION}"
echo "========================================="

# Check if eksctl is installed
if ! command -v eksctl &> /dev/null; then
    echo "ERROR: eksctl is not installed"
    echo "Install from: https://eksctl.io/installation/"
    exit 1
fi

# Create EKS cluster
eksctl create cluster \
    --name ${CLUSTER_NAME} \
    --region ${REGION} \
    --node-type ${NODE_TYPE} \
    --nodes ${DESIRED_NODES} \
    --nodes-min ${MIN_NODES} \
    --nodes-max ${MAX_NODES} \
    --managed \
    --with-oidc \
    --ssh-access \
    --ssh-public-key ~/.ssh/id_rsa.pub \
    --enable-ssm \
    --full-ecr-access \
    --asg-access \
    --alb-ingress-access \
    --external-dns-access

echo ""
echo "========================================="
echo "Installing AWS Load Balancer Controller"
echo "========================================="

# Install AWS Load Balancer Controller
helm repo add eks https://aws.github.io/eks-charts
helm repo update

kubectl apply -k "github.com/aws/eks-charts/stable/aws-load-balancer-controller//crds?ref=master"

AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)

eksctl create iamserviceaccount \
  --cluster=${CLUSTER_NAME} \
  --namespace=kube-system \
  --name=aws-load-balancer-controller \
  --attach-policy-arn=arn:aws:iam::${AWS_ACCOUNT_ID}:policy/AWSLoadBalancerControllerIAMPolicy \
  --override-existing-serviceaccounts \
  --approve

helm install aws-load-balancer-controller eks/aws-load-balancer-controller \
  -n kube-system \
  --set clusterName=${CLUSTER_NAME} \
  --set serviceAccount.create=false \
  --set serviceAccount.name=aws-load-balancer-controller

echo ""
echo "========================================="
echo "Installing EBS CSI Driver"
echo "========================================="

# Install EBS CSI Driver for persistent volumes
eksctl create iamserviceaccount \
    --name ebs-csi-controller-sa \
    --namespace kube-system \
    --cluster ${CLUSTER_NAME} \
    --region ${REGION} \
    --attach-policy-arn arn:aws:iam::aws:policy/service-role/AmazonEBSCSIDriverPolicy \
    --approve \
    --override-existing-serviceaccounts

eksctl create addon \
    --name aws-ebs-csi-driver \
    --cluster ${CLUSTER_NAME} \
    --region ${REGION} \
    --service-account-role-arn arn:aws:iam::${AWS_ACCOUNT_ID}:role/AmazonEKS_EBS_CSI_DriverRole \
    --force

echo ""
echo "========================================="
echo "Cluster Created Successfully!"
echo "========================================="
echo ""
echo "Cluster Name: ${CLUSTER_NAME}"
echo "Region: ${REGION}"
echo ""
echo "Next steps:"
echo "1. Run './deploy.sh' to deploy the application"
echo "2. Configure your secrets"
echo "3. Access your application via the ALB URL"
