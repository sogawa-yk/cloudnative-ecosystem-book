#!/usr/bin/env bash
set -euo pipefail

# Cilium installation script using Helm
# Prerequisites: Helm 3.x installed

CILIUM_VERSION="1.16.5"

echo "=== Adding Cilium Helm repository ==="
helm repo add cilium https://helm.cilium.io/
helm repo update

echo "=== Installing Cilium ==="
helm install cilium cilium/cilium \
  --version "${CILIUM_VERSION}" \
  --namespace kube-system \
  --set hubble.relay.enabled=true \
  --set hubble.ui.enabled=true \
  --set hubble.metrics.enableOpenMetrics=true \
  --set hubble.metrics.enabled="{dns,drop,tcp,flow,port-distribution,icmp,httpV2:exemplars=true;labelsContext=source_ip\,source_namespace\,source_workload\,destination_ip\,destination_namespace\,destination_workload\,traffic_direction}"

echo "=== Waiting for Cilium to be ready ==="
kubectl wait --for=condition=ready pod -l app.kubernetes.io/part-of=cilium -n kube-system --timeout=300s

echo "=== Applying CiliumNetworkPolicy ==="
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
kubectl apply -f "${SCRIPT_DIR}/network-policy.yaml"

echo "=== Cilium installation complete ==="
echo "Verify with: cilium status"
