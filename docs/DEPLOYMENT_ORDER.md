# Deployment Order & Dependencies

This document specifies the order in which Kubernetes manifests must be deployed and their dependencies.

## Deployment Phases

```
Phase 0: Cluster Bootstrap (RKE2)
  ↓
Phase 1: System Layer (Storage, Networking, PKI)
  ├→ Cert-Manager
  ├→ MetalLB
  ├→ Longhorn
  └→ Rancher (optional management UI)
  ↓
Phase 2: Core Identity Services
  ├→ Samba AD (LDAP source of truth)
  └→ Authentik (SSO/MFA frontend)
  ↓
Phase 3: Observability & Backup
  ├→ Monitoring (Prometheus, Grafana, Wazuh)
  └→ Backup (MinIO, Velero)
  ↓
Phase 4: Applications
  └→ Zimbra (mail/collaboration)
  ↓
Phase 5: Client Deployment
  └→ Ubuntu desktop workstations ("Flexible 10")
```

---

## Phase 0: RKE2 Cluster Bootstrap

**Prerequisites:** Ubuntu Server LTS nodes with SSH access

**Deployment Method:** Ansible

```bash
cd infrastructure
ansible-playbook -i hosts.ini setup-rke2.yml
```

**What's Installed:**
- RKE2 server (Kubernetes control plane)
- RKE2 agents (worker nodes)
- Podman (container runtime, daemonless)
- kubectl, crictl symlinks

**Verification:**
```bash
export KUBECONFIG=~/.kube/sovereign-stack.yaml
kubectl get nodes
# All nodes should show STATUS: Ready
```

**Timeline:** ~15–20 minutes

---

## Phase 1: System Layer

**Order is CRITICAL**: Must follow sequence below.

### 1.1 Cert-Manager (First)

**Purpose:** Automated TLS certificate provisioning and renewal

**Manifest:** External (not in repo)

```bash
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.2/cert-manager.yaml

# Wait for deployment
kubectl wait --for=condition=available --timeout=300s \
  deployment/cert-manager -n cert-manager
```

**Why first:** MetalLB, Rancher, and apps depend on TLS certs provided by Cert-Manager.

**Verification:**
```bash
kubectl get pods -n cert-manager
kubectl get clusterissuer
```

**Timeline:** 3–5 minutes

---

### 1.2 MetalLB (After Cert-Manager)

**Purpose:** L2 load balancer for bare-metal; enables LoadBalancer service type

**Manifest:** `kubernetes/system/metallb.yaml` + external Helm chart

```bash
# Install MetalLB core
kubectl apply -f https://raw.githubusercontent.com/metallb/metallb/v0.14.5/config/manifests/metallb-native.yaml

# Wait for controller/speaker
kubectl wait --for=condition=ready pod -l app=speaker -n metallb-system --timeout=300s

# Apply address pool config
# ⚠️ EDIT FIRST: Update 192.168.1.200-192.168.1.250 to match your network
kubectl apply -f kubernetes/system/metallb.yaml
```

**Why after Cert-Manager:** MetalLB services will need TLS certs for Ingress.

**Why before Longhorn/Rancher:** They expose themselves via LoadBalancer services.

**Verification:**
```bash
kubectl get pods -n metallb-system
kubectl get configmap config -n metallb-system -o yaml | grep addresses
```

**Timeline:** 2–3 minutes

---

### 1.3 Longhorn Storage (After MetalLB)

**Purpose:** Distributed block storage for stateful workloads

**Manifest:** Helm chart (YAML in `kubernetes/system/longhorn.yaml` is placeholder)

```bash
helm repo add longhorn https://charts.longhorn.io
helm repo update

helm install longhorn longhorn/longhorn \
  --namespace longhorn-system \
  --create-namespace \
  --set defaultClass=true \
  --set persistence.defaultClass=true

# Wait for CSI controller/node
kubectl wait --for=condition=ready pod -l app=csi-attacher \
  -n longhorn-system --timeout=600s
```

**Why after MetalLB:** Longhorn UI exposes itself via LoadBalancer; needs IP from MetalLB pool.

**Why before applications:** Apps create PVCs for databases, mail, config.

**Verification:**
```bash
kubectl get pods -n longhorn-system
kubectl get storageclass longhorn
kubectl get pvc -A  # should all show Bound after apps deploy
```

