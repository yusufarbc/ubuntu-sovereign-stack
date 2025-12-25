# Quick Start Guide

Get the Ubuntu Sovereign Stack running locally or on a small lab cluster in under 2 hours.

## For Local Testing (Docker Desktop or Podman Desktop)

### Prerequisites
- Docker Desktop (4.10+) or Podman Desktop with Kubernetes enabled
- macOS, Windows, or Linux
- 8GB RAM available
- 50GB free disk space

### Quick Local Setup

1. **Enable Kubernetes in Docker Desktop**
   - Docker → Settings → Kubernetes → Enable Kubernetes
   - Wait for cluster to start (~5 min)

2. **Verify kubectl access**
   ```bash
   kubectl cluster-info
   kubectl get nodes
   ```

3. **Install MetalLB (for LoadBalancer services)**
   ```bash
   kubectl apply -f https://raw.githubusercontent.com/metallb/metallb/v0.14.5/config/manifests/metallb-native.yaml
   
   # Configure for Docker Desktop IPs
   kubectl apply -f - <<EOF
   apiVersion: v1
   kind: ConfigMap
   metadata:
     namespace: metallb-system
     name: config
   data:
     config: |
       address-pools:
       - name: default
         protocol: layer2
         addresses:
         - 172.17.0.200-172.17.0.250
   EOF
   ```

4. **Install Cert-Manager**
   ```bash
   kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.2/cert-manager.yaml
   ```

5. **Install Longhorn Storage**
   ```bash
   helm repo add longhorn https://charts.longhorn.io
   helm repo update
   helm install longhorn longhorn/longhorn \
     --namespace longhorn-system \
     --create-namespace \
     --set defaultClass=true
   ```

6. **Deploy Core Services**
   ```bash
   cd kubernetes/core
   
   # Update credentials before applying
   # Edit authentik.yaml: change postgres-password and secret-key
   
   kubectl apply -f samba-ad.yaml
   kubectl apply -f authentik.yaml
   
   # Wait for pods
   kubectl get pods -n identity --watch
   ```

7. **Deploy Monitoring**
   ```bash
   cd ../monitoring
   kubectl apply -f prometheus.yaml
   kubectl apply -f grafana.yaml
   
   # Access Grafana
   kubectl port-forward svc/grafana 3000:3000 -n monitoring
   # http://localhost:3000 (admin/admin)
   ```

8. **Deploy Backup Infrastructure**
   ```bash
   cd ../backup
   kubectl apply -f minio.yaml
   kubectl apply -f velero.yaml
   ```

---

## For Small Lab Cluster (3 Nodes)

### Hardware
- 3x Linux VMs (4 CPU, 8GB RAM, 50GB disk each)
- Ubuntu Server 22.04 LTS or later
- Network: all nodes can reach each other

### Step 1: Prepare Nodes

On all nodes:

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Ansible on one node (control node)
sudo apt install -y ansible git

# Clone repository
git clone https://github.com/your-org/ubuntu-sovereign-stack.git
cd ubuntu-sovereign-stack
```

### Step 2: Configure Inventory

Edit `infrastructure/hosts.ini`:

```ini
[control]
node1 ansible_host=192.168.1.10 ansible_user=ubuntu ansible_ssh_key_file=~/.ssh/id_rsa

[workers]
node2 ansible_host=192.168.1.11 ansible_user=ubuntu ansible_ssh_key_file=~/.ssh/id_rsa
node3 ansible_host=192.168.1.12 ansible_user=ubuntu ansible_ssh_key_file=~/.ssh/id_rsa

[all:vars]
ansible_python_interpreter=/usr/bin/python3
```

### Step 3: Set Up SSH Key Access

```bash
# Generate SSH key (if not present)
ssh-keygen -t rsa -b 4096 -f ~/.ssh/id_rsa -N ""

# Copy to all nodes
for host in 192.168.1.10 192.168.1.11 192.168.1.12; do
  ssh-copy-id -i ~/.ssh/id_rsa.pub ubuntu@$host
