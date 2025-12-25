# Deployment Verification Checklist

Post-installation validation and troubleshooting guide for the Ubuntu Sovereign Stack.

## Pre-Flight Checks (Before Production)

- [ ] **Cluster Node Readiness**
  ```bash
  kubectl get nodes -o wide
  # All nodes should show STATUS: Ready
  # All ROLES should be assigned (control-plane, etcd, or worker)
  ```

- [ ] **All System Pods Running**
  ```bash
  kubectl get pods -A --field-selector=status.phase!=Running,status.phase!=Succeeded
  # Should return 0 results (no failed/pending pods)
  ```

- [ ] **Persistent Storage Bound**
  ```bash
  kubectl get pvc -A
  # All PVCs should show STATUS: Bound
  # All PVs should show STATUS: Bound
  ```

- [ ] **Network Connectivity**
  ```bash
  kubectl run -it --rm debug --image=alpine -- sh
  # Inside pod: ping 8.8.8.8 (external), nslookup kubernetes.default (DNS)
  ```

- [ ] **Certificate Manager Ready**
  ```bash
  kubectl get pods -n cert-manager
  kubectl get clusterissuer
  # Should show at least 1 ClusterIssuer (self-signed or CA)
  ```

- [ ] **Ingress Controller Ready**
  ```bash
  kubectl get pods -n kube-system | grep traefik
  kubectl get svc -n kube-system traefik
  # traefik pod should be Running; LoadBalancer IP should be assigned
  ```

---

## Tier 1: System Services (Core Infrastructure)

### Cert-Manager Validation

```bash
# Check deployment
kubectl get deployment -n cert-manager
# Expected: cert-manager, cert-manager-cainjector, cert-manager-webhook (all Running)

# Verify webhook
kubectl get validatingwebhookconfigurations | grep cert-manager

# Test certificate issuance
kubectl apply -f - <<EOF
apiVersion: cert-manager.io/v1
kind: Certificate
metadata:
  name: test-cert
  namespace: cert-manager
spec:
  secretName: test-tls
  issuerRef:
    name: selfsigned-issuer
    kind: Issuer
  commonName: test.example.com
---
apiVersion: cert-manager.io/v1
kind: Issuer
metadata:
  name: selfsigned-issuer
  namespace: cert-manager
spec:
  selfSigned: {}
EOF

# Verify secret was created
kubectl get secret test-tls -n cert-manager -o jsonpath='{.data.tls\.crt}' | base64 -d | openssl x509 -text -noout
kubectl delete certificate test-cert issuer selfsigned-issuer -n cert-manager
```

### MetalLB Validation

```bash
# Check deployment
kubectl get pods -n metallb-system

# Verify address pool is loaded
kubectl get configmap -n metallb-system config -o yaml | grep -A 5 "address-pools"

# Test by creating a LoadBalancer service
kubectl apply -f - <<EOF
apiVersion: v1
kind: Service
metadata:
  name: test-lb
  namespace: default
spec:
  type: LoadBalancer
  ports:
  - port: 8080
    targetPort: 80
  selector:
    app: nginx
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx
spec:
  replicas: 1
  selector:
    matchLabels:
      app: nginx
  template:
    metadata:
      labels:
        app: nginx
    spec:
      containers:
      - name: nginx
        image: nginx:alpine
EOF

# Wait for LoadBalancer IP assignment (should be from 192.168.1.200-250)
kubectl get svc test-lb --watch
# Ctrl+C after IP appears

# Cleanup
kubectl delete deployment nginx svc test-lb
```

### Longhorn Storage Validation

```bash
# Check deployment
kubectl get pods -n longhorn-system
kubectl get storageclass longhorn

# Verify default StorageClass
kubectl get storageclass --field-selector metadata.name=longhorn

# Test PVC creation
kubectl apply -f - <<EOF
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: test-storage
spec:
  accessModes: ["ReadWriteOnce"]
  storageClassName: longhorn
  resources:
    requests:
      storage: 2Gi
EOF

# Wait for Bound status
kubectl get pvc test-storage --watch
kubectl delete pvc test-storage
```

---

## Tier 2: Core Identity Services

### Samba AD Validation

