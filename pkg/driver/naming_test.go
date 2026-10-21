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

func TestRunnerNames_RespectGitHub64CharLimit(t *testing.T) {
	job := JobScopedRunnerName("el-j/landing.inquam-services", "amd64", 38156662479, 114520936456, "734f0c")
	manual := ManualRunnerName("el-j/landing.inquam-services", "amd64", "734f0c")
	for _, n := range []string{job, manual} {
		if len(n) > 64 {
			t.Fatalf("runner name %q is %d chars, GitHub allows 64", n, len(n))
		}
		if !strings.HasSuffix(n, "-734f0c") {
			t.Fatalf("entropy suffix lost in %q", n)
		}
	}
}

func TestResolveRepoFromMachineName_RecoversLossyOrbStackRepo(t *testing.T) {
	repos := []string{"el-j/herbful", "el-j/landing.inquam-services", "el-j/run-zero"}
	cases := map[string]string{
		"runzero-j118881070610-r39490761518-amd64-el-j-landing-in-e4efbc":         "el-j/landing.inquam-services",
		"runzero-j119267842113-r39613374904-amd64-el-j-herbful-516143":            "el-j/herbful",
		orbstackMachineName(ManualRunnerName("el-j/run-zero", "arm64", "abc123")): "el-j/run-zero",
	}
	for name, want := range cases {
		if got := ResolveRepoFromMachineName(name, repos); got != want {
			t.Errorf("ResolveRepoFromMachineName(%q) = %q, want %q", name, got, want)
		}
	}
	if got := ResolveRepoFromMachineName("runzero-j1-r2-amd64-other-repo-abc123", repos); got != "" {
		t.Errorf("expected no match for untracked repo, got %q", got)
	}
}