**Timeline:** 5–10 minutes

---

### 1.4 Rancher Management (Optional, After Longhorn)

**Purpose:** Kubernetes cluster management UI

**Manifest:** External (Helm chart via `infrastructure/install-rancher.sh`)

```bash
# Edit install-rancher.sh to set hostname
bash infrastructure/install-rancher.sh

# Monitor startup
kubectl logs -f deployment/rancher -n cattle-system
```

**Why optional:** Rancher simplifies UI management but not required for core functionality.

**Why after Longhorn:** Rancher creates PVCs for local cluster management.

**Verification:**
```bash
kubectl get pods -n cattle-system
kubectl get svc -n cattle-system rancher
# Access: https://<LoadBalancer_IP>
```

**Timeline:** 5–10 minutes

**Sign-off for Phase 1:**
```bash
kubectl get nodes  # all Ready
kubectl get pods -A --field-selector=status.phase!=Running,status.phase!=Succeeded  # none
kubectl get pvc -A  # none should be Pending
```

---

## Phase 2: Core Identity Services

**Prerequisites:** Phase 1 complete

**Order:** Samba AD → Authentik (AD provides LDAP backend)

### 2.1 Samba AD (First)

**Purpose:** LDAP directory (Active Directory compatible)

**Manifest:** `kubernetes/core/samba-ad.yaml`

**Pre-deployment:**
```bash
# ⚠️ EDIT BEFORE APPLYING
# kubernetes/core/samba-ad.yaml → update:
#   - Samba domain (sambadomain)
#   - Admin password
#   - Network configuration (CIDR)

# Create identity namespace
kubectl create namespace identity

# Apply manifest
kubectl apply -f kubernetes/core/samba-ad.yaml
```

**Wait for readiness:**
```bash
kubectl wait --for=condition=ready pod -l app=samba-ad \
  -n identity --timeout=300s
```

**Verification:**
```bash
# Check pod status
kubectl get pods -n identity -l app=samba-ad

# Test LDAP (from pod or external)
kubectl run -it --rm ldap-test --image=alpine --restart=Never -- \
  apk add openldap-clients && \
  ldapsearch -H ldap://samba-ad.identity.svc:389 \
    -D "cn=admin,dc=example,dc=com" -w password \
    -b "dc=example,dc=com" "objectClass=*"
```

**Timeline:** 5–10 minutes

---

### 2.2 Authentik (After Samba AD)

**Purpose:** SSO + MFA frontend; uses Samba AD as identity backend

**Manifest:** `kubernetes/core/authentik.yaml`

**Pre-deployment:**
```bash
# ⚠️ CRITICAL: Generate strong secrets BEFORE applying
echo "Postgres Password: $(openssl rand -base64 32)"
echo "Authentik Secret Key: $(openssl rand -base64 32)"

# Edit kubernetes/core/authentik.yaml:
#   - postgres-password: <generated>
#   - authentik-secret-key: <generated>
#   - Configure LDAP backend (samba-ad.identity.svc)

# Apply manifest
kubectl apply -f kubernetes/core/authentik.yaml
```

**Wait for readiness:**
```bash
kubectl wait --for=condition=ready pod -l app=authentik-server \
  -n identity --timeout=600s
```

**Verification:**
```bash
# Check deployments
kubectl get pods -n identity

# Check database connectivity
kubectl logs deployment/authentik-postgres -n identity

# Check storage
kubectl get pvc -n identity
```

**Post-deployment config:**
```bash
# Get Authentik LoadBalancer IP
AUTHENTIK_IP=$(kubectl get svc -n identity authentik -o jsonpath='{.status.loadBalancer.ingress[0].ip}')

# Access admin console: https://$AUTHENTIK_IP
# Default user: akadmin
# Default password: (check logs or use password reset)

# Configure LDAP provider:
# Authentik UI → Providers → LDAP
# LDAP Server: samba-ad.identity.svc:389
# Bind DN: cn=admin,dc=example,dc=com
# Bind Password: <samba admin password>
```

**Timeline:** 10–15 minutes

**Sign-off for Phase 2:**
```bash
kubectl get pods -n identity  # all Running
kubectl get pvc -n identity  # all Bound

# Test LDAP + SSO working
# Create test user in Samba
# Login to Authentik with test user
```

---

## Phase 3: Observability & Backup

