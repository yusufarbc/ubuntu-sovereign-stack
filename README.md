# Ubuntu Sovereign Stack

## Abstract
Enterprise workloads increasingly depend on hyperscale clouds governed by extraterritorial laws (e.g., the U.S. CLOUD Act). Even when data resides in-region, vendor-operated control planes and encryption keys can be compelled for disclosure. The Ubuntu Sovereign Stack is an on-premise, open-source reference architecture that keeps identity, collaboration, and observability fully under organizational custody. It pairs Ubuntu Server LTS with Kubernetes (RKE2) and Rancher for cluster governance, Podman for daemonless containers, Samba 4 + Authentik for identity, Zimbra for mail/collaboration, and Wazuh/Prometheus/Grafana for security and metrics. Client flexibility is preserved via ten Ubuntu-based desktops tuned to user personas, minimizing lock-in while sustaining manageability.

## Architecture at a Glance
| Layer | Choice / Rationale |
| --- | --- |
| Server OS | Ubuntu Server LTS (5y support, HWE, broad ecosystem) |
| Orchestration | Kubernetes (RKE2) managed by Rancher (UI, RBAC, lifecycle) |
| Container Runtime | Podman (daemonless, rootless; Docker explicitly excluded) |
| Identity | Samba 4 AD (source of truth) + Authentik (SSO/MFA) |
| Collaboration | Zimbra CE + ClamAV + SpamAssassin |
| Security/Observability | Wazuh (SIEM/XDR), Prometheus + Grafana (metrics/dashboards) |
| Storage/Networking | Longhorn (CSI), MetalLB (L2 LB), Cert-Manager (PKI) |
| Management | Ansible for provisioning; Rancher for day-2 K8s ops |
| Client Strategy | 10 Ubuntu-based distros aligned to roles (below) |

### The “Flexible 10” Client Strategy
1) Ubuntu Desktop (standard) • 2) Linux Mint (office) • 3) Zorin OS (management) • 4) Pop!_OS (engineering) • 5) Kubuntu (power users) • 6) Xubuntu (legacy HW) • 7) Lubuntu (thin) • 8) Ubuntu MATE (traditional) • 9) elementary OS (kiosk/public) • 10) KDE Neon (R&D).

## Quick Start (Provision Ubuntu servers with Ansible)
Prereqs: Ansible control node with SSH key access; inventory `infrastructure/hosts.ini` defining `[master]` and `[worker]`.

```bash
# Install Ansible deps
sudo apt update && sudo apt install -y ansible git

# Run base provisioning (Podman + RKE2 server on all targets; adjust roles as needed)
cd infrastructure
ansible-playbook -i hosts.ini setup-rke2.yml

# After install, copy /etc/rancher/rke2/rke2.yaml from master to your kubeconfig path.
# Deploy system add-ons: Longhorn, MetalLB, Cert-Manager, Rancher helm chart.
# Apply application manifests under kubernetes/ (core, apps, monitoring).
```

## Repository Layout
- .github/ (CI/CD, issue templates)
- docs/ (thesis docs, architecture, gap/risk, runbooks)
- infrastructure/ (Ansible for RKE2/OS prep)
- kubernetes/
  - core/ (Samba AD, Authentik, identity services)
  - apps/ (Zimbra, Wazuh, collaboration/security apps)
  - monitoring/ (Prometheus, Grafana)
- website/ (static landing page)

## Key Documentation
- [QUICKSTART.md](QUICKSTART.md): Local and 3-node lab setup in under 2 hours.
- [docs/CLUSTER_SETUP_GUIDE.md](docs/CLUSTER_SETUP_GUIDE.md): Production deployment (RKE2, system layer, identity, apps).
- [docs/DEPLOYMENT_ORDER.md](docs/DEPLOYMENT_ORDER.md): Required manifest sequence and validation checkpoints.
- [docs/DEPLOYMENT_CHECKLIST.md](docs/DEPLOYMENT_CHECKLIST.md): Post-install validation, troubleshooting, sign-off.
- [docs/OPERATIONAL_RUNBOOK.md](docs/OPERATIONAL_RUNBOOK.md): Day-2 operations (scaling, maintenance, rotations, restore drills).
- [docs/SECURITY_HARDENING.md](docs/SECURITY_HARDENING.md): Network policies, RBAC, pod security, image policy, secrets.
- [AUDIT_REPORT.md](AUDIT_REPORT.md): Gap analysis and remediation summary.