```bash
# Check pod status
kubectl get pods -n identity -l app=samba-ad

# Verify volume mounting
kubectl describe pod -n identity -l app=samba-ad | grep "Mounts:" -A 5

# Test LDAP connectivity
kubectl run -it --rm ldap-test --image=alpine --restart=Never -- \
  apk add openldap-clients && \
  ldapsearch -H ldap://samba-ad.identity.svc:389 -D "cn=admin,dc=example,dc=com" -w password -b "dc=example,dc=com"

# Check logs for errors
kubectl logs -n identity -l app=samba-ad --tail=50
```

### Authentik Validation

```bash
# Check pod status
kubectl get pods -n identity -l app=authentik

# Verify database connectivity
kubectl logs -n identity deployment/authentik-postgres --tail=20

# Check service status
kubectl get svc -n identity authentik
# Should show ClusterIP or LoadBalancer type

# Test web UI accessibility
AUTHENTIK_IP=$(kubectl get svc -n identity authentik -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
curl -k https://$AUTHENTIK_IP/api/v3/admin/version

# Default credentials (change immediately in production)
# Username: akadmin
# Password: (from SECRET or logs)
```

---

## Tier 3: Applications Layer

### Monitoring (Prometheus + Grafana + Wazuh)

#### Prometheus

```bash
# Check deployment
kubectl get pods -n monitoring -l app=prometheus
kubectl get svc -n monitoring prometheus

# Access web UI
PROM_IP=$(kubectl get svc -n monitoring prometheus -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
curl http://$PROM_IP:9090/api/v1/targets

# Verify scrape targets are healthy
# Navigate to http://$PROM_IP:9090/targets
```

#### Grafana

```bash
# Check deployment
kubectl get pods -n monitoring -l app=grafana
kubectl get svc -n monitoring grafana

# Access web UI
GRAFANA_IP=$(kubectl get svc -n monitoring grafana -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
echo "http://$GRAFANA_IP:3000"
# Default credentials: admin/admin (CHANGE IMMEDIATELY)

# Verify data source connections
curl -s -u admin:admin http://$GRAFANA_IP:3000/api/datasources | jq '.[] | {name, url, health}'
```

#### Wazuh

```bash
# Check deployment
kubectl get pods -n monitoring -l app=wazuh

# Access Wazuh UI
WAZUH_IP=$(kubectl get svc -n monitoring wazuh -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
curl -k https://$WAZUH_IP:443

# Verify agent connectivity
kubectl exec -it pod/wazuh-manager -n monitoring -- \
  /var/ossec/bin/agent_control -l
```

### Backup (MinIO + Velero)

#### MinIO Validation

```bash
# Check pod status
kubectl get pods -n backup -l app=minio
kubectl get svc -n backup minio

# Verify storage
kubectl exec -it pod/minio-0 -n backup -- mc ls minio/backup-uss

# Access MinIO UI
MINIO_IP=$(kubectl get svc -n backup minio -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
echo "http://$MINIO_IP:9001"
# Default credentials: minioadmin/minioadmin (CHANGE IMMEDIATELY)
```

#### Velero Validation

```bash
# Install Velero CLI (if not present)
wget https://github.com/vmware-tanzu/velero/releases/download/v1.12.2/velero-v1.12.2-linux-amd64.tar.gz
tar xvf velero-v1.12.2-linux-amd64.tar.gz
sudo mv velero-v1.12.2-linux-amd64/velero /usr/local/bin/

# Check Velero deployment
kubectl get pods -n velero
velero version

# Verify backup storage location
velero backup-location get

# Test backup (should complete in <5 min)
velero backup create test-backup --wait
velero backup get test-backup
velero backup logs test-backup

# Cleanup
velero backup delete test-backup --confirm
```

### Collaboration (Zimbra)

