# Kubernetes Cluster Setup Guide

## Overview
This guide provides step-by-step instructions to deploy the Ubuntu Sovereign Stack on a bare-metal or IaaS Kubernetes cluster using RKE2, managed by Rancher.

**Target Audience:** Infrastructure operators, DevOps engineers  
**Duration:** 2–4 hours (depending on hardware provisioning)  
**Supported Platform:** Ubuntu Server 22.04 LTS / 24.04 LTS

---

## Part 1: Prerequisites & Planning

### 1.1 Hardware Requirements

| Component | Specification | Rationale |
|-----------|---------------|-----------|
| **Control Plane Nodes** | 3x (min 4 CPUs, 8GB RAM, 50GB disk each) | HA Kubernetes control plane; etcd replication |
| **Worker Nodes** | 2–5x (min 8 CPUs, 16GB RAM, 100GB disk each) | Workload distribution; Longhorn storage replication |
| **Network** | Layer 2 connectivity; static IPs | MetalLB L2 mode; DNS resolution |
| **Storage** | Raw block devices (for Longhorn) | Replicated distributed storage |
| **Total Cluster** | 5–8 nodes (minimum) | Production-ready HA setup |

### 1.2 Network Planning

Before starting, plan and document:

```
Control Plane VIPs:
  - kube-api:       192.168.1.50 (Kubernetes API)
  - rancher:        192.168.1.51 (Rancher UI)
  - ingress:        192.168.1.52-100 (MetalLB pool)

DNS Records:
  - rancher.sovereign.lan → 192.168.1.51
  - *.apps.sovereign.lan → 192.168.1.52 (wildcard ingress)
  
Firewall Rules (inbound to control plane):
  - 6443 (Kubernetes API) from admins
  - 80, 443 (Ingress) from clients
  - 2379–2380 (etcd) between control nodes only
  - 10250 (kubelet) between nodes
  - 10251–10252 (scheduler, controller) internal
```

### 1.3 Infrastructure Inventory

Create `infrastructure/hosts.ini`:

```ini
[control]
cp1 ansible_host=192.168.1.10 ansible_user=ubuntu
cp2 ansible_host=192.168.1.11 ansible_user=ubuntu
cp3 ansible_host=192.168.1.12 ansible_user=ubuntu

[workers]
w1 ansible_host=192.168.1.20 ansible_user=ubuntu
w2 ansible_host=192.168.1.21 ansible_user=ubuntu
w3 ansible_host=192.168.1.22 ansible_user=ubuntu

[all:vars]
ansible_ssh_private_key_file=~/.ssh/id_rsa
```

### 1.4 Pre-Deployment Verification

Run from your Ansible control node:

```bash
# Test SSH connectivity
ansible -i infrastructure/hosts.ini all -m ping

# Verify OS
ansible -i infrastructure/hosts.ini all -m shell -a "lsb_release -a"

# Check hardware specs
ansible -i infrastructure/hosts.ini all -m shell -a "nproc && free -h && df -h /"
```

---

## Part 2: OS & RKE2 Installation

### 2.1 Run Ansible Provisioning

```bash
cd infrastructure

# Install Ansible (if not already installed)
sudo apt update && sudo apt install -y ansible

# Run base provisioning across all nodes
ansible-playbook -i hosts.ini setup-rke2.yml -v

# Monitor output for errors; expect ~10 min per node
```

**What this does:**
- Updates OS packages (security patches)
- Installs Podman (container runtime)
- Downloads & installs RKE2 v1.28.10
- Enables RKE2 systemd service
- Symlinks kubectl, crictl tools

### 2.2 Bootstrap Control Plane (First Master)

SSH to the first control plane node and verify RKE2:

```bash
ssh ubuntu@192.168.1.10

# Wait for RKE2 to fully start
sudo systemctl status rke2-server

# Verify RKE2 is running
sudo /var/lib/rancher/rke2/bin/kubectl --kubeconfig=/etc/rancher/rke2/rke2.yaml get nodes

# Expected output: 1 node in "NotReady" (waiting for CNI)
```

### 2.3 Join Additional Control Nodes

For each additional control plane node:

