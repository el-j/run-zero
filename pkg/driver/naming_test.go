package driver

import (
	"strings"
	"testing"
)

func TestJobScopedRunnerNameContainsJobAndRun(t *testing.T) {
	name := JobScopedRunnerName("el-j/herbful", "amd64", 101, 202, "063160")
	if !strings.Contains(name, "j202") || !strings.Contains(name, "r101") {
		t.Fatalf("expected job and run identifiers in name, got %q", name)
	}
	if !strings.Contains(name, "el-j__herbful") {
		t.Fatalf("expected encoded repo in name, got %q", name)
	}
	if !strings.HasPrefix(name, "runzero-") {
		t.Fatalf("expected runzero prefix, got %q", name)
	}
}

func TestManualRunnerNameUsesManualPrefix(t *testing.T) {
	name := ManualRunnerName("el-j/herbful", "arm64", "abc123")
	if !strings.Contains(name, "manual") {
		t.Fatalf("expected manual marker in name, got %q", name)
	}
	if !strings.Contains(name, "el-j__herbful") {
		t.Fatalf("expected encoded repo in name, got %q", name)
	}
}
