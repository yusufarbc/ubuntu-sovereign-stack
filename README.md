# Ubuntu Sovereign Stack

## Background: The "Cloud-First" Imposition
Microsoft has made its stance clear: the future is Azure. This is evidenced by the deprecation of **WSUS**, the shift to **Azure Update Manager**, and the admission that European data is subject to the **US CLOUD Act**.

> For a detailed analysis of Microsoft's strategy, the deprecation of on-prem tools, and the legal risks of the CLOUD Act, please read our [**Background Analysis: Cloud-First Strategy vs. Data Sovereignty**](docs/BACKGROUND_CLOUD_FIRST.md).

This project demonstrates that an organization can build a **100% On-Premise**, **Enterprise-Grade** infrastructure that ensures data remains physically, legally, and operationally under their sole control—without sacrificing modern capabilities.

## Core Objectives
This architecture serves as a prototype to validate four core requirements:
1.  **TCO Advantage:** What is the tangible cost benefit of eliminating proprietary licensing (CALs, Subscriptions)?
2.  **Security & Compliance:** Can Open Source solutions (Wazuh, Authentik) achieve parity with proprietary enterprise security stacks?
3.  **Usability & Manageability:** How effectively does the Rancher/Kubernetes abstraction layer modernize on-premise operations?
4.  **Data Sovereignty:** How does this architecture specifically mitigate the legal risks associated with data residency and the US CLOUD Act?

## Technical Architecture (Cloud Native & Open Source)
We replace legacy virtualization with a modern, container-centric stack.

| Layer | Component | Implementation |
| :--- | :--- | :--- |
| **Server OS** | **Ubuntu Server LTS** | Selected for stability and 5-year support cycles. Runs on bare-metal across 3 physical nodes. |
| **Orchestration** | **Kubernetes (RKE2)** | FIPS-compliant, secure distribution managed by **Rancher** for centralized cluster operations. |
| **Runtime** | **Podman** | **Critical Requirement:** A Daemonless and Rootless container engine. Docker is explicitly excluded to eliminate the security risks of a central daemon. |
| **Identity (IAM)** | **Samba 4 AD + Authentik** | **Samba 4** serves as the Active Directory Source of Truth. **Authentik** bridges legacy AD with modern SSO/MFA. |
| **Collaboration** | **Zimbra Suite** | A full replacement for Exchange/O365, secured with **ClamAV** and **SpamAssassin**. |
| **Security (SIEM)** | **Wazuh** | Centralized SIEM for Intrusion Detection and Log Analysis. |

| **Observability** | **Prometheus + Grafana** | Real-time metric collection and visualization. |

## DevOps Methodology
We reject manual "click-ops" in favor of **Infrastructure as Code (IaC)**:
*   **Reproducibility:** The initial server provisioning is handled by **Ansible**. The entire stack can be rebuilt from code.
*   **Management:** Day-2 operations are handled via the **Rancher** UI, providing a "Single Pane of Glass" for the entire cluster.

## The "Flexible 10" Client Strategy
To overcome user resistance to Linux, we reject the "one size fits all" approach. We offer a curated menu of 10 Ubuntu-based distributions tailored to specific user personas:

| Distribution | Target Profile | Rationale |
| :--- | :--- | :--- |
| **1. Ubuntu Desktop** | Standard Corporate User | The reference standard; stable, supported, and universally recognized. |
| **2. Linux Mint** | Office / Admin Staff | Cinnamon DE provides a highly familiar Windows-7/10 like workflow. |
| **3. Zorin OS** | Management / Execs | Highly polished, aesthetic interface resembling modern Windows/macOS. |
| **4. Pop!_OS** | R&D / Engineers | Optimized for development, tiling windows, and native GPU support. |
| **5. Kubuntu** | Power Users | KDE Plasma offers maximum configurability for users needing granular control. |
| **6. Xubuntu** | Legacy Hardware | Lightweight XFCE desktop to extend the life of older corporate assets. |
| **7. Lubuntu** | Thin Clients | Extremely lightweight (LXQt) for low-resource endpoints. |
| **8. Ubuntu MATE** | Traditionalists | GNOME 2 fork for users preferring the classic Linux desktop metaphor. |
| **9. elementary OS** | Kiosks / Public | macOS-like, restrictive interface perfect for focused, simplified usage. |
| **10. KDE Neon** | Bleeding Edge / Testing | For evaluating the latest desktop technologies before wider rollout. |

## Quick Start
### Prerequisites
*   3x Physical Servers (Ubuntu 22.04/24.04 LTS)
*   Ansible installed on your control node.

### Provisioning
1.  **Clone the Repository:**
    ```bash
    git clone https://github.com/yusufarbc/ubuntu-sovereign-stack.git
    cd ubuntu-sovereign-stack
    ```

2.  **Configure Inventory:**
    Edit `infrastructure/hosts.ini` with your server IP addresses.

3.  **Deploy Infrastructure:**
    Use Ansible to update systems, install Podman, and deploy RKE2:
    ```bash
    ansible-playbook -i infrastructure/hosts.ini infrastructure/setup-rke2.yml
    ```

## Detailed Documentation
For a navigable index of all research and technical documents, please visit the **[Documentation Directory](docs/)**.

This repository contains a comprehensive documentation suite for the project:

*   **[Background Analysis](docs/BACKGROUND_CLOUD_FIRST.md):** Deep dive into Microsoft's "Cloud-First" strategy and the case for sovereignty.
*   **[Comparative Analysis](docs/COMPARATIVE_ANALYSIS.md):** Detailed architectural comparison and defense against the Microsoft Ecosystem.
*   **[System Architecture](docs/ARCHITECTURE.md):** Detailed breakdown of the 3-Node Cluster, Networking, and Storage layers.
*   **[Tools & Components](docs/TOOLS.md):** Justification for every component selection (Podman, RKE2, Authentik, etc.).
*   **[Methodology & Metrics](docs/METHODOLOGY.md):** How we measure TCO, Security, and Usability.
*   **[Client Strategy](docs/CLIENT_STRATEGY.md):** The "Flexible 10" adoption model for end-users.
*   **[Project Management](docs/PROJECT_MANAGEMENT.md):** Timeline, WBS, and Risk Registry.
*   **[Gap Analysis](docs/GAP_ANALYSIS.md):** Initial analysis of missing system components.
