#!/usr/bin/env bash
set -euo pipefail

: "${IMAGE_REF:?Set IMAGE_REF to an image reference pinned by SHA-256 digest}"
: "${IDENTITY:?Set IDENTITY to the expected signing certificate identity}"
: "${GRYPE_JSON:?Set GRYPE_JSON to the Grype JSON report path}"

ISSUER="${ISSUER:-https://token.actions.githubusercontent.com}"
POLICY_FILE="policies/deployment.rego"

for tool in cosign opa jq; do
    if ! command -v "$tool" >/dev/null 2>&1; then
        echo "ERROR: Required tool not found: $tool" >&2
        exit 1
    fi
done

if [[ ! -f "$POLICY_FILE" ]]; then
    echo "ERROR: Policy file not found: $POLICY_FILE" >&2
    exit 1
fi

if [[ ! -f "$GRYPE_JSON" ]]; then
    echo "ERROR: Grype report not found: $GRYPE_JSON" >&2
    exit 1
fi

if ! jq -e '.matches | type == "array"' "$GRYPE_JSON" >/dev/null; then
    echo "ERROR: Invalid Grype JSON report." >&2
    exit 1
fi

TMP_DIR="$(mktemp -d)"
trap 'rm -rf "$TMP_DIR"' EXIT

echo "[1/4] Verifying image signature..."
cosign verify \
    --certificate-identity "$IDENTITY" \
    --certificate-oidc-issuer "$ISSUER" \
    "$IMAGE_REF" > "$TMP_DIR/signature.json"

echo "[2/4] Verifying signed CycloneDX SBOM attestation..."
cosign verify-attestation \
    --type cyclonedx \
    --certificate-identity "$IDENTITY" \
    --certificate-oidc-issuer "$ISSUER" \
    "$IMAGE_REF" > "$TMP_DIR/attestation.json"

test -s "$TMP_DIR/attestation.json"

echo "[3/4] Checking Grype vulnerability report..."
CRITICAL_COUNT="$(jq \
    '[.matches[]? | select(.vulnerability.severity == "Critical")] | length' \
    "$GRYPE_JSON")"

echo "Critical vulnerabilities found: $CRITICAL_COUNT"

jq -n \
    --arg image_ref "$IMAGE_REF" \
    --argjson critical_count "$CRITICAL_COUNT" \
    '{
        image_ref: $image_ref,
        signature_verified: true,
        sbom_attestation_verified: true,
        critical_count: $critical_count
    }' > "$TMP_DIR/input.json"

echo "[4/4] Evaluating OPA deployment policy..."
if [[ "$(opa eval --format raw \
    --data "$POLICY_FILE" \
    --input "$TMP_DIR/input.json" \
    'data.deployment.allow')" != "true" ]]; then
    echo "DENIED: Deployment policy rejected the image." >&2
    exit 1
fi

echo "ALLOWED: Signature, SBOM attestation and vulnerability checks passed."
