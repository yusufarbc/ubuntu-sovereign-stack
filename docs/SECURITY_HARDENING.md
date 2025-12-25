# Security Hardening Guide

Controls to secure the Ubuntu Sovereign Stack across Kubernetes, runtime, identity, and backup layers.

## Identity & Access
- Central auth: Samba AD as source of truth; Authentik for SSO/MFA
- RBAC: least privilege roles per team (platform-admin, app-admin, read-only)
- Service accounts: namespace-scoped; bind minimal Roles/RoleBindings
- API access: enforce short-lived kubeconfig tokens; rotate quarterly

## Network Policies
- Default deny per namespace; only allow required egress/ingress
- Identity namespace: allow Authentik ↔ Postgres/Redis; block internet egress except updates
- Monitoring: allow Prometheus scrapes; restrict Grafana to ingress/LB
- Backup: allow Velero ↔ MinIO; block public egress
- Apps: expose only via Ingress/LoadBalancer; deny pod-to-pod by default

Example baseline (adapt per namespace):
```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: default-deny
spec:
  podSelector: {}
  policyTypes: [Ingress, Egress]
```

## Pod Security / PSA
- Enforce baseline or restricted Pod Security Admission labels on namespaces
- Run rootless where possible; set `runAsNonRoot: true`, drop `NET_RAW`, disallow privileged
- Set `readOnlyRootFilesystem: true` for stateless services
- Use seccomp: `runtime/default` and AppArmor profiles where available

## Secrets & Certificates
- Never commit secrets; store in Kubernetes Secrets or external secret stores
- Rotate secrets quarterly; force pod restarts after rotation
- TLS: use cert-manager issuers; monitor `kubectl get certificate -A`
- Encrypt at rest (Longhorn supports replica encryption if enabled)

## Supply Chain & Images
- Pin images to digests; avoid `latest`
- Scan images (Trivy/GHCR scanning) before promotion
- Allowlist registries; block public pulls in production
- Enable admission checks (e.g., kyverno/gatekeeper) for image policy and mandatory labels

## Resource Governance
- Set requests/limits for all workloads; prevent noisy-neighbor issues
- Quotas per namespace for CPU, memory, PVC count, and object counts
- Liveness/readiness probes required; startup probes for heavy apps (Zimbra)

## Logging & Monitoring
- Centralize logs (Fluentd/Loki/ELK optional); ensure Wazuh agents enrolled
- Alerting: node NotReady, pod restarts >5/10m, API server latency, PVC >75%, Velero failures
- Audit logs: enable Kubernetes audit policy; ship to SIEM (Wazuh)

## Backup & DR
- Velero schedules with MinIO; ensure IAM key rotation
- Monthly restore drills into staging namespace; validate app health post-restore
- Document RPO/RTO per workload; tag critical PVCs for snapshot frequency

## Ingress & Certificates
- Use HTTPS everywhere; HSTS on public endpoints
- Prefer DNS-validated certs; for air-gapped, manage internal CA and rotation calendar
- Enforce TLS 1.2+; disable weak ciphers on ingress controller

## Node & OS
- Patch cadence: monthly; use cordon/drain per runbook
- Disable password SSH; key-based only; restrict sudoers
- Auditd or Wazuh agent on nodes; forward security events
- Time sync with chrony; consistent logs for forensics

## Admin Checklist (Ongoing)
- [ ] NetworkPolicies applied to all namespaces
- [ ] PSA labels set (baseline/restricted) on namespaces
- [ ] Requests/limits + probes on every workload
- [ ] Secrets rotated on schedule; no secrets in Git
- [ ] TLS certs monitored; renew before expiry
- [ ] Velero backup success + monthly restore test
- [ ] Image scans clean; no `latest` tags
- [ ] RBAC least privilege; audit bindings quarterly
