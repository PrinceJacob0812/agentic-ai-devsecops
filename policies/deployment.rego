package deployment

import rego.v1

default allow := false

allow if {
    input.signature_verified == true
    input.sbom_attestation_verified == true
    input.critical_count == 0
    regex.match(`@sha256:[a-f0-9]{64}$`, input.image_ref)
}