```bash
ssh ubuntu@192.168.1.11  # (or cp3)

# Retrieve join token from first master
TOKEN=$(ssh ubuntu@192.168.1.10 'cat /var/lib/rancher/rke2/server/node-token')

# Set up RKE2 server joining
cat <<EOF > /tmp/rke2-config.yaml
server: https://192.168.1.10:6443
token: $TOKEN
EOF

sudo INSTALL_RKE2_TYPE=server sh /tmp/install_rke2.sh

# Start RKE2 server
sudo systemctl start rke2-server
sudo systemctl enable rke2-server
```

### 2.4 Join Worker Nodes

For each worker node:

```bash
ssh ubuntu@192.168.1.20  # (or w2, w3)

# Retrieve join token
TOKEN=$(ssh ubuntu@192.168.1.10 'cat /var/lib/rancher/rke2/server/node-token')

# Configure as agent (worker)
cat <<EOF > /tmp/rke2-config.yaml
server: https://192.168.1.10:6443
token: $TOKEN
EOF

sudo INSTALL_RKE2_TYPE=agent sh /tmp/install_rke2.sh

# Start RKE2 agent
sudo systemctl start rke2-agent
sudo systemctl enable rke2-agent
```

### 2.5 Verify Cluster Readiness

From your local machine with kubeconfig:

```bash
# Copy kubeconfig from master
scp ubuntu@192.168.1.10:/etc/rancher/rke2/rke2.yaml ~/.kube/sovereign-stack.yaml

# Update server IP
sed -i 's/127.0.0.1/192.168.1.10/g' ~/.kube/sovereign-stack.yaml
export KUBECONFIG=~/.kube/sovereign-stack.yaml

# Verify all nodes are Ready
kubectl get nodes

# Expected output:
# NAME   STATUS   ROLES                      AGE   VERSION
# cp1    Ready    control-plane,etcd,master  2m    v1.28.10+rke2r1
# cp2    Ready    control-plane,etcd,master  1m    v1.28.10+rke2r1
# cp3    Ready    control-plane,etcd,master  1m    v1.28.10+rke2r1
# w1     Ready    worker                     30s   v1.28.10+rke2r1
# w2     Ready    worker                     30s   v1.28.10+rke2r1
# w3     Ready    worker                     30s   v1.28.10+rke2r1
```

---

## Part 3: System Layer Installation

Deploy cluster prerequisites in strict order:

### 3.1 Install Cert-Manager

Provides automated TLS certificate management:

```bash
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.2/cert-manager.yaml

# Wait for deployment
kubectl wait --for=condition=available --timeout=300s \
  deployment/cert-manager -n cert-manager

# Verify
kubectl get pods -n cert-manager
```

### 3.2 Install MetalLB

Provides L2 load balancer for bare-metal:

```bash
# Edit address pool in kubernetes/system/metallb.yaml
# Change: 192.168.1.200-192.168.1.250 → YOUR_NETWORK_RANGE

# Install MetalLB core (must do before applying config)
kubectl apply -f https://raw.githubusercontent.com/metallb/metallb/v0.14.5/config/manifests/metallb-native.yaml

# Wait for deployment
kubectl wait --for=condition=available --timeout=300s \
  deployment/controller -n metallb-system

# Apply address pool config
kubectl apply -f kubernetes/system/metallb.yaml

# Verify
kubectl get svc -A | grep LoadBalancer  # should see pending → assigned
```

### 3.3 Install Longhorn Storage

Provides distributed block storage for stateful apps:

```bash
# Install Longhorn via Helm (recommended over static manifests)
helm repo add longhorn https://charts.longhorn.io
helm repo update

helm install longhorn longhorn/longhorn \
  --namespace longhorn-system \
  --create-namespace \
  --set defaultClass=true

# Wait for CSI controller/node
kubectl wait --for=condition=ready pod -l app=csi-attacher \
  -n longhorn-system --timeout=600s

# Verify storage class
kubectl get storageclass longhorn
```

### 3.4 Install Rancher (Optional but Recommended)

Provides cluster management UI:

