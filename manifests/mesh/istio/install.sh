#!/usr/bin/env bash
set -euo pipefail

# Istio installation script
# Prerequisites: istioctl installed (https://istio.io/latest/docs/setup/getting-started/)

NAMESPACE="book-app"

echo "=== Installing Istio with demo profile ==="
istioctl install --set profile=demo -y

echo "=== Enabling sidecar injection for namespace ${NAMESPACE} ==="
kubectl label namespace "${NAMESPACE}" istio-injection=enabled --overwrite

echo "=== Applying Istio resources ==="
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
kubectl apply -f "${SCRIPT_DIR}/gateway.yaml"
kubectl apply -f "${SCRIPT_DIR}/virtualservice.yaml"
kubectl apply -f "${SCRIPT_DIR}/destination-rule.yaml"

echo "=== Restarting deployments to inject sidecars ==="
kubectl rollout restart deployment -n "${NAMESPACE}"

echo "=== Istio installation complete ==="
echo "Verify with: istioctl analyze -n ${NAMESPACE}"
