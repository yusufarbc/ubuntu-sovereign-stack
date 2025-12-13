# Tools & Components

## Core Components Selection Rationale

### Operating System: Ubuntu Server LTS
**Why:** Reliability and Support.
Canonical provides 5 years of free security updates for LTS releases. This eliminates the need for frequent `dist-upgrades` and ensures a stable production environment. It serves as the ubiquitous standard for Linux server deployments.

### Orchestration: Kubernetes with Rancher
**Why:** Modern Management & Abstraction.
While Kubernetes handles the scheduling, **Rancher** provides the management layer that rivals proprietary clouds. It simplifies upgrades, access control, and observability, making the complexity of K8s manageable for typical IT teams.

### Container Runtime: Podman
**Why:** Security (Rootless/Daemonless).
Unlike Docker, which requires a central daemon running as root (a single point of failure and security risk), **Podman** runs containers as independent processes. This "Daemonless" architecture is a critical security requirement for a sovereign stack.

## Application Stack

### Identity: Authentik & Samba 4
*   **Samba 4 Active Directory**: Chosen for its robust compatibility with the Active Directory protocol. It allows the system to support Windows clients (if necessary) and standard LDAP integrations without Microsoft licensing.
*   **Authentik**: A modern, open-source Identity Provider (IdP). It bridges the legacy world (LDAP) with modern web standards (OIDC/SAML) and enforces policies like **WebAuthn/TOTP MFA**, which Samba cannot do natively on its own.

### Collaboration: Zimbra Community Edition
**Why:** Feature Parity with Exchange.
Zimbra offers a complete suite (Email, Calendar, Contacts, File Sharing) with a mature Web UI. It is one of the few open-source solutions that effectively replaces the full functionality of Microsoft Exchange + Outlook Web App.
*   **Security Integration**: Includes **ClamAV** (Antivirus) and **SpamAssassin** (Antispam) out of the box.

### Security: Wazuh (SIEM/XDR)
**Why:** Unified Security Visibility.
Wazuh serves as the "Digital Immune System". It correlates logs from the OS, Kubernetes, and Applications to detect anomalies (e.g., Brute Force attacks, File Integrity changes). It replaces solutions like Microsoft Sentinel.

### Vulnerability Management: OpenVAS
**Why:** Continuous Auditing.
OpenVAS (Greenbone) provides the "Offensive" perspective, scanning the network for known CVEs and misconfigurations, ensuring the stack remains hardened against new threats.

### Observability: Prometheus & Grafana
**Why:** Industry Standard Monitoring.
Replaces proprietary monitoring tools (like SCOM). Prometheus pulls metrics; Grafana visualizes them. This pair provides deep insight into resource usage (CPU/RAM) and application health.