done

# Test connectivity
ansible -i infrastructure/hosts.ini all -m ping
```

### Step 4: Deploy with Ansible

```bash
cd infrastructure

# Run provisioning (watch output for errors)
ansible-playbook -i hosts.ini setup-rke2.yml -v

# Should complete in ~15 min
```

### Step 5: Verify Cluster

```bash
# Copy kubeconfig from master
scp ubuntu@192.168.1.10:/etc/rancher/rke2/rke2.yaml ~/.kube/lab-cluster.yaml

# Update server IP
sed -i 's/127.0.0.1/192.168.1.10/g' ~/.kube/lab-cluster.yaml
export KUBECONFIG=~/.kube/lab-cluster.yaml

# Verify nodes
kubectl get nodes
# Expected: 1 master + 2 workers, all Ready
```

### Step 6: Deploy System Layer

```bash
# Install Cert-Manager
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.2/cert-manager.yaml

# Install MetalLB
kubectl apply -f https://raw.githubusercontent.com/metallb/metallb/v0.14.5/config/manifests/metallb-native.yaml

# Configure MetalLB address pool
kubectl apply -f - <<EOF
apiVersion: v1
kind: ConfigMap
metadata:
  namespace: metallb-system
  name: config
data:
  config: |
    address-pools:
    - name: default
      protocol: layer2
      addresses:
      - 192.168.1.200-192.168.1.210
EOF

# Install Longhorn
helm repo add longhorn https://charts.longhorn.io
helm install longhorn longhorn/longhorn \
  --namespace longhorn-system \
  --create-namespace \
  --set defaultClass=true
```

### Step 7: Deploy Applications

```bash
# Deploy all manifests in order
cd kubernetes

# Core services
kubectl apply -f core/samba-ad.yaml
kubectl apply -f core/authentik.yaml

# Monitoring
kubectl apply -f monitoring/prometheus.yaml
kubectl apply -f monitoring/grafana.yaml
kubectl apply -f monitoring/wazuh.yaml

# Backup
kubectl apply -f backup/minio.yaml
kubectl apply -f backup/velero.yaml

# Apps
kubectl apply -f apps/zimbra.yaml

# Wait for all pods
kubectl get pods -A --watch
```

### Step 8: Configure DNS

Add to your /etc/hosts or DNS server:

```
192.168.1.200 rancher.sovereign.lan grafana.sovereign.lan authentik.sovereign.lan
192.168.1.200 prometheus.sovereign.lan wazuh.sovereign.lan zimbra.sovereign.lan
```

### Step 9: Access Services

```bash
# Get LoadBalancer IPs
kubectl get svc -A | grep LoadBalancer

# Grafana
# http://grafana.sovereign.lan:3000 (admin/admin)

# Prometheus
# http://prometheus.sovereign.lan:9090

# Authentik
# https://authentik.sovereign.lan (akadmin/password)

# Zimbra Admin
# https://zimbra.sovereign.lan:7071/zimbraAdmin (admin/password)
```

---

## Configuration Secrets

⚠️ **Change these immediately in production:**

### Authentik
```bash
# Default credentials in kubernetes/core/authentik.yaml
postgres-password: "change-me" → generate with: openssl rand -base64 32
authentik-secret-key: "generate-a-long-random-string" → openssl rand -base64 32

# Update in secret
kubectl patch secret authentik-secrets -n identity --type merge -p '{"stringData":{"postgres-password":"new-password"}}'
```

### Grafana
```bash
# Default admin/admin
kubectl exec -it deployment/grafana -n monitoring -- \
  grafana-cli admin reset-admin-password new-password
```

### MinIO
```bash
# Default minioadmin/minioadmin
kubectl patch secret minio-credentials -n backup --type merge -p '{"stringData":{"root-user":"new-admin","root-password":"new-password"}}'
```

### Zimbra
```bash
# Default admin/password
# Change in Zimbra Admin Console → Global Settings
```

---

## Testing the Stack

### Test Identity (Samba + Authentik)

```bash
# Create test user in Samba AD
kubectl exec -it pod/samba-ad-0 -n identity -- \
  samba-tool user create testuser password123

