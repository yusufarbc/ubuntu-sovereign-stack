# Documentation Index

## Abstract
Enterprise workloads are increasingly bound to hyperscale clouds and their extraterritorial control planes (e.g., CLOUD Act). The Ubuntu Sovereign Stack provides an on-prem, open-source reference architecture that keeps identity, collaboration, and observability fully under organizational custody. It uses Ubuntu Server LTS + Kubernetes (RKE2) managed by Rancher, Podman as a daemonless runtime, Samba 4 + Authentik for identity, Zimbra for mail, and Wazuh/Prometheus/Grafana for security and metrics. Persistent storage (Longhorn), networking (MetalLB), PKI (Cert-Manager), and backups (Velero + MinIO) complete the platform. Client flexibility is preserved via ten Ubuntu-based desktops tuned to user personas.

## Core Strategy Documents
* **[Strategic Implementation Plan](PROJECT_PROPOSAL.md):** Complete vision, architecture, client strategy, WBS, risk management, deliverables, and success criteria.
* **[Background & Context Analysis](BACKGROUND_CLOUD_FIRST.md):** Cloud-First risks, CLOUD Act exposure, and system layer gap analysis.
* **[Comparative Analysis](COMPARATIVE_ANALYSIS.md):** Ubuntu Sovereign Stack vs. Microsoft ecosystem; evaluation methodology and metrics.

## Deployment & Operations
* **[Quick Start Guide](QUICKSTART.md):** Get up and running in 2 hours (local or lab cluster).
* **[Cluster Setup Guide](CLUSTER_SETUP_GUIDE.md):** Step-by-step production deployment for RKE2, system layer, core services, and apps.
* **[Deployment Order & Dependencies](DEPLOYMENT_ORDER.md):** Manifest execution sequence, phase breakdown, validation checkpoints.
* **[Deployment Verification Checklist](DEPLOYMENT_CHECKLIST.md):** Post-installation validation, troubleshooting guide, performance checks, and sign-off procedures.
* **[Operational Runbook](OPERATIONAL_RUNBOOK.md):** Day-2 operations: scaling, maintenance, rotations, backup/restore drills.
* **[Security Hardening](SECURITY_HARDENING.md):** Network policies, RBAC, pod security, image policy, secrets, backup/DR controls.
* **[Audit Report](AUDIT_REPORT.md):** Gap analysis and remediation summary.

## Technical Architecture
* **[System Architecture](ARCHITECTURE.md):** Topology, cluster design, storage, networking.
* **[Tools & Components](TOOLS.md):** Rationale for Podman, RKE2, Authentik, Longhorn, MetalLB, Velero; includes "Flexible 10" client strategy.
