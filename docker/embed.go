package docker

import _ "embed"

// ProvisionToolchainScript contains the shared toolchain provisioning bash script.
//
//go:embed provision-toolchain.sh
var ProvisionToolchainScript string
