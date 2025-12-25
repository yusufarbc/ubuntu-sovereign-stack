# Project Proposal: Ubuntu-Based Open-Source Sovereign Enterprise Architecture

> *   **Server:** Kubernetes (Rancher)
> *   **IAM/MFA:** Authentik
> *   **Directory:** Samba AD + Zimbra CE
> *   **Client:** Ubuntu LTS and Derivatives

## Abstract
This project presents a fully on-premise, Ubuntu LTS-based open-source enterprise architecture designed to reduce cloud dependence and strengthen data sovereignty. Server-side services run as containers on Kubernetes managed by Rancher; identity and MFA are provided by Authentik; directory and mail services are implemented with Samba 4 Active Directory and Zimbra Community Edition. Security and observability layers rely on Wazuh (SIEM) and Prometheus + Grafana (metrics and alerting). The network perimeter is protected by physical firewalls, and backups are handled by physical appliances (e.g., QNAP NAS). The initiative aims to produce comparative evidence—against Microsoft’s cloud-first ecosystem—across TCO, security, usability, and portability, with a primary legal focus on data residency and sovereignty.

## Vision & Problem Statement
Cloud-first mandates and the U.S. CLOUD Act create extraterritorial exposure even when data is hosted in-region. The goal is an on-prem, open-source stack where compute, identity, keys, and backups remain under the organization’s legal and operational control, avoiding vendor-operated control planes. (*See* [Background Analysis](BACKGROUND_CLOUD_FIRST.md) for legal/strategic context.)

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
*   **Server Side:** 1× control plane + 2× worker (Ubuntu Server LTS) running RKE2; Rancher for lifecycle, RBAC, and observability. Helm/manifests; CI/CD-ready.
    *   *See [System Architecture](ARCHITECTURE.md) for detailed node and network topology.*
*   **Runtime:** Podman-only policy (daemonless/rootless); Docker explicitly excluded.
*   **Storage/Network/PKI:** Longhorn (CSI) for PVCs; MetalLB (L2) for service IPs; Cert-Manager for internal PKI.
*   **Backup:** Velero + MinIO (S3-compatible) for cluster and volume protection; CSI/kopia snapshots; periodic recovery drills.
*   **Client Side:** Ubuntu LTS derivatives (Linux Mint, Zorin OS, etc.) selected based on user experience and deployed via phased pilots.
    *   *See [Client Strategy](CLIENT_STRATEGY.md) for the "Flexible 10" model.*
*   **Network Security:** Physical firewall; segmentation/VPN; IDS/IPS options.

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

| **Observability** | Prometheus + Grafana | Metric collection, dashboards, alerting. |
| **Storage** | Longhorn (CSI) | Distributed block storage with snapshots. |
| **Load Balancing** | MetalLB (L2) | Service IPs on bare-metal via ARP/NDP. |
| **PKI** | Cert-Manager | Automated internal certificates. |
| **Backup** | Velero + MinIO (S3) | Cluster + PVC backups with CSI/kopia. |
| **IaC** | Ansible | Infrastructure as Code, reproducible & portable setups. |

### 4.2 Methodology & Project Management
The project follows a strict DevOps and Project Management framework to ensure reproducibility and timely delivery.
*   *See [Methodology & Metrics](METHODOLOGY.md) for the evaluation framework (TCO, Security Tests).*
*   *See [Project Management](PROJECT_MANAGEMENT.md) for the timeline, WBS, and risk registry.*

## 5. Client Strategy (“Flexible 10”)
Persona-based desktop catalog to reduce migration friction: Ubuntu Desktop (baseline), Linux Mint/Zorin (Windows converts), Pop!_OS (engineers), Kubuntu (power users), Xubuntu/Lubuntu (legacy/thin), Ubuntu MATE (traditional), elementary OS (kiosk/public), KDE Neon (R&D). (*See* [Client Strategy](CLIENT_STRATEGY.md) for full grid and rollout.)

