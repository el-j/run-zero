package arch

import (
	"fmt"
	"runtime"
	"strings"
)

const (
	ModeOff = "off"
	ModeAll = "all"
)

var emulationLabels = map[string]bool{
	"rosetta": true,
	"x86_64":  true,
}

// NormalizeHostArch converts runtime.GOARCH spellings to standard arm64/amd64.
func NormalizeHostArch(arch string) string {
	a := strings.ToLower(strings.TrimSpace(arch))
	if a == "aarch64" || a == "arm64" {
		return "arm64"
	}
	if a == "x86_64" || a == "amd64" || a == "x64" {
		return "amd64"
	}
	return a
}

// NativeArchOverride manages dynamic amd64 -> arm64 translation routing on Apple Silicon hosts.
type NativeArchOverride struct {
	Mode     string
	Repos    map[string]bool
	HostArch string
}

// NewNativeArchOverride parses configuration string ("off", "all", or comma-separated repos).
func NewNativeArchOverride(raw string, hostArch string) (*NativeArchOverride, error) {
	val := strings.ToLower(strings.TrimSpace(raw))
	if val == "" {
		val = ModeOff
	}

	if hostArch == "" {
		hostArch = NormalizeHostArch(runtime.GOARCH)
	} else {
		hostArch = NormalizeHostArch(hostArch)
	}

	if val == ModeOff || val == ModeAll {
		return &NativeArchOverride{
			Mode:     val,
			Repos:    make(map[string]bool),
			HostArch: hostArch,
		}, nil
	}

	reposMap := make(map[string]bool)
	parts := strings.Split(val, ",")
	for _, p := range parts {
		r := strings.TrimSpace(p)
		if r == "" {
			continue
		}
		if strings.Count(r, "/") != 1 || strings.HasPrefix(r, "/") || strings.HasSuffix(r, "/") {
			return nil, fmt.Errorf("NATIVE_ARCH_OVERRIDE=%q must be off, all, or comma-separated owner/repo names", raw)
		}
		reposMap[r] = true
	}

	return &NativeArchOverride{
		Mode:     "list",
		Repos:    reposMap,
		HostArch: hostArch,
	}, nil
}

// AppliesTo reports whether the repository opted into native architecture dispatch.
func (o *NativeArchOverride) AppliesTo(repo string) bool {
	if o.Mode == ModeAll {
		return true
	}
	if o.Mode == ModeOff {
		return false
	}
	return o.Repos[strings.ToLower(strings.TrimSpace(repo))]
}

// ArchFor determines the execution architecture for a job.
func (o *NativeArchOverride) ArchFor(jobArch string, jobLabels []string, repo string) string {
	normJobArch := NormalizeHostArch(jobArch)
	if normJobArch != "amd64" || o.HostArch != "arm64" || !o.AppliesTo(repo) {
		return jobArch
	}

	for _, l := range jobLabels {
		if emulationLabels[strings.ToLower(strings.TrimSpace(l))] {
			return jobArch
		}
	}
	return "arm64"
}
