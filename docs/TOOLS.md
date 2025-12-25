# Tools & Components

## Core Stack (Server)

| Category | Component | Key Features & Rationale |
| --- | --- | --- |
| Operating System | Ubuntu Server LTS | 5y security updates, broad ecosystem, HWE kernel support. |
| Orchestration | Kubernetes (RKE2) + Rancher | FIPS-capable distro; Rancher for UI, RBAC, upgrades, multi-cluster. |
| Container Runtime | Podman | Daemonless/rootless; Docker explicitly excluded to reduce attack surface. |
| Identity | Samba 4 AD | AD-compatible source of truth; avoids CAL licensing. |
| SSO / MFA | Authentik | OIDC/SAML with WebAuthn/TOTP; bridges legacy LDAP/AD. |
| Collaboration | Zimbra CE + ClamAV + SpamAssassin | Exchange/O365 alternative with built-in AV/AS. |
| SIEM / XDR | Wazuh | Centralized detection/response, log correlation for OS/K8s/apps. |
| Metrics / Viz | Prometheus + Grafana | De facto standard for metrics and dashboards. |
| Storage (CSI) | Longhorn | Distributed block storage; CSI snapshots for PVCs. |
| Load Balancing | MetalLB (L2) | Bare-metal service publishing via ARP/NDP pools. |
| PKI | Cert-Manager | Automated cert issuance (self-signed or internal CA). |
| Backup | Velero + MinIO (S3) | Cluster + PVC backups with kopia/CSI to an on-prem S3 target. |

## Client Stack: The "Flexible 10" Model

### Philosophy
One-size-fits-all desktops create friction. A persona-based catalog of Ubuntu derivatives reduces resistance, speeds migration from Windows, and keeps support predictable.

### The 10 Distributions

| # | Distribution | Target Persona | Why This Choice |
| --- | --- | --- | --- |
| 1 | Ubuntu Desktop | Standard corporate user | Canonical baseline; stable, broad hardware support. |
| 2 | Linux Mint (Cinnamon) | Office / Admin | Windows-like workflow; minimal retraining. |
| 3 | Zorin OS | Management / Exec | Premium, polished UI akin to Win11/macOS. |
| 4 | Pop!_OS | Engineers / Devs | Tiling, good GPU support, dev tooling focus. |
| 5 | Kubuntu | Power users | KDE customization for advanced users. |
| 6 | Xubuntu | Legacy hardware | XFCE lightweight; extends life of old assets. |
| 7 | Lubuntu | Thin clients | Ultra-light LXQt for low-resource endpoints. |
| 8 | Ubuntu MATE | Traditionalists | Classic desktop metaphor; low learning curve. |
| 9 | elementary OS | Kiosk / Public | Opinionated, focused UI; locked-down feel. |
| 10 | KDE Neon | R&D / Explorers | Latest KDE stack for experimentation. |

### Migration & Training Plan

**Phase 1: Discover & Map**
* Inventory Windows-only apps; classify: **Replace** (web/Linux alt), **Emulate** (Wine/Proton), **Virtualize** (VDI/local VM).
* Map personas to one of the 10 distros; pre-bake configs (browser, mail, VPN, printers).

**Phase 2: Pilot**
* Start with Linux Mint for office and Pop!_OS for engineers (5–10 users each).
* Provide cheat sheets and a 30-minute onboarding ("where is file manager/print/VPN").

**Phase 3: Rollout & Support**
* Stage deployments by persona; enforce common SSO (Authentik) and mail (Zimbra) to simplify helpdesk.
* Track satisfaction/issue metrics; adjust distro choice only if blocking issues persist.

**Phase 4: Optimize**
* Harden telemetry stance (disable vendor data sharing); push consistent security baselines via Ansible.
* Refresh low-end fleets with Lubuntu/Xubuntu; reserve KDE Neon for labs, not broad rollout.

> This selection prioritizes open-source licensing, data sovereignty, and operational maturity over “cloud convenience.”
