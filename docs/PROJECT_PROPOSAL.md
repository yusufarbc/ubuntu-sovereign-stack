# Project Proposal: Ubuntu-Based Open-Source Sovereign Enterprise Architecture

> *   **Server:** Kubernetes (Rancher)
> *   **IAM/MFA:** Authentik
> *   **Directory:** Samba AD + Zimbra CE
> *   **Client:** Ubuntu LTS and Derivatives

## Abstract
This project presents a fully on-premise, Ubuntu LTS-based open-source enterprise architecture designed to reduce cloud dependence and strengthen data sovereignty. Server-side services run as containers on Kubernetes managed by Rancher; identity and MFA are provided by Authentik; directory and mail services are implemented with Samba 4 Active Directory and Zimbra Community Edition. Security and observability layers rely on Wazuh (SIEM), OpenVAS (vulnerability scanning), and Prometheus + Grafana (metrics and alerting). The network perimeter is protected by physical firewalls, and backups are handled by physical appliances (e.g., QNAP NAS). The initiative aims to produce comparative evidence—against Microsoft’s cloud-first ecosystem—across TCO, security, usability, and portability, with a primary legal focus on data residency and sovereignty.

## 1. Introduction
Accelerated digitalization in the public and private sectors has made cloud computing platforms attractive; however, it has also brought critical issues such as **data sovereignty**, privacy, and **Total Cost of Ownership (TCO)** to the forefront. Regulations like the **US CLOUD Act** increase the risk of data being subject to foreign legal demands. Specifically within the Microsoft ecosystem, steps such as the Azure-centric evolution of Windows Server 2019–2025 and the deprecation of WSUS are driving organizations towards hybrid/cloud solutions. This project evaluates an open-source, on-premise architecture against these risks using technical and managerial metrics.

## 2. Background – Microsoft’s Cloud-First Strategy vs. On-Prem Trends
*   **Windows Server 2019:** Focus on sustaining classic on-prem workloads.
*   **Windows Server 2022:** Introduction of Azure Edition, Hotpatch, SMB over QUIC, and Azure Extended Networking – signaling a shift to hybrid/cloud integrations.
*   **Windows Server 2025:** While including AD DS/LAPS improvements, it significantly emphasizes Azure Local/Arc/Entra ID integrations.
*   **WSUS Deprecation:** In 2024, WSUS was deprecated; investment in new features has stopped, and customers are being redirected to Azure Update Manager, Intune, or Autopatch.
*   **Licensing Dynamics:** Core-based licensing and subscription models create long-term budget pressure.

This trend renders on-premise, open-source alternatives strategic for organizations focused on **sovereignty** and **cost control**.

> *For a deeper dive into these trends, see the [Background Analysis: Cloud-First Strategy vs. Data Sovereignty](BACKGROUND_CLOUD_FIRST.md).*

## 3. Purpose and Research Questions
**Purpose:** To design a manageable and reproducible Ubuntu-based open-source enterprise architecture that reduces dependence on cloud providers and strengthens data sovereignty, and to benchmark it against the Microsoft ecosystem.

**Research Questions:**
1.  **TCO Advantage:** What is the cost benefit compared to proprietary licensing?
2.  **Security/Compliance:** What is the level of security (SSO/MFA/SIEM/Vulnerability) achieved?
3.  **Usability & Manageability:** How do Rancher/Kubernetes improve the management experience?
4.  **Data Sovereignty:** How are legal risks regarding data residency reduced?

## 4. Scope and System Architecture
*   **Server Side:** A Kubernetes cluster consisting of 1 Control Plane (Master) + 2 Worker nodes on 3 physical servers. Lifecycle management, RBAC, and observability via Rancher. All services are container-based; versioned with Helm/Manifests; CI/CD integratable.
    *   *See [System Architecture](ARCHITECTURE.md) for detailed node and network topology.*
*   **Client Side:** Ubuntu LTS derivatives (Linux Mint, Zorin OS, etc.) selected based on user experience and deployed via phased pilots.
    *   *See [Client Strategy](CLIENT_STRATEGY.md) for the "Flexible 10" model.*
*   **Network Security:** Physical firewall; network segmentation/VPN; IDS/IPS integration options.
*   **Backup:** Snapshot/versioning on QNAP NAS; adhering to the 3-2-1 rule with periodic recovery drills.

### 4.1 Open Source Components
*   *See [Tools & Components](TOOLS.md) for detailed definitions and selection rationale.*

| Service Area | Component | Key Features |
| :--- | :--- | :--- |
| **OS** | Ubuntu LTS (Server) + Mint/Zorin (Client) | LTS stability, vast package ecosystem, user-friendly desktop. |
| **Cluster Mgmt** | Kubernetes + Rancher | Multi-cluster GUI, RBAC, Catalog, scaling/backup workflows. |
| **Directory** | Samba 4 Active Directory | AD-compatible LDAP/Kerberos; supports Windows/Linux clients. |
| **IAM / SSO** | Authentik | SAML/OIDC/LDAP/RADIUS; MFA (TOTP/WebAuthn); policy engine. |
| **Email/Collab** | Zimbra CE | External auth with AD; web client; calendar/contacts; on-prem storage. |
| **SIEM/XDR** | Wazuh | Centralized logging, correlation, compliance reports. |
| **Vuln Mgmt** | OpenVAS | CVSS-based scanning, risk prioritization. |
| **Observability** | Prometheus + Grafana | Metric collection, dashboards, alerting. |
| **IaC** | OpenTofu / Ansible | Infrastructure as Code, reproducible & portable setups. |

### 4.2 Methodology & Project Management
The project follows a strict DevOps and Project Management framework to ensure reproducibility and timely delivery.
*   *See [Methodology & Metrics](METHODOLOGY.md) for the evaluation framework (TCO, Security Tests).*
*   *See [Project Management](PROJECT_MANAGEMENT.md) for the timeline, WBS, and risk registry.*
