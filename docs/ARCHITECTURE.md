# System Architecture

## Overview
The proposed architecture is a holistic **On-Premise Sovereign Cloud** built on **Ubuntu Server LTS**. It is designed to replace the traditional Microsoft ecosystem (Windows Server/Hyper-V/Active Directory) with a modern, container-based open-source stack.

## Physical Layer
The foundation consists of **3 Physical Servers** configured as a High-Availability (HA) cluster:
*   **Operating System:** Ubuntu Server 22.04/24.04 LTS.
*   **Configuration:** 1 Control Plane (Master) node, 2 Worker nodes (or 3 HA Master/Worker hybrid nodes for resilience).
*   **Networking:** Private network segmentation behind a physical Firewall (e.g., pfSense/OPNsense) with strict egress rules.
*   **Storage:** Local SSDs aggregated via **Longhorn** for distributed persistent block storage.

## Orchestration Layer: Kubernetes & Rancher
Instead of legacy virtualization, the system uses **Kubernetes (RKE2)** managed by **Rancher**.
*   **RKE2**: Used for its FIPS compliance and secure-by-default configuration.
*   **Rancher:** Provides the "Single Pane of Glass" for lifecycle management, RBAC, and workload visibility.
*   **Runtime:** **Podman** is mandated as the container engine (Daemonless/Rootless) to mitigate security risks associated with the Docker daemon.

## Logical Architecture & Namespaces

Services are logically isolated into Kubernetes Namespaces for security and resource management:

| Namespace | Services | Role & Configuration |
| :--- | :--- | :--- |
| `infrastructure` | **Samba 4 AD**<br>**Authentik** | **Core Identity:** AD serves as the "Source of Truth". Authentik syncs via LDAP to provide SSO (SAML/OIDC) and MFA. |
| `collaboration` | **Zimbra Suite** | **Business Apps:** Email, Calendar, Contacts. Data persists on Longhorn volumes; secured by ClamAV/SpamAssassin. |
| `security` | **Wazuh Manager** | **Defensive Ops:** Central SIEM for log correlation. |
| `monitoring` | **Prometheus**<br>**Grafana** | **Observability:** Scrapes metrics from nodes/pods and visualizes them via accessible dashboards (e.g., `grafana.sovereign.lan`). |

## Networking & Integration
*   **Ingress Controller**: NGINX Ingress handles TLS termination and routing (Layer 7).
*   **Load Balancer**: MetalLB provides Layer 2 IP assignment for the Ingress Controller.
*   **DNS Strategy**: Split-DNS configuration where internal services (`*.sovereign.lan`) resolve to the MetalLB VIP.

## Backup & Disaster Recovery
*   **Strategy**: 3-2-1 Rule.
*   **Implementation**:
    *   **Longhorn Snapshots**: Instant recovery points for volumes.
    *   **Velero**: Backs up Kubernetes manifests to S3-compatible on-prem storage (e.g., MinIO or QNAP NAS).
    *   **Physical NAS**: QNAP device receives nightly cold storage dumps.