## 6. Operating Model (IaC + GUI)
* Provisioning/rebuilds via Ansible (repeatable, testable).
* Day-2 ops via Rancher UI plus GitOps-friendly manifests and Helm charts.

## 7. Objectives & Measures
* **TCO:** Avoid CALs/O365/Azure licensing; quantify infra + ops cost.
* **Legal Security:** Keep control planes, keys, and backups on-prem to avoid CLOUD Act reach.
* **Usability/Manageability:** Compare Rancher/K8s ops to Azure Portal experience.
* **Reproducibility:** Time-to-rebuild via Ansible + Velero restores.

---

## 8. Implementation Timeline & Work Breakdown Structure (WBS)

### Phase 1: Foundation & Requirements (Month 1-2)
* **Hardware Sourcing:** Procure 3× servers (CPU, RAM, SSD, NIC specs).
* **Network Topology Design:** Segment networks, plan firewall rules, DNS split-view.
* **Ansible Scaffolding:** Baseline OS deployment scripts (Ubuntu LTS, kernel tuning, Podman).
* **Output:** Cluster Bootstrapped; RKE2 cluster running.
* **Milestone:** All 3 nodes running RKE2, Rancher UI accessible.

### Phase 2: Core Services Deployment (Month 3-4)
* **Identity:** Deploy Samba 4 AD (StatefulSet, PVC, backups). Test user login.
* **IAM/SSO:** Deploy Authentik; sync with Samba; configure MFA policies.
* **Collaboration:** Deploy Zimbra CE (StatefulSet with external auth).
* **Storage/Networking:** Deploy Longhorn, MetalLB, Cert-Manager.
* **Output:** Email flow works end-to-end; users can SSO to Zimbra.
* **Milestone:** First successful email delivery; successful MFA login.

### Phase 3: Security & Refinement (Month 5)
* **Observability:** Deploy Prometheus, Grafana, and Wazuh.
* **Hardening:** Firewall tuning, SELinux/AppArmor rules, network segmentation.
* **Incident Response:** Wazuh rule creation; drill "ransomware detection" scenario.
* **Output:** Security baselines documented; compliance checklist passed.
* **Milestone:** Security audit passed; zero "Critical" findings.

### Phase 4: Validation & Reporting (Month 6)
* **TCO Calculation:** Tally CapEx (hardware), OpEx (electricity, staffing), compare to Microsoft (5-year).
* **UX Pilot:** Deploy Linux Mint to 5 office users, Pop!_OS to 5 engineers; collect feedback.
* **Performance Testing:** Measure cluster recovery time (Velero restore), patch cycle.
* **Final Report:** Comparative analysis tables, lessons learned, recommendations.
* **Output:** Thesis document, defense slides.
* **Milestone:** Thesis defense; prototype stable for 6+ months.

---

## 9. Risk Management & Mitigation Strategy

| Risk | Impact | Probability | Mitigation Strategy |
| :--- | :--- | :--- | :--- |
| **User Resistance (Desktop Migration)** | High | Medium | Start with Linux Mint (Windows-like UI); robust end-user training; highlight privacy/cost benefits; provide support hotline. |
| **Legacy App Incompatibility** | High | Medium | Early inventory of Windows-only apps; maintain small VDI pool for essential apps; migrate web-based apps aggressively. |
| **Operational Complexity (Kubernetes/Ansible)** | Medium | Medium | Use Rancher UI to lower K8s barrier; comprehensive runbooks; pair junior admins with seniors; invest in training. |
| **Samba 4 / Authentik Integration Issues** | Medium | Low | Early integration testing; maintain test environment; document federation workflows. |
| **Data Loss (Backup Failure)** | Critical | Low | 3-2-1 Backup Rule: Longhorn local snapshots + Velero to S3 + physical NAS cold copy; monthly recovery drills. |
| **Hardware Failure (Node Outage)** | High | Low | 3-node HA cluster; etcd redundancy; PVC replication via Longhorn; automated failover. |
| **Compliance / Audit Findings** | Medium | Low | Early engagement with compliance team; document GDPR/ISO 27001 alignment; Wazuh for audit trail. |
| **Vendor Lock-in (Authentik/Samba EOL)** | Low | Very Low | Both are open-source with active communities; multi-year stable releases; document migration path. |

