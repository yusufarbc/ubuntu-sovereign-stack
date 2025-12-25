#!/bin/bash
# Install Cert-Manager
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.2/cert-manager.yaml

# Wait for Cert-Manager
kubectl rollout status deployment/cert-manager -n cert-manager
kubectl rollout status deployment/cert-manager-webhook -n cert-manager

# Add Rancher Repo
helm repo add rancher-latest https://releases.rancher.com/server-charts/latest
helm repo update

# Create Namespace
kubectl create namespace cattle-system

# Install Rancher (Using internal self-signed certs for airgap/sovereignty)
helm install rancher rancher-latest/rancher \
  --namespace cattle-system \
  --set hostname=rancher.sovereign.lan \
  --set bootstrapPassword=RancherInitial2025! \
  --set ingress.tls.source=rancher
