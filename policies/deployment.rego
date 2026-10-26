package deployment

import rego.v1

default allow := false

allow if {
    input.signature_verified == true
    input.sbom_attestation_verified == true
    regex.match(`@sha256:[a-f0-9]{64}$`, input.image_ref)
}