**Prerequisites:** Phase 1 complete (Phase 2 optional but recommended)

**Parallel deployment possible:** Monitoring and Backup are independent

### 3.1 Monitoring Stack

#### 3.1.1 Prometheus (Metrics Collection)

**Manifest:** `kubernetes/monitoring/prometheus.yaml`

```bash
kubectl apply -f kubernetes/monitoring/prometheus.yaml

kubectl wait --for=condition=ready pod -l app=prometheus \
  -n monitoring --timeout=300s
```

**Verification:**
```bash
kubectl get pods -n monitoring -l app=prometheus
kubectl get svc -n monitoring prometheus
```

---

#### 3.1.2 Grafana (Visualization)

**Manifest:** `kubernetes/monitoring/grafana.yaml`

**Dependencies:** Prometheus must be running (for data source)

```bash
kubectl apply -f kubernetes/monitoring/grafana.yaml

kubectl wait --for=condition=ready pod -l app=grafana \
  -n monitoring --timeout=300s
```

**Post-deployment config:**
```bash
# Get Grafana IP
GRAFANA_IP=$(kubectl get svc -n monitoring grafana -o jsonpath='{.status.loadBalancer.ingress[0].ip}')

# Access: http://$GRAFANA_IP:3000
# Default: admin/admin (CHANGE IMMEDIATELY)

# Add data source:
# Configuration → Data Sources → Add Prometheus
# URL: http://prometheus.monitoring.svc:9090
```

---

#### 3.1.3 Wazuh (Security Monitoring)

**Manifest:** `kubernetes/monitoring/wazuh.yaml`

**Dependencies:** None (independent)

```bash
kubectl apply -f kubernetes/monitoring/wazuh.yaml

kubectl wait --for=condition=ready pod -l app=wazuh \
  -n monitoring --timeout=600s
```

**Verification:**
```bash
kubectl get pods -n monitoring -l app=wazuh
kubectl get svc -n monitoring wazuh
```

**Timeline for 3.1:** 15–20 minutes total

---

### 3.2 Backup Stack

#### 3.2.1 MinIO (S3-Compatible Storage)

**Manifest:** `kubernetes/backup/minio.yaml`

**Pre-deployment:**
```bash
# ⚠️ EDIT BEFORE APPLYING
# kubernetes/backup/minio.yaml → update:
#   - Root user/password (default: minioadmin/minioadmin)
#   - Storage size requirements

echo "MinIO Admin: $(openssl rand -base64 12)"
echo "MinIO Password: $(openssl rand -base64 32)"

kubectl apply -f kubernetes/backup/minio.yaml

kubectl wait --for=condition=ready pod -l app=minio \
  -n backup --timeout=300s
```

**Verification:**
```bash
# Get MinIO IP
MINIO_IP=$(kubectl get svc -n backup minio -o jsonpath='{.status.loadBalancer.ingress[0].ip}')

# Access UI: http://$MINIO_IP:9001
# CLI test:
kubectl exec -it pod/minio-0 -n backup -- \
  mc mb minio/backup-uss  # create bucket for Velero
```

---

#### 3.2.2 Velero (Backup Management)

**Manifest:** `kubernetes/backup/velero.yaml`

**Dependencies:** MinIO must be running + bucket created

**Pre-deployment:**
```bash
# ⚠️ EDIT BEFORE APPLYING
# kubernetes/backup/velero.yaml → update:
#   - MinIO credentials (match Step 3.2.1)
#   - S3 URL: http://minio.backup.svc:9000

kubectl apply -f kubernetes/backup/velero.yaml

kubectl wait --for=condition=ready pod -l app=velero \
  -n velero --timeout=300s
```

**Post-deployment config:**
```bash
# Create default backup schedule
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
    ttl: 720h  # 30 days retention
EOF

# Test backup
velero backup create test-backup --wait
velero backup get
```

**Verification:**
```bash
velero version
velero backup-location get
velero backup get
```

**Timeline for 3.2:** 10–15 minutes total

**Sign-off for Phase 3:**
```bash
# Metrics collecting
curl http://$PROMETHEUS_IP:9090/api/v1/targets

# Grafana showing data
# Access http://$GRAFANA_IP:3000

# Velero backup completed
velero backup get test-backup | grep Completed
```

---

## Phase 4: Applications

**Prerequisites:** Phase 1 + Phase 2 complete

