#!/usr/bin/env bash
set -euo pipefail

# Cosign verification examples for container images
# Prerequisites: cosign installed (https://docs.sigstore.dev/cosign/system_config/installation/)

REGISTRY="${REGISTRY:-ghcr.io/cloudnative-book}"
COSIGN_KEY="${COSIGN_KEY:-cosign.pub}"

# --- Sign an image ---
sign_image() {
  local image="$1"
  echo "=== Signing image: ${image} ==="
  cosign sign --key cosign.key "${image}"
}

# --- Verify an image signature ---
verify_image() {
  local image="$1"
  echo "=== Verifying image: ${image} ==="
  cosign verify --key "${COSIGN_KEY}" "${image}"
}

# --- Verify all book-app images ---
verify_all() {
  echo "=== Verifying all book-app images ==="
  local images=(
    "${REGISTRY}/frontend:latest"
    "${REGISTRY}/api-gateway:latest"
    "${REGISTRY}/product-service:latest"
    "${REGISTRY}/order-service:latest"
  )

  for image in "${images[@]}"; do
    echo ""
    verify_image "${image}"
  done
}

# --- Generate a key pair ---
generate_keys() {
  echo "=== Generating Cosign key pair ==="
  cosign generate-key-pair
  echo "Keys generated: cosign.key (private), cosign.pub (public)"
}

# --- Verify with keyless (Sigstore) ---
verify_keyless() {
  local image="$1"
  local identity="$2"
  local issuer="$3"
  echo "=== Keyless verification for: ${image} ==="
  cosign verify \
    --certificate-identity "${identity}" \
    --certificate-oidc-issuer "${issuer}" \
    "${image}"
}

# Main
case "${1:-help}" in
  sign)
    sign_image "$2"
    ;;
  verify)
    verify_image "$2"
    ;;
  verify-all)
    verify_all
    ;;
  generate-keys)
    generate_keys
    ;;
  verify-keyless)
    verify_keyless "$2" "$3" "$4"
    ;;
  *)
    echo "Usage: $0 {sign|verify|verify-all|generate-keys|verify-keyless} [args...]"
    echo ""
    echo "Commands:"
    echo "  sign <image>                          Sign an image"
    echo "  verify <image>                        Verify an image signature"
    echo "  verify-all                            Verify all book-app images"
    echo "  generate-keys                         Generate a Cosign key pair"
    echo "  verify-keyless <image> <id> <issuer>  Keyless verification"
    ;;
esac
