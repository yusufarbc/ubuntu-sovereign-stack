# Tools & Components

## Core Components Selection Rationale

| Category | Component | Key Features & Rationale |
| :--- | :--- | :--- |
| **Operating System** | **Ubuntu Server LTS** | **Reliability:** 5 years of free security updates. Ubiquitous standard for Linux server deployments. |
| **Orchestration** | **Kubernetes (RKE2)** | **Modern Management:** Managed by **Rancher** to rival proprietary clouds. Simplifies upgrades and access control. |
| **Runtime** | **Podman** | **Security:** Daemonless and rootless architecture eliminates the Docker daemon attack vector. |
| **Directory** | **Samba 4 AD** | **Compatibility:** Drop-in replacement for Active Directory. Supports Windows/Linux clients without CALs. |
| **IAM / SSO** | **Authentik** | **Modern Identity:** Bridges LDAP with OIDC/SAML. Enforces **WebAuthn/TOTP MFA** policy system-wide. |
| **Email / Collab** | **Zimbra CE** | **Exchange Alternative:** Full suite (Email, Calendar, Tasks). Includes ClamAV (Anti-virus) and SpamAssassin. |
| **SIEM / XDR** | **Wazuh** | **Visibility:** Correlates logs from OS, K8s, and Apps to detect anomalies (Digital Immune System). |

| **Observability** | **Prometheus + Grafana** | **Metrics:** Industry standard for resource usage and application health monitoring. |

> **Note:** This selection prioritizes open-source licenses, data sovereignty, and enterprise-grade maturity over "bleeding edge" features.
