# Methodology & Evaluation Metrics

To prove the validity of the "Ubuntu Sovereign Stack" as a replacement for Microsoft's Cloud-First ecosystem, the thesis employs a multi-dimensional evaluation methodology.

## 1. Total Cost of Ownership (TCO) Analysis
**Goal:** Quantify the economic advantage of the Open Source model.
*   **Method:** A 5-Year Projection comparison between:
    *   **Scenario A (Microsoft):** Windows Server licenses + CALs + Azure Subscriptions + Exchange Enterprise CALs + System Center costs.
    *   **Scenario B (Ubuntu Sovereign):** Hardware costs + Electricity + Estimated Engineering hours (OpEx).
*   **Metric:** Net cost savings (CapEx + OpEx) and break-even point analysis.

## 2. Security Assessment
**Goal:** Prove that "Open Source" does not mean "Less Secure".
*   **Vulnerability Scanning:** Periodic full-stack scans.
    *   *Metric:* Number of Critical/High ongoing vulnerabilities vs. Time to Remediate.
*   **Incident Detection:** Simulation of attacks (e.g., "WannaCry-style" ransomware simulation or Brute Force patterns).
    *   *Metric:* Detection time (MTTD) by **Wazuh** and Response time (MTTR).
*   **Identity Security:** Verification of MFA enforcement.
    *   *Metric:* Testing authenticated access attempts without MFA (Should Fail).

## 3. Usability & Manageability Analysis
**Goal:** Assess the operational overhead for IT Administrators.
*   **Automation:** Testing the "Infrastructure as Code" maturity.
    *   *Metric:* Time required to rebuild the entire cluster from scratch using Ansible (Reproducibility Test).
*   **Day-2 Operations:** Routine tasks evaluation.
    *   *Metric:* Number of "clicks/steps" to provision a new user in Authentik/Samba vs. Active Directory Users & Computers (ADUC).

## 4. Client Strategy Verification (UX)
**Goal:** Evaluate end-user adaptability to Linux Desktops.
*   **Pilot Study:** A 1-week structured pilot with non-technical users on **Linux Mint/Zorin OS**.
*   **Qualitative Data:** Semi-structured interviews covering:
    *   "Can you perform your daily office tasks (Docs, Email)?"
    *   "How does the interface compare to Windows?"
*   **Quantitative Data:** Task completion success rate (e.g., "Connect to Printer", "Open from Network Share").

## 5. Sovereignty Stress Test
**Goal:** Confirm Data Residency guarantees.
*   **Network Isolation:** Verifying zero telemetry egress.
    *   *Method:* Packet capture (Wireshark) at the firewall level to ensure no unauthorized data (telemetry) leaves the local network to US-based servers (unlike Windows 10/11 default behavior).
