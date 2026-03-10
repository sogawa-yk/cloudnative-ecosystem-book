#!/usr/bin/env bash
set -euo pipefail

# Trivy Operator installation script
# Scans running workloads for vulnerabilities, misconfigurations, and secrets

echo "=== Adding Aqua Security Helm repository ==="
helm repo add aqua https://aquasecurity.github.io/helm-charts/
helm repo update

echo "=== Installing Trivy Operator ==="
helm install trivy-operator aqua/trivy-operator \
  --namespace trivy-system \
  --create-namespace \
  --set trivy.ignoreUnfixed=true \
  --set operator.scanJobsConcurrentLimit=3 \
  --set operator.vulnerabilityScannerEnabled=true \
  --set operator.configAuditScannerEnabled=true \
  --set operator.rbacAssessmentScannerEnabled=true \
  --set operator.secretScannerEnabled=true

echo "=== Waiting for Trivy Operator to be ready ==="
kubectl wait --for=condition=ready pod -l app.kubernetes.io/name=trivy-operator \
  -n trivy-system --timeout=300s

echo "=== Trivy Operator installation complete ==="
echo "View vulnerability reports: kubectl get vulnerabilityreports -n book-app"
echo "View config audit reports: kubectl get configauditreports -n book-app"
