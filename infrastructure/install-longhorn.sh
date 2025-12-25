#!/bin/bash
# Install Longhorn via Helm
# Longhorn provides distributed block storage for the Kubernetes cluster.
# Prerequisite: open-iscsi must be installed on all nodes (handled in setup-rke2.yml).

echo "Adding Longhorn Helm repo..."
helm repo add longhorn https://charts.longhorn.io
helm repo update

echo "Creating longhorn-system namespace..."
kubectl create namespace longhorn-system

echo "Installing Longhorn..."
helm install longhorn longhorn/longhorn \
  --namespace longhorn-system \
  --create-namespace \
  --set defaultSettings.defaultDataPath="/var/lib/longhorn"

echo "Longhorn installation initiated. Check status with: kubectl -n longhorn-system get pods"
