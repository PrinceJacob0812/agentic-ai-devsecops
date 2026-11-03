package deployment_test

import rego.v1
import data.deployment

test_allow_valid_image if {
    deployment.allow with input as {
        "image_ref": "ghcr.io/example/app@sha256:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
        "signature_verified": true,
        "sbom_attestation_verified": true,
        "critical_count": 0
    }
}

test_deny_critical_vulnerability if {
    result := deployment.allow with input as {
        "image_ref": "ghcr.io/example/app@sha256:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
        "signature_verified": true,
        "sbom_attestation_verified": true,
        "critical_count": 1
    }
    result == false
}

test_deny_invalid_signature if {
    result := deployment.allow with input as {
        "image_ref": "ghcr.io/example/app@sha256:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
        "signature_verified": false,
        "sbom_attestation_verified": true,
        "critical_count": 0
    }
    result == false
}

test_deny_invalid_sbom_attestation if {
    result := deployment.allow with input as {
        "image_ref": "ghcr.io/example/app@sha256:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
        "signature_verified": true,
        "sbom_attestation_verified": false,
        "critical_count": 0
    }
    result == false
}

test_deny_invalid_image_digest if {
    result := deployment.allow with input as {
        "image_ref": "ghcr.io/example/app:latest",
        "signature_verified": true,
        "sbom_attestation_verified": true,
        "critical_count": 0
    }
    result == false
}
