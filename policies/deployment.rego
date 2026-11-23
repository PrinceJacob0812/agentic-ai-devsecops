package deployment

import rego.v1

default allow := false

allow if {
    input.signature_verified == true
    input.sbom_attestation_verified == true
    input.critical_count == 0
    regex.match(`@sha256:[a-f0-9]{64}$`, input.image_ref)
}

deny contains "image signature was not verified" if {
    input.signature_verified != true
}

deny contains "SBOM attestation was not verified" if {
    input.sbom_attestation_verified != true
}

deny contains "one or more Critical vulnerabilities were found" if {
    input.critical_count > 0
}

deny contains "image reference must be pinned by a SHA-256 digest" if {
    not regex.match(`@sha256:[a-f0-9]{64}$`, input.image_ref)
}