### 4.1 Zimbra (Mail & Collaboration)

**Manifest:** `kubernetes/apps/zimbra.yaml`

**Pre-deployment:**
```bash
# ⚠️ CRITICAL: Review resource requests
# Zimbra needs: 8GB RAM, 100GB storage minimum

# Create apps namespace
kubectl create namespace apps

# Apply manifest
kubectl apply -f kubernetes/apps/zimbra.yaml
```

**Wait for readiness:**
```bash
kubectl wait --for=condition=ready pod -l app=zimbra \
  -n apps --timeout=900s

# Can take 10–15 minutes (downloading large container)
```

**Verification:**
```bash
kubectl get pods -n apps -l app=zimbra
kubectl get svc -n apps zimbra

# Access Admin Console
ZIMBRA_IP=$(kubectl get svc -n apps zimbra -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
# https://$ZIMBRA_IP:7071/zimbraAdmin
# Default: admin/password
```

**Timeline:** 15–20 minutes

**Sign-off for Phase 4:**
```bash
# Zimbra pod Running
kubectl get pods -n apps

# Mail services active
kubectl exec pod/zimbra-0 -n apps -- \
  sudo -u zimbra /opt/zimbra/bin/zmcontrol status
```

---

## Phase 5: Client Deployment

**Prerequisites:** All phases complete + network infrastructure ready

**See:** [CLIENT_STRATEGY.md](docs/CLIENT_STRATEGY.md)

---

## Deployment Timeline Summary

| Phase | Duration | Sequential | Notes |
|-------|----------|-----------|-------|
| Phase 0: RKE2 | 15–20 min | Yes | Infrastructure bootstrap |
| Phase 1: System Layer | 20–30 min | Yes | Must follow order: Cert-Manager → MetalLB → Longhorn → Rancher |
| Phase 2: Identity | 15–25 min | Yes | Samba AD → Authentik |
| Phase 3: Monitoring+Backup | 25–35 min | Partial | Monitoring & Backup parallel; Prometheus → Grafana sequential |
| Phase 4: Apps | 15–20 min | No | Zimbra independent |
| Phase 5: Clients | 30–60 min | No | Per-workstation provisioning |
| **Total** | **2–3 hours** | Optimized | With parallelization |

---

## Validation Script

Run after each phase to verify prerequisites:

```bash
#!/bin/bash
# check-phase.sh

PHASE=$1
KUBECONFIG=~/.kube/sovereign-stack.yaml

case $PHASE in
  1)
    echo "Checking Phase 1..."
    kubectl get pods -n cert-manager
    kubectl get pods -n metallb-system
    kubectl get pods -n longhorn-system
    kubectl get storageclass longhorn
    ;;
  2)
    echo "Checking Phase 2..."
    kubectl get pods -n identity
    kubectl get svc -n identity
    ;;
  3)
    echo "Checking Phase 3..."
    kubectl get pods -n monitoring
    kubectl get pods -n backup
    kubectl get pvc -n backup
    ;;
  4)
    echo "Checking Phase 4..."
    kubectl get pods -n apps
    kubectl get svc -n apps
    ;;
esac

echo "All pods:"
kubectl get pods -A --field-selector=status.phase!=Running,status.phase!=Succeeded
```

---

## Rollback Procedures

### Uninstall Phase 4 (Apps)

```bash
kubectl delete -f kubernetes/apps/zimbra.yaml
kubectl delete namespace apps
```

### Uninstall Phase 3 (Backup & Monitoring)

```bash
kubectl delete -f kubernetes/backup/
kubectl delete -f kubernetes/monitoring/
kubectl delete namespace backup monitoring
```

### Uninstall Phase 2 (Identity)

```bash
kubectl delete -f kubernetes/core/
kubectl delete namespace identity
```

### Uninstall Phase 1 (System Layer)

```bash
# Longhorn
helm uninstall longhorn --namespace longhorn-system

# MetalLB
kubectl delete -f https://raw.githubusercontent.com/metallb/metallb/v0.14.5/config/manifests/metallb-native.yaml

# Cert-Manager
kubectl delete -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.2/cert-manager.yaml

# Rancher (if installed)
helm uninstall rancher --namespace cattle-system
```

---

**Last Updated:** 2024  
**Status:** Ready for Use  
**Next:** [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md) for post-deployment validation
