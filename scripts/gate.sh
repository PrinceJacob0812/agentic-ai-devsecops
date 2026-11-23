#!/usr/bin/env bash
set -euo pipefail

: "${IMAGE_REF:?Set IMAGE_REF to an image reference pinned by SHA-256 digest}"
: "${IDENTITY:?Set IDENTITY to the expected signing certificate identity}"
: "${GRYPE_JSON:?Set GRYPE_JSON to the Grype JSON report generated from the verified SBOM attestation}"

ISSUER="${ISSUER:-https://token.actions.githubusercontent.com}"
POLICY_FILE="policies/deployment.rego"

for tool in cosign opa jq; do
    if ! command -v "$tool" >/dev/null 2>&1; then
        echo "ERROR: Required tool not found: $tool" >&2
        exit 1
    fi
done

if [[ ! -f "$POLICY_FILE" || ! -f "$GRYPE_JSON" ]]; then
    echo "ERROR: Policy or Grype report file not found." >&2
    exit 1
fi

if ! jq -e '.matches | type == "array"' "$GRYPE_JSON" >/dev/null; then
    echo "ERROR: Invalid Grype JSON report." >&2
    exit 1
fi

TMP_DIR="$(mktemp -d)"
trap 'rm -rf "$TMP_DIR"' EXIT

echo "[1/4] Verifying image signature..."
if ! cosign verify \
    --certificate-identity "$IDENTITY" \
    --certificate-oidc-issuer "$ISSUER" \
    "$IMAGE_REF" > "$TMP_DIR/signature.json" 2>"$TMP_DIR/signature.err"; then
    echo "DENIED: Image signature verification failed." >&2
    cat "$TMP_DIR/signature.err" >&2
    exit 1
fi

echo "[2/4] Verifying signed CycloneDX SBOM attestation..."
if ! cosign verify-attestation \
    --type cyclonedx \
    --certificate-identity "$IDENTITY" \
    --certificate-oidc-issuer "$ISSUER" \
    "$IMAGE_REF" > "$TMP_DIR/attestation.json" 2>"$TMP_DIR/attestation.err"; then
    echo "DENIED: SBOM attestation verification failed." >&2
    cat "$TMP_DIR/attestation.err" >&2
    exit 1
fi

if [[ ! -s "$TMP_DIR/attestation.json" ]]; then
    echo "DENIED: SBOM attestation is empty." >&2
    exit 1
fi

echo "[3/4] Checking Grype vulnerability report..."
CRITICAL_COUNT="$(jq '[.matches[]? | select(.vulnerability.severity == "Critical")] | length' "$GRYPE_JSON")"
HIGH_COUNT="$(jq '[.matches[]? | select(.vulnerability.severity == "High")] | length' "$GRYPE_JSON")"

echo "Critical vulnerabilities found: $CRITICAL_COUNT"
echo "High vulnerabilities found: $HIGH_COUNT (warn-only; see issue #29 for agreed blocking target)"

jq -n \
    --arg image_ref "$IMAGE_REF" \
    --argjson critical_count "$CRITICAL_COUNT" \
    '{image_ref: $image_ref, signature_verified: true, sbom_attestation_verified: true, critical_count: $critical_count}' \
    > "$TMP_DIR/input.json"

echo "[4/4] Evaluating OPA deployment policy..."
if ! opa eval --format json \
    --data "$POLICY_FILE" \
    --input "$TMP_DIR/input.json" \
    'data.deployment.allow' > "$TMP_DIR/allow.json"; then
    echo "DENIED: OPA policy evaluation failed." >&2
    exit 1
fi

OPA_ALLOWED="$(jq -r '.result[0].expressions[0].value // false' "$TMP_DIR/allow.json")"
if [[ "$OPA_ALLOWED" != "true" ]]; then
    echo "DENIED: Deployment policy rejected the image. Reason(s):" >&2
    if opa eval --format json --data "$POLICY_FILE" --input "$TMP_DIR/input.json" 'data.deployment.deny' > "$TMP_DIR/deny.json"; then
        jq -r '.result[0].expressions[0].value[]? // empty' "$TMP_DIR/deny.json" | sed 's/^/  - /' >&2
    fi
    exit 1
fi

echo "ALLOWED: Signature, SBOM attestation and vulnerability checks passed."
