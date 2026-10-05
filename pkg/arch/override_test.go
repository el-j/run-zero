package arch

import (
	"testing"
)

func TestNativeArchOverride(t *testing.T) {
	// Mode "off" with default hostArch
	oOff, err := NewNativeArchOverride("off", "")
	if err != nil || oOff.AppliesTo("org/repo") {
		t.Fatalf("expected off mode not to apply")
	}
	if oOff.ArchFor("amd64", nil, "org/repo") != "amd64" {
		t.Errorf("expected amd64 unchanged when off")
	}

	// Mode "all" on arm64 host
	oAll, err := NewNativeArchOverride("all", "arm64")
	if err != nil || !oAll.AppliesTo("org/repo") {
		t.Fatalf("expected all mode to apply")
	}
	if oAll.ArchFor("amd64", nil, "org/repo") != "arm64" {
		t.Errorf("expected amd64 to become arm64 on arm64 host")
	}
	// Emulation label skips override
	if oAll.ArchFor("amd64", []string{"rosetta"}, "org/repo") != "amd64" {
		t.Errorf("expected rosetta label to preserve amd64")
	}

	// Mode "list"
	oList, err := NewNativeArchOverride("org/opted-in, other/repo", "arm64")
	if err != nil {
		t.Fatalf("unexpected list parse error: %v", err)
	}
	if !oList.AppliesTo("org/opted-in") || oList.AppliesTo("org/not-opted") {
		t.Errorf("unexpected applies to results for list mode")
	}

	// Non-arm64 host
	oIntel, _ := NewNativeArchOverride("all", "amd64")
	if oIntel.ArchFor("amd64", nil, "org/repo") != "amd64" {
		t.Errorf("expected amd64 on intel host")
	}

	// Invalid format
	if _, err := NewNativeArchOverride("invalid-no-slash", "arm64"); err == nil {
		t.Error("expected error for repo without slash")
	}

	// Defaults and normalization
	norm := NormalizeHostArch("x86_64")
	if norm != "amd64" {
		t.Errorf("expected amd64, got %s", norm)
	}
	normA := NormalizeHostArch("aarch64")
	if normA != "arm64" {
		t.Errorf("expected arm64, got %s", normA)
	}
}
