# Ubuntu Sovereign Stack - Vision Document

## 1. Core Vision & Problem
This project is a rebellion against Microsoft's **"Cloud-First"** strategy (Windows Server 2025/Azure mandates) and the risk of "data sovereignty violation" posed by the **US CLOUD Act**. The goal is to ensure that data remains 100% under the organization's control (On-Premise), not just physically, but also **legally and visibly**.

> *For the full background on this problem, see [Background Analysis](BACKGROUND_CLOUD_FIRST.md).*

## 2. Technical Architecture (Cloud Native & Open Source)
Instead of legacy virtualization, we are establishing a modern, **container-based** structure.
*   *See [System Architecture](ARCHITECTURE.md) for the full topology.*
*   *See [Tools & Components](TOOLS.md) for component details.*

*   **Server Operating System:** **Ubuntu Server LTS** for stability and 5-year support.
*   **Orchestration:** **Kubernetes** managed by **Rancher** (RKE2) for cluster management.
*   **Container Engine (Critical Distinction):** Mandatory use of **Podman** instead of Docker due to security (daemonless/rootless) advantages.
*   **Identity Management (IAM):** **Samba 4 Active Directory** (Source of Truth) replacing Windows AD, with **Authentik** integration for modern SSO/MFA.
*   **Communication:** **Zimbra Collaboration Suite (OSE)** as an Exchange alternative. Integrated with ClamAV and SpamAssassin for security.
*   **Security & Observability:** **Wazuh** for centralized SIEM, intrusion detection, and vulnerability scanning; **Prometheus** and **Grafana** for metric monitoring.

## 3. Client Strategy
To overcome end-user resistance, we adopt a flexible model instead of enforcing a "single Linux type".
*   *See [Client Strategy](CLIENT_STRATEGY.md) for the "Flexible 10" guide.*

*   **Linux Mint/Zorin OS** for those coming from Windows.
*   **Pop!_OS** for Engineers.
*   **Xubuntu/Lubuntu** for legacy hardware.
*   Offering a total of **10 different Ubuntu-based distribution** options.

## 4. Management Methodology (DevOps)
Instead of manual installation, we adopt the **"Infrastructure as Code" (IaC)** principle.
*   *See [Project Management](PROJECT_MANAGEMENT.md) for the implementation roadmap.*

*   Initial setup will be "plug-and-play" (reproducible) using **Ansible** and YAML configurations.
*   Daily management and visualization will be conducted via the **Rancher** interface.

## 5. Thesis Objectives
With this architecture, you will prove the following (as detailed in [Methodology](METHODOLOGY.md)):
1.  **Cost:** Reducing TCO (Total Cost of Ownership) by zeroing out licensing fees.
2.  **Legal Security:** Preventing data from being subject to US laws (CLOUD Act).
3.  **Applicability:** Demonstrating that open-source systems meet corporate performance requirements.

In summary; you have designed not just a "Linux server setup", but a fully-fledged **"Sovereign Cloud"** prototype that is legally, economically, and technically grounded.