```bash
# Check pod status
kubectl get pods -n apps -l app=zimbra
kubectl get svc -n apps zimbra

# Verify storage mounts
kubectl describe pod -n apps -l app=zimbra | grep Mounts -A 10

# Access Zimbra UI
ZIMBRA_IP=$(kubectl get svc -n apps zimbra -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
echo "https://$ZIMBRA_IP:7071/zimbraAdmin"
# Admin port: 7071 (default credentials: admin/password)

# Check mail services
kubectl exec -it pod/zimbra-0 -n apps -- \
  sudo -u zimbra /opt/zimbra/bin/zmcontrol status

# Test IMAP/SMTP
kubectl run -it --rm mail-test --image=alpine --restart=Never -- \
  apk add netcat-openbsd && \
  nc -zv zimbra.apps.svc 143  # IMAP
  nc -zv zimbra.apps.svc 25   # SMTP
```

---

## Tier 4: Rancher Management (Optional)

```bash
# Check deployment
kubectl get pods -n cattle-system

# Access Rancher UI
RANCHER_IP=$(kubectl get svc -n cattle-system rancher -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
echo "https://$RANCHER_IP"

# Retrieve initial bootstrap password
kubectl get secret -n cattle-system bootstrap-password \
  -o jsonpath='{.data.password}' | base64 -d
# (or check logs: kubectl logs deployment/rancher -n cattle-system)

# Add local cluster to Rancher management
# (Done via Rancher UI or kubectl apply with cluster API)
```

---

## Common Issues & Resolutions

### Issue: Pod Stuck in Pending

**Symptom:**
```bash
kubectl get pods -n <namespace>
# Pod shows STATUS: Pending for >5 min
```

**Diagnosis:**
```bash
kubectl describe pod <pod-name> -n <namespace>
# Check Events section for: ImagePull, Storage, ResourceQuota, Node

# Common causes:
# 1. PVC not Bound: kubectl get pvc -n <namespace>
# 2. Node resource exhaustion: kubectl top nodes
# 3. Invalid image: kubectl describe pod | grep Image
```

**Resolution:**
```bash
# If storage issue:
kubectl apply -f - <<EOF
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: longhorn
  annotations:
    storageclass.kubernetes.io/is-default-class: "true"
provisioner: driver.longhorn.io
EOF

# If resource issue, add more worker nodes or remove low-priority workloads
kubectl get pods -A --sort-by=.spec.nodeName
```

### Issue: CrashLoopBackOff or Error

**Diagnosis:**
```bash
kubectl logs <pod-name> -n <namespace> --tail=50
kubectl logs <pod-name> -n <namespace> -p  # Previous logs
kubectl describe pod <pod-name> -n <namespace>
```

**Common Causes:**
- Missing config/secrets: `kubectl get secret,configmap -n <namespace>`
- Permission denied: `kubectl get pvc,role,rolebinding -n <namespace>`
- Port conflicts: `kubectl logs <pod> | grep -i port`

**Resolution:**
```bash
# Restart pod (often resolves temporary issues)
kubectl delete pod <pod-name> -n <namespace>
# Pod will be auto-recreated

# If persistent, check manifests in kubernetes/ directory
# Verify: passwords, IP addresses, resource requests
```

### Issue: LoadBalancer Service Stuck in Pending

**Symptom:**
```bash
kubectl get svc
# SERVICE has EXTERNAL-IP: <pending>
```

**Diagnosis:**
```bash
kubectl describe svc <service-name>
# Check Events section

kubectl get pods -n metallb-system
# Check MetalLB controller/speaker pods are Running

kubectl get configmap -n metallb-system config -o yaml
# Verify address pool matches your network
```

**Resolution:**
```bash
# Verify MetalLB address pool
kubectl patch configmap config -n metallb-system --type merge -p '
{
  "data": {
    "config": "address-pools:\n- name: default\n  protocol: layer2\n  addresses:\n  - 192.168.1.200-192.168.1.250\n"
  }
}'

# Or restart MetalLB controller
kubectl rollout restart deployment controller -n metallb-system
```

### Issue: Certificate Not Renewing

**Symptom:**
```bash
kubectl get certificate -A
# Certificate shows conditions: Ready=False or Issuing=True
```

**Diagnosis:**
```bash
kubectl describe certificate <cert-name> -n <namespace>
# Check for expiration date and issuer reference

kubectl get certificaterequest -n <namespace>
# Should show CertificateRequest in Ready state
```

