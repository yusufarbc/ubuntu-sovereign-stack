# Project Management & Deliverables

## Work Breakdown Structure (WBS) & Timeline

### Month 1-2: Foundation & Requirements
*   **Activity:** Hardware sourcing, Network topology design.
*   **Output:** `infrastructure/` code complete. OpenTofu/Ansible scripts ready.
*   **Milestone:** Cluster Scaffolded.

### Month 3-4: Core Services Deployment
*   **Activity:** Deploying Kubernetes Workloads.
*   **Focus:** Identity (Samba/Authentik) and Collaboration (Zimbra).
*   **Milestone:** Successful Email flow and User Login.

### Month 5: Security & Refinement
*   **Activity:** Hardening.
*   **Focus:** Deploying Wazuh Agents, configuring OpenVAS scans, fine-tuning Firewall rules.
*   **Milestone:** Security Audit Passed.

### Month 6: Validation & Reporting
*   **Activity:** TCO Calculation, UX Pilot Testing.
*   **Output:** Final Thesis Report, Comparative Anaylsis Tables.
*   **Milestone:** Thesis Defense.

## Risk Management

| Risk | Impact | Mitigation Strategy |
| :--- | :--- | :--- |
| **User Resistance** | High | Use familiar UIs (Linux Mint); Provide robust training; Highlight privacy benefits. |
| **Legacy App Incompatibility** | Medium | Maintain a small VDI pool for indispensable Windows apps; Aggressively move to Web-based alternatives. |
| **Operational Complexity** | Medium | Use **Rancher** to simplify K8s management; Document everything in "Runbooks". |
| **Data Loss** | Critical | **3-2-1 Backup Rule**: Local Snapshots (Longhorn) + NAS Backup + Offline Replica. |

## Deliverables
1.  **Working Prototype:** A fully functional 3-node Kubernetes cluster running the Sovereign Stack.
2.  **Documentation Suite:**
    *   Technical Runbooks (Installation/Configuration).
    *   Architecture Diagrams.
3.  **Analysis Reports:**
    *   TCO Comparative Analysis (Excel/PDF).
    *   Security Vulnerability Report (OpenVAS Export).
    *   User Experience Survey Results.
4.  **Academic Thesis:** The final written document defending the model.
