package driver

import (
	"runtime"
	"strings"
)

// Backend kinds a runner can run on.
const (
	KindDocker    = "docker"
	KindOrbStack  = "orbstack"
	KindWSL2      = "wsl2"
	KindMultipass = "multipass"
)

// BackendKind folds the backend names accepted by RUNNER_BACKEND / VM_BACKEND
// into a backend kind. "" means auto (no fixed backend); "vm" means whichever
// VM engine is configured.
func BackendKind(name string) string {
	switch strings.ToLower(strings.TrimSpace(name)) {
	case "", "auto", "hybrid":
		return ""
	case "docker", "container":
		return KindDocker
	case "orb", "orbstack", "orbstack-vm", "vm-orb":
		return KindOrbStack
	case "wsl", "wsl2", "windows":
		return KindWSL2
	case "multipass", "canonical-multipass":
		return KindMultipass
	case "vm":
		return "vm"
	}
	return ""
}

// IsVMBackend reports whether name selects a VM engine rather than containers.
func IsVMBackend(name string) bool {
	switch BackendKind(name) {
	case KindOrbStack, KindWSL2, KindMultipass, "vm":
		return true
	}
	return false
}

// hostArch is the host CPU as a runner arch. Multipass and WSL2 only run guests
// of the host's own architecture.
func hostArch() string { return normalizeArch(runtime.GOARCH) }

func normalizeArch(a string) string {
	switch strings.ToLower(a) {
	case "amd64", "x64", "x86_64":
		return "amd64"
	}
	return "arm64"
}