**Resolution:**
```bash
# Manual renewal
kubectl delete certificate <cert-name> -n <namespace>
# Certificate will be auto-recreated

# Or force renewal
kubectl annotate certificate <cert-name> -n <namespace> \
  cert-manager.io/issue-temporary-certificate=true --overwrite
```

### Issue: Node NotReady

**Symptom:**
```bash
kubectl get nodes
# Node shows STATUS: NotReady
```

**Diagnosis (on the node):**
```bash
sudo systemctl status rke2-server  # or rke2-agent
sudo journalctl -u rke2-server -n 100
sudo systemctl restart rke2-server

# Check kubelet
sudo systemctl status rke2-kubelet
systemctl cat rke2-server | grep ARGS
```

**Common Causes:**
- Disk space exhausted: `df -h /var/lib/rancher`
- Memory pressure: `free -h`
- Network partition: `ip route`

**Resolution:**
```bash
# Clean up disk space
sudo docker system prune -a  # if using Docker
sudo podman system prune -a  # if using Podman

# Restart RKE2
sudo systemctl restart rke2-server

# Monitor recovery
kubectl get nodes --watch
```

### Issue: PVC Not Binding to Longhorn

**Symptom:**
```bash
kubectl get pvc
# PVC shows STATUS: Pending
```

**Diagnosis:**
```bash
kubectl describe pvc <pvc-name> -n <namespace>
# Look for "waiting for first consumer" or storage class issues

kubectl get storageclass
# Verify longhorn StorageClass exists and is default

kubectl get pods -n longhorn-system
# Check for errors in manager/controller/driver pods
```

**Resolution:**
```bash
# Verify StorageClass
kubectl apply -f - <<EOF
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: longhorn
  annotations:
    storageclass.kubernetes.io/is-default-class: "true"
provisioner: driver.longhorn.io
allowVolumeExpansion: true
parameters:
  numberOfReplicas: "3"
EOF

# Restart Longhorn manager
kubectl rollout restart deployment longhorn-manager -n longhorn-system

# Re-create PVC
kubectl delete pvc <pvc-name> -n <namespace>
kubectl apply -f - <<EOF
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: <pvc-name>
  namespace: <namespace>
spec:
  accessModes: ["ReadWriteOnce"]
  storageClassName: longhorn
  resources:
    requests:
      storage: 10Gi
EOF
```

---

## Performance Checks

### Node Resource Usage

```bash
# CPU/Memory per node
kubectl top nodes

# CPU/Memory per pod
kubectl top pods -A | sort -k3 -nr | head -20  # top CPU consumers
kubectl top pods -A | sort -k4 -nr | head -20  # top memory consumers
```

### Storage Usage

```bash
# PV usage (if supported by driver)
kubectl get pv -o json | jq '.items[] | {name: .metadata.name, size: .spec.capacity.storage}'

# Longhorn disk usage
kubectl exec -it pod/longhorn-manager-0 -n longhorn-system -- \
  longhorn-manager -json disks
```

### Network Connectivity

```bash
# MTU/latency checks
kubectl run -it --rm net-test --image=alpine --restart=Never -- \
  apk add iputils ipconfig && \
  ping -c 1 -s 8972 kubernetes.default  # Test fragmentation
```

---

## Sign-Off Checklist

Before considering deployment complete:

- [ ] All nodes show `STATUS: Ready`
- [ ] All system pods (cert-manager, metallb, longhorn) are `Running`
- [ ] All application pods (authentik, prometheus, grafana, zimbra) are `Running`
- [ ] All PVCs show `STATUS: Bound`
- [ ] Test pod successfully created and mounted storage
- [ ] LoadBalancer service received external IP
- [ ] Certificate was automatically issued by cert-manager
- [ ] Prometheus is scraping metrics
- [ ] Grafana dashboards display data
- [ ] Velero backup completed successfully
- [ ] Rancher UI is accessible
- [ ] SSH keys rotated and documented
- [ ] Initial admin passwords changed on all services
- [ ] Backup schedule is configured
- [ ] DNS records are set and resolving

---

**Status:** Ready for Production  
**Last Updated:** 2024  
**Next:** See [OPERATIONAL_RUNBOOK.md](OPERATIONAL_RUNBOOK.md) for day-2 operations