---

## 10. Deliverables & Success Criteria

### 1. Working Prototype
* **3-node Kubernetes cluster** (RKE2) running on Ubuntu Server LTS.
* **All core services deployed** and functional: Samba AD, Authentik, Zimbra, Wazuh, Prometheus/Grafana, Longhorn, MetalLB, Velero.
* **User workflows verified**: Login → Zimbra email → File access via Samba shares → Observability via Grafana dashboard.
* **Backup & recovery tested**: Velero snapshot → restore cycle verified on test cluster.

### 2. Documentation Suite
* **Infrastructure as Code (IaC):**
  * Ansible playbooks for full cluster rebuild (infrastructure/, kubernetes/ directories).
  * Kubernetes manifests (YAML) for all services; Helm charts where applicable.
  * Network topology diagram (physical + logical).
* **Operational Runbooks:**
  * Cluster scaling (add/remove worker nodes).
  * Service patching (RKE2, Podman, app updates).
  * Backup/restore procedures (Velero recovery drills).
  * Incident response (e.g., "Pod CrashLoopBackOff", "Samba replication lag").
* **Architecture Document** (System Architecture + this Strategic Implementation Plan).

### 3. Analysis Reports
* **TCO Comparative Analysis (5-year projection):**
  * Scenario A (Microsoft): Windows Server licenses, CALs, Azure subscriptions, Exchange, System Center.
  * Scenario B (Ubuntu Sovereign): Hardware, electricity, estimated engineering FTE costs.
  * Break-even point, payback period, cost per user per month.
* **Security Assessment Report:**
  * Vulnerability scanning results (tools: Trivy, Falco).
  * Incident simulation results (ransomware detection time via Wazuh).
  * MFA enforcement verification (all users require TOTP/WebAuthn).
* **User Experience Survey:**
  * Pilot results from Linux Mint (office) and Pop!_OS (engineers).
  * Task completion success rates (email, file sharing, VPN, printing).
  * Net Promoter Score (NPS) and satisfaction metrics.
* **Reproducibility Benchmark:**
  * "Time to rebuild cluster from scratch" using Ansible + Velero restore.
  * Cost of adding a new node / replacing failed node.

### 4. Academic Thesis
* Written defense of the Ubuntu Sovereign Stack model.
* Chapters: (1) Introduction & Background, (2) Technical Architecture, (3) Comparative Analysis, (4) Implementation Results, (5) Lessons Learned, (6) Recommendations.
* Presentation slides for oral defense.

---

## 11. Client Strategy: The "Flexible 10" Model

Persona-based desktop catalog to reduce migration friction and support burden. Details in [CLIENT_STRATEGY.md](CLIENT_STRATEGY.md); summary:

| # | Distro | Persona | Rationale |
| --- | --- | --- | --- |
| 1–3 | Ubuntu, Mint, Zorin | Standard / Admin / Exec | Baseline, Windows-like, premium. |
| 4–5 | Pop!_OS, Kubuntu | Engineers, Power Users | Dev tooling, customization. |
| 6–8 | Xubuntu, Lubuntu, MATE | Legacy, Thin, Traditional | Lightweight, classic UX. |
| 9–10 | elementary, KDE Neon | Kiosk, R&D Lab | Polished lockdown, latest KDE. |

**Rollout Strategy:**
1. Inventory Windows-only apps; classify as Replace/Emulate/Virtualize.
2. Pilot Mint (office, n=5) + Pop!_OS (engineers, n=5) for 2 weeks.
3. Gather feedback; refine distro assignments.
4. Stage rollout by team; provide training, cheat sheets, support hotline.
5. Monitor helpdesk ticket volume; adjust if blockers emerge.

---

## 12. Operating Model: IaC + GUI

