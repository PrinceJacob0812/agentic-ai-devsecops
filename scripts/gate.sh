#!/usr/bin/env bash
set -euo pipefail

: "${IMAGE_REF:?Set IMAGE_REF to an image reference pinned by SHA-256 digest}"
: "${IDENTITY:?Set IDENTITY to the expected signing certificate identity}"

ISSUER="${ISSUER:-https://token.actions.githubusercontent.com}"

for tool in cosign opa jq; do
    if ! command -v "$tool" >/dev/null 2>&1; then
        echo "ERROR: Required tool not found: $tool" >&2
        exit 1
    fi
done

POLICY_FILE="policies/deployment.rego"

if [[ ! -f "$POLICY_FILE" ]]; then
    echo "ERROR: Policy file not found: $POLICY_FILE" >&2
    exit 1
fi

TMP_DIR="$(mktemp -d)"
trap 'rm -rf "$TMP_DIR"' EXIT

echo "[1/3] Verifying image signature..."
cosign verify \
    --certificate-identity "$IDENTITY" \
    --certificate-oidc-issuer "$ISSUER" \
    "$IMAGE_REF" > "$TMP_DIR/signature.json"

echo "[2/3] Verifying signed CycloneDX SBOM attestation..."
cosign verify-attestation \
    --type cyclonedx \
    --certificate-identity "$IDENTITY" \
    --certificate-oidc-issuer "$ISSUER" \
    "$IMAGE_REF" > "$TMP_DIR/attestation.json"

test -s "$TMP_DIR/attestation.json"

jq -n \
    --arg image_ref "$IMAGE_REF" \
    '{
        image_ref: $image_ref,
        signature_verified: true,
        sbom_attestation_verified: true
    }' > "$TMP_DIR/input.json"

echo "[3/3] Evaluating OPA deployment policy..."
if [[ "$(opa eval --format raw \
    --data "$POLICY_FILE" \
    --input "$TMP_DIR/input.json" \
    'data.deployment.allow')" != "true" ]]; then
    echo "DENIED: Deployment policy rejected the image." >&2
    exit 1
fi

echo "ALLOWED: Signature, attestation and deployment policy checks passed."
