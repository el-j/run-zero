package main

import (
	"bytes"
	"os"
	"path/filepath"
	"strings"
	"testing"
)

func TestCLI_Version(t *testing.T) {
	var stdout, stderr bytes.Buffer
	code := run([]string{"-version"}, &stdout, &stderr)
	if code != 0 {
		t.Fatalf("expected 0, got %d", code)
	}
	if !strings.Contains(stdout.String(), "runzero v") {
		t.Errorf("expected version output, got: %s", stdout.String())
	}
}

func TestCLI_ParseError(t *testing.T) {
	var stdout, stderr bytes.Buffer
	code := run([]string{"-unknown-flag"}, &stdout, &stderr)
	if code != 1 {
		t.Fatalf("expected 1 for parse error, got %d", code)
	}
}

func TestCLI_InvalidConfig(t *testing.T) {
	tmpDir := t.TempDir()
	badEnv := filepath.Join(tmpDir, "bad.env")
	_ = os.WriteFile(badEnv, []byte("MAX_RUNNERS=invalid_int\n"), 0644)

	var stdout, stderr bytes.Buffer
	code := run([]string{"-config", badEnv}, &stdout, &stderr)
	if code != 1 {
		t.Fatalf("expected 1 for invalid config, got %d", code)
	}
	if !strings.Contains(stderr.String(), "[Config Error]") {
		t.Errorf("expected [Config Error] in output, got: %s", stderr.String())
	}
}

func TestCLI_UnreadableConfig(t *testing.T) {
	tmpDir := t.TempDir()
	unreadable := filepath.Join(tmpDir, "unreadable.env")
	_ = os.WriteFile(unreadable, []byte("FOO=bar"), 0000)

	var stdout, stderr bytes.Buffer
	code := run([]string{"-config", unreadable}, &stdout, &stderr)
	if code != 0 && code != 1 {
		t.Errorf("unexpected code: %d", code)
	}
}

func TestCLI_DaemonStartupFailure(t *testing.T) {
	tmpDir := t.TempDir()
	envPath := filepath.Join(tmpDir, ".env")
	_ = os.WriteFile(envPath, []byte("DASHBOARD_HOST=999.999.999.999\n"), 0644)

	var stdout, stderr bytes.Buffer
	code := run([]string{"-config", envPath}, &stdout, &stderr)
	if code != 1 {
		t.Fatalf("expected 1 for daemon error, got %d", code)
	}
	if !strings.Contains(stderr.String(), "[Daemon Error]") {
		t.Errorf("expected [Daemon Error] in stderr, got: %s", stderr.String())
	}
}

func TestCLI_Doctor(t *testing.T) {
	var stdout, stderr bytes.Buffer
	code := run([]string{"doctor", "-timeout", "500ms"}, &stdout, &stderr)
	if code != 0 && code != 1 {
		t.Fatalf("unexpected code from doctor: %d", code)
	}
	if !strings.Contains(stdout.String(), "runzero Doctor Diagnostics") {
		t.Errorf("expected doctor diagnostics header, got: %s", stdout.String())
	}
}

func TestCLI_DoctorParseError(t *testing.T) {
	var stdout, stderr bytes.Buffer
	code := run([]string{"doctor", "-badflag"}, &stdout, &stderr)
	if code != 1 {
		t.Fatalf("expected 1, got %d", code)
	}
}

func TestCLI_BridgeParseError(t *testing.T) {
	var stdout, stderr bytes.Buffer
	code := run([]string{"bridge", "-badflag"}, &stdout, &stderr)
	if code != 1 {
		t.Fatalf("expected 1, got %d", code)
	}
}

func TestCLI_BuildVMBase(t *testing.T) {
	var stdout, stderr bytes.Buffer
	code := run([]string{"build-vm-base", "-badflag"}, &stdout, &stderr)
	if code != 1 {
		t.Fatalf("expected 1, got %d", code)
	}

	stdout.Reset()
	stderr.Reset()
	code = run([]string{"build-vm-base", "-arch", "invalid_arch"}, &stdout, &stderr)
	if code != 1 {
		t.Fatalf("expected 1 for invalid arch, got %d", code)
	}
}