```bash
# Run installation script
cd infrastructure
bash install-rancher.sh

# Monitor Rancher startup
kubectl logs -f deployment/rancher -n cattle-system

# Retrieve admin password (if bootstrapped)
kubectl get secret -n cattle-system bootstrap-password -o jsonpath='{.data.password}' | base64 -d

# Access at https://rancher.sovereign.lan
```

---

## Part 4: Core Identity Services

Deploy after system layer is ready:

### 4.1 Deploy Samba AD + Authentik

```bash
# Apply identity namespace and secrets
# ⚠️ BEFORE APPLYING: Edit kubernetes/core/authentik.yaml
# Replace:
#   - postgres-password: "change-me"
#   - authentik-secret-key: "generate-long-random-key"

# Generate secure secrets
echo "Postgres: $(openssl rand -base64 32)"
echo "Authentik: $(openssl rand -base64 32)"

# Apply manifests
kubectl apply -f kubernetes/core/samba-ad.yaml
kubectl apply -f kubernetes/core/authentik.yaml

# Wait for pods
kubectl wait --for=condition=ready pod -l app=samba-ad \
  -n identity --timeout=600s

# Verify
kubectl get pods -n identity
kubectl get pvc -n identity  # check storage binding
```

---

## Part 5: Applications Layer

Deploy after core services are operational:

### 5.1 Deploy Monitoring (Prometheus + Grafana + Wazuh)

```bash
# Create monitoring namespace and secrets
kubectl apply -f kubernetes/monitoring/prometheus.yaml
kubectl apply -f kubernetes/monitoring/grafana.yaml
kubectl apply -f kubernetes/monitoring/wazuh.yaml

# Verify persistence
kubectl get pvc -n monitoring

# Access Grafana via MetalLB LoadBalancer IP
kubectl get svc -n monitoring grafana
# http://<LOADBALANCER_IP>:3000 (default: admin/admin)
```

### 5.2 Deploy Backup (MinIO + Velero)

```bash
# Create backup namespace and credentials
# ⚠️ BEFORE APPLYING: Update MinIO credentials in kubernetes/backup/minio.yaml

kubectl apply -f kubernetes/backup/minio.yaml
kubectl apply -f kubernetes/backup/velero.yaml

# Wait for MinIO and Velero
kubectl wait --for=condition=ready pod -l app=minio \
  -n backup --timeout=300s

# Configure default backup schedule (after Velero is ready)
kubectl apply -f - <<EOF
apiVersion: velero.io/v1
kind: Schedule
metadata:
  name: daily-backup
  namespace: velero
spec:
  schedule: "0 2 * * *"  # 2 AM UTC daily
  template:
    includedNamespaces: ['*']
    storageLocation: default
    ttl: 720h  # 30 days
EOF

# Verify
kubectl get backupstoragelocations -n velero
```

### 5.3 Deploy Collaboration (Zimbra)

```bash
# Apply Zimbra
kubectl apply -f kubernetes/apps/zimbra.yaml

# Wait for Zimbra server
kubectl wait --for=condition=ready pod -l app=zimbra \
  -n apps --timeout=900s

# Get LoadBalancer IP
kubectl get svc -n apps zimbra

# Access at https://<LOADBALANCER_IP> → Admin Console (port 7071)
```

---

## Part 6: Verification & Validation

### 6.1 Cluster Health Check

```bash
# Node status
kubectl get nodes -o wide

# Pod status (all namespaces)
kubectl get pods -A --field-selector=status.phase!=Running,status.phase!=Succeeded

# StorageClass and PVs
kubectl get sc,pv,pvc -A

# Services and IPs
kubectl get svc -A | grep -E "^(NAMESPACE|default|identity|monitoring|apps|backup|longhorn)"
```

### 6.2 CNI & Networking Verification

```bash
# Deploy test pod
kubectl run -it --rm test-pod --image=alpine -- sh

# Inside pod:
ping 8.8.8.8  # external connectivity
nslookup kubernetes.default  # DNS resolution
exit
```

### 6.3 Storage Verification

