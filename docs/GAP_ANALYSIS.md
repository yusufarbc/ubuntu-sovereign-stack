# Ubuntu Sovereign Stack - Gap Analysis

## Current Status
We have successfully scaffolded:
1.  **Core OS & Runtime:** Ubuntu + RKE2 + Podman.
2.  **Application Layer:** Zimbra, Wazuh, Authentik, Samba.
3.  **Observability:** Prometheus, Grafana.

## Critical Gaps for "Enterprise-Grade" Prototype
To make this thesis project a **functional** and **defendable** sovereign cloud prototype on **Bare Metal**, the following "System Layer" components are currently missing:

### 1. Persistent Storage (The "State" Problem)
*   **Missing:** A distributed block storage solution.
*   **Why:** Kubernetes on Bare Metal does not have a default StorageClass (unlike AWS EBS or Azure Disk).
*   **Impact:** StatefulSets (Samba, Zimbra, Postgres, Elasticsearch/Wazuh) will **fail to start** because their `VolumeClaims` cannot be provisioned.
*   **Solution:** Implement **Longhorn** (Cloud-Native distributed storage, highly recommended for Rancher/RKE2).

### 2. Networking & Load Balancing (The "Access" Problem)
*   **Missing:** A Layer 2 Load Balancer.
*   **Why:** `NodePort` is not suitable for production. We need dedicated IPs for services (e.g., Mail, Web).
*   **Impact:** Accessing services will require specifying ports (e.g., `server-ip:30443`), which breaks the "Enterprise" experience.
*   **Solution:** Implement **MetalLB**.

### 3. Rancher Management Platform
*   **Missing:** The actual installation of the Rancher UI.
*   **Why:** The Vision specifies "Managed by Rancher". We installed RKE2 (the cluster), but not Rancher (the dashboard).
*   **Solution:** Add a Helm Chart wrapper for **Rancher Manager**.

### 4. Ingress & TLS (The "Security" Problem)
*   **Missing:** Ingress Controller configuration and Certificate Management.
*   **Why:** Secure HTTPS access is non-negotiable for a security-focused thesis.
*   **Solution:** Configure **Ingress-Nginx** (included in RKE2 but needs config) and add **Cert-Manager** for internal/self-signed certificates.

### 5. Backup & Disaster Recovery (The "Sovereignty" Guarantee)
*   **Missing:** A backup mechanism.
*   **Why:** True sovereignty implies you can recover your data if hardware fails.
*   **Solution:** Add **Velero** manifests.

## Recommended Action Plan
1.  Create `kubernetes/system/` directory.
2.  Add manifests/scripts for:
    *   `longhorn.yaml`
    *   `metallb.yaml`
    *   `rancher-install.sh` (or Helm values)
    *   `cert-manager.yaml`
