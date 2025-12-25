# Operational Runbook

Day-2 guidance for running the Ubuntu Sovereign Stack: routine checks, scaling, maintenance, backup/restore, and emergency actions.

## Daily
- Check cluster health: `kubectl get nodes`; `kubectl get pods -A --field-selector=status.phase!=Running,status.phase!=Succeeded`
- Review monitoring: Grafana dashboards (CPU, memory, storage, network), Prometheus targets, Wazuh alerts
- Verify backups: `velero backup get | head -5`; confirm last successful timestamp
- Cert status: `kubectl get certificate -A`

## Weekly
- Rotate admin passwords and API tokens; ensure secrets use strong values
- Inspect PVC usage: `kubectl get pvc -A`; watch for growth trends
- Review RBAC changes and audit logs
- Check image freshness: rebuild critical images; scan via Trivy or GHCR scanning

## Monthly
- Patch OS nodes (control + worker) with rolling drain/upgrade
- Rotate TLS for ingress and internal services; renew CA chains if self-signed
- Test Velero restore (namespace-level) into a staging namespace
- Capacity review: CPU/memory/IO headroom; plan node adds if >70% utilized

## Node Maintenance (Rolling)
1. Cordon + drain the node:
   ```bash
   kubectl cordon <node>
   kubectl drain <node> --ignore-daemonsets --delete-emptydir-data
   ```
2. Patch/upgrade OS and RKE2; reboot if required
3. Uncordon and verify workloads reschedule:
   ```bash
   kubectl uncordon <node>
   kubectl get pods -A --field-selector=status.phase!=Running,status.phase!=Succeeded
   ```
4. Repeat per node to maintain quorum (never drain all control planes at once)

## Scaling Workloads
- Horizontal: `kubectl scale deployment <name> -n <ns> --replicas=N`
- Vertical: adjust requests/limits; ensure Longhorn capacity is sufficient
- Add worker nodes: provision OS, run Ansible, join via RKE2 token (see CLUSTER_SETUP_GUIDE)

## Backup & Restore
- Ad-hoc backup: `velero backup create on-demand-$(date +%F) --wait`
- Restore to staging:
  ```bash
  velero restore create test-restore --from-backup <backup-name> --namespace-mappings default:restore-test
  kubectl get pods -n restore-test
  ```
- Production restore: validate target namespace is empty; announce change freeze; restore; run application-level checks (DB migrations, mail queues)

## Certificate & Secret Rotation
- Rotate ingress TLS secrets before expiry; prefer cert-manager issuers
- Rotate database and service credentials quarterly; restart dependent pods
- Never commit secrets to Git; use Kubernetes Secrets or external secret stores; encrypt at rest

## Logging & Monitoring
- Prometheus targets healthy: `curl http://<prom>:9090/api/v1/targets`
- Grafana alerts configured for CPU >80%, memory >80%, PVC usage >75%, node down, pod restart flaps
- Wazuh: verify agent enrollment and alert delivery; rotate API keys

## Incident Response (Quick Actions)
- Pod crash: `kubectl logs <pod> -n <ns> --tail=50`; delete pod to recreate
- Pending pods: check PVC binding, node resources, MetalLB IP availability
- Node NotReady: `journalctl -u rke2-server -n 100`; check disk/memory/network
- Storage issues: check Longhorn UI, replica health; avoid simultaneous node drains

## Change Management
- Use GitOps or CI validation before applying manifests
- Apply changes during maintenance windows; keep rollback YAMLs and Helm history
- Record: change description, author, timestamp, success/failure, rollback steps

## Contacts & Escalation
- Primary operators: cluster-admin group
- Security: security-ops group (handles RBAC, secrets, certificates)
- DR lead: responsible for Velero restore sign-off