# Verify in Authentik UI
# http://authentik.sovereign.lan
# Users → List → should see testuser
```

### Test Storage (Longhorn)

```bash
# Create PVC and verify binding
kubectl apply -f - <<EOF
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: test-pvc
spec:
  accessModes: ["ReadWriteOnce"]
  storageClassName: longhorn
  resources:
    requests:
      storage: 5Gi
---
apiVersion: v1
kind: Pod
metadata:
  name: test-storage
spec:
  containers:
  - name: alpine
    image: alpine
    command: ["sleep", "3600"]
    volumeMounts:
    - name: data
      mountPath: /data
  volumes:
  - name: data
    persistentVolumeClaim:
      claimName: test-pvc
EOF

# Write and read data
kubectl exec test-storage -- sh -c 'echo "test" > /data/test.txt && cat /data/test.txt'

# Cleanup
kubectl delete pod test-storage pvc test-pvc
```

### Test Backup (Velero)

```bash
# Create backup
velero backup create test-backup --wait

# Verify
velero backup get test-backup

# Delete backup after testing
velero backup delete test-backup --confirm
```

---

## Scaling the Cluster

### Add More Worker Nodes

1. **Prepare new node** (same as original setup):
   ```bash
   # Run Ansible provisioning
   ansible-playbook -i infrastructure/hosts.ini setup-rke2.yml -e "ansible_host=new-node-ip"
   ```

2. **Verify** node joins cluster:
   ```bash
   kubectl get nodes  # should see new node in NotReady
   # After ~2 min → Ready
   ```

### Scale Applications

```bash
# Scale Prometheus replicas
kubectl scale deployment prometheus -n monitoring --replicas=3

# Scale Grafana replicas
kubectl scale deployment grafana -n monitoring --replicas=2

# Monitor pods
kubectl get pods -n monitoring -l app=prometheus --watch
```

---

## Troubleshooting Quick Fixes

### Pods Not Starting

```bash
# Check pod status
kubectl describe pod <pod-name> -n <namespace>

# Common issues:
# 1. Storage not available: kubectl get pvc -n <namespace>
# 2. Image pull error: kubectl logs <pod-name> -n <namespace>
# 3. Resource quota: kubectl describe namespace <namespace>

# Fix: Delete and recreate
kubectl delete pod <pod-name> -n <namespace>
```

### LoadBalancer Stuck in Pending

```bash
# Check MetalLB
kubectl get pods -n metallb-system
kubectl describe svc <service> -n <namespace>

# Ensure address pool is configured
kubectl get configmap config -n metallb-system -o yaml
```

### Out of Disk Space

```bash
# On node with issue
df -h /var/lib/rancher

# Clean up
sudo podman system prune -a
sudo journalctl --vacuum=100M

# If persistent: add more disk to node
```

---

## Next Steps

1. **Deploy client workstations** → See [CLIENT_STRATEGY.md](CLIENT_STRATEGY.md)
2. **Harden security** → See [SECURITY_HARDENING.md](SECURITY_HARDENING.md) (TBD)
3. **Automate backups** → Configure Velero schedules in [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md#tier-3-backup--miniovlero)
4. **Monitor & alert** → Configure Grafana alerts
5. **Join to existing domain** → Configure Samba/Authentik as domain controller

---

## Support & Troubleshooting

- **Kubernetes docs:** https://kubernetes.io/docs/
- **RKE2 docs:** https://docs.rke2.io/
- **Rancher docs:** https://rancher.com/docs/rancher/latest/
- **Longhorn docs:** https://longhorn.io/docs/
- **Cert-Manager docs:** https://cert-manager.io/docs/

---

**Status:** Ready for Lab/Dev Use  
**Last Updated:** 2024  
**Production Checklist:** See [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md)