```bash
# Create test PVC and pod
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
      storage: 1Gi
---
apiVersion: v1
kind: Pod
metadata:
  name: test-storage
spec:
  containers:
  - name: test
    image: alpine
    command: ["sleep", "3600"]
    volumeMounts:
    - name: data
      mountPath: /mnt
  volumes:
  - name: data
    persistentVolumeClaim:
      claimName: test-pvc
EOF

# Verify persistence
kubectl exec test-storage -- sh -c 'echo "test" > /mnt/test.txt && cat /mnt/test.txt'

# Cleanup
kubectl delete pod test-storage pvc test-pvc
```

### 6.4 Ingress Verification

```bash
# Check ingress controller
kubectl get pods -n kube-system | grep traefik

# Test ingress (if any deployed)
kubectl get ingress -A
```

---

## Part 7: Post-Deployment Configuration

### 7.1 Configure DNS

Add DNS records pointing to MetalLB pool:

```dns
rancher.sovereign.lan     → 192.168.1.52
*.apps.sovereign.lan      → 192.168.1.52
samba.sovereign.lan       → 192.168.1.52
authentik.sovereign.lan   → 192.168.1.52
grafana.sovereign.lan     → 192.168.1.52
prometheus.sovereign.lan  → 192.168.1.52
```

### 7.2 Configure Backups

Test Velero backup:

```bash
# Create manual backup
velero backup create initial-backup --wait

# Check backup status
velero backup get
velero backup logs initial-backup

# Schedule daily backups (already done in 5.2)
kubectl get schedule -n velero
```

### 7.3 Secure Rancher UI

```bash
# Generate self-signed cert (or use your CA)
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout tls.key -out tls.crt -subj "/CN=rancher.sovereign.lan"

# Create TLS secret
kubectl create secret tls rancher-tls -n cattle-system \
  --cert=tls.crt --key=tls.key

# Update Rancher Ingress to use TLS
kubectl patch ingress -n cattle-system rancher \
  -p '{"spec":{"tls":[{"hosts":["rancher.sovereign.lan"],"secretName":"rancher-tls"}]}}'
```

---

## Part 8: Troubleshooting

### Node Not Ready

```bash
# Check kubelet service
sudo systemctl status rke2-server  # (or rke2-agent on workers)

# Check kubelet logs
sudo journalctl -u rke2-server -n 50 --no-pager

# Check CNI plugin
kubectl get daemonset -A | grep -i cni
```

### Pod Stuck in Pending

```bash
# Describe pod
kubectl describe pod <pod-name> -n <namespace>

# Check PVC binding (if storage-related)
kubectl get pvc -n <namespace>

# Check node capacity
kubectl top nodes
kubectl describe node <node-name>
```

### Storage Not Available

```bash
# Check Longhorn status
kubectl get pods -n longhorn-system
kubectl logs -n longhorn-system deployment/longhorn-manager

# Check replicas
kubectl get -n longhorn-system volumereplicasets.longhorn.io
```

### Rancher Bootstrap Failed

```bash
# Reset bootstrap password
kubectl delete secret bootstrap-password -n cattle-system

# Restart Rancher
kubectl rollout restart deployment/rancher -n cattle-system

# Check logs
kubectl logs -f deployment/rancher -n cattle-system
```

---

## Appendix: Deployment Order Dependency Graph

```
1. RKE2 Cluster (all nodes)
   ↓
2. Cert-Manager
   ↓
3. MetalLB
   ├→ 4a. Longhorn (storage)
   ├→ 4b. Rancher (management UI) [optional]
   ↓
5. Core Services (Samba AD + Authentik)
   ↓
6. Apps Layer
   ├→ 6a. Monitoring (Prometheus + Grafana + Wazuh)
   ├→ 6b. Backup (MinIO + Velero)
   └→ 6c. Collaboration (Zimbra)
```

---

## Next Steps

1. **Day 2 Operations:** See [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md) for post-installation validation.
2. **Client Provisioning:** Follow [CLIENT_STRATEGY.md](CLIENT_STRATEGY.md) to deploy the "Flexible 10" desktops.
3. **Operational Runbooks:** Reference individual service documentation in `/docs/`.

---

**Last Updated:** 2024  
**Status:** Production-Ready  
**Support:** See README.md for community channels