### Infrastructure as Code (Ansible)
* **Provisioning:** Ansible playbooks for baseline OS deployment, Podman runtime, kernel tuning.
* **Scaling:** Add worker nodes via Ansible; regenerate kubeconfig; verify node joins cluster.
* **Patching:** Rolling OS/RKE2 updates orchestrated via Ansible + Rancher (minimal downtime).
* **Reproducibility:** Full stack rebuild from bare metal in <2 hours using Ansible + Velero restore.

### Day-2 Operations (Rancher + GitOps)
* **Rancher UI:** Manage workloads, RBAC, multi-cluster federation, health dashboards.
* **Helm Charts:** Templated, version-controlled app deployments (Zimbra, Wazuh, etc.).
* **GitOps:** All manifests in Git; pull requests for changes; automated CD pipeline.
* **Monitoring:** Prometheus scrapes metrics; Grafana dashboards accessible to ops team.

### Incident Response
* **SIEM:** Wazuh correlates logs from all services; alerts on anomalies (failed logins, file exfiltration patterns).
* **Alerting:** PagerDuty / Grafana alerts for CPU/memory/disk thresholds; Samba replication lag; Zimbra queue backlog.
* **Runbooks:** Step-by-step remediation procedures; automated recovery where possible (e.g., Pod restart).

---

## 13. Success Criteria & Exit Criteria

### Go / No-Go Criteria for Phase Transitions

| Phase | Exit Criterion | Verification |
| :--- | :--- | :--- |
| **Phase 1 (Foundation)** | RKE2 cluster stable; all nodes healthy | `kubectl get nodes` → 3× Ready |
| **Phase 2 (Services)** | Samba AD + Authentik synced; Zimbra email flows | User login → Zimbra web access → Send/receive email |
| **Phase 3 (Security)** | Zero Critical vulnerabilities; Wazuh correlation rules functional | Trivy scan; simulate ransomware → Wazuh detects |
| **Phase 4 (Validation)** | Pilot pilots complete; TCO report finalized; Defense scheduled | NPS ≥ 6.5; all deliverables submitted |

### Long-Term Success Metrics
* **Availability:** 99.5% uptime over 6 months (excluding maintenance windows).
* **RTO/RPO:** Cluster recovery time <4 hours (via Velero); RPO <24 hours (daily snapshots).
* **Cost Efficiency:** TCO savings ≥30% vs. Microsoft over 5 years.
* **User Adoption:** ≥80% of pilot users satisfied (NPS ≥ 7); zero mandatory rollback.
* **Operational Maturity:** All runbooks tested; incident response time <30 min for critical alerts.

---

## 14. Lessons Learned & Future Work

### Expected Learnings
* **Kubernetes Maturity:** How well does RKE2 perform on bare-metal (vs. cloud-managed K8s)?
* **Identity Integration:** Samba 4 → Authentik → Zimbra federation complexity.
* **Desktop Diversity:** Is the "10 variants" approach sustainable, or does it require consolidation?
* **Ops Burden:** Ansible/Kubernetes learning curve vs. traditional Windows admin skillset.

### Future Enhancements
* **Multi-datacenter Failover:** Kubernetes federation across geographic sites.
* **AI/ML Integration:** Wazuh ML for anomaly detection; predictive alerting.
* **Advanced Backup Strategies:** Off-site replication; immutable backups; ransomware protection via air-gapped replicas.
* **Compliance Automation:** Continuous compliance scanning (OSCAP); automated remediation.
* **Capacity Planning:** Predictive scaling based on demand trends (Prometheus + Thanos).

---

## 15. Stakeholder Sign-Off & Approval

| Role | Name | Signature | Date |
| :--- | :--- | :--- | :--- |
| **Project Sponsor (CIO)** | [Name] | _______ | [Date] |
| **Technical Architect** | [Name] | _______ | [Date] |
| **Security Officer** | [Name] | _______ | [Date] |
| **Project Manager** | [Name] | _______ | [Date] |

---

**Document Version:** 1.0  
**Last Updated:** December 2025  
**Status:** In Implementation (Phase 1 in progress)
