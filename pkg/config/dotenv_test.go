package config

import (
	"os"
	"path/filepath"
	"strings"
	"testing"
)

func TestEnv_DotEnvParser(t *testing.T) {
	raw := `
# Comment line
export ACCESS_TOKEN=token123
OWNER="my-org"
POLL_INTERVAL='15'
INVALID_LINE_NO_EQUALS
EMPTY_VAL=
`
	env, err := ParseDotEnv(strings.NewReader(raw))
	if err != nil {
		t.Fatalf("ParseDotEnv failed: %v", err)
	}

	if env["ACCESS_TOKEN"] != "token123" {
		t.Errorf("expected token123, got %s", env["ACCESS_TOKEN"])
	}
	if env["OWNER"] != "my-org" {
		t.Errorf("expected my-org, got %s", env["OWNER"])
	}
	if env["POLL_INTERVAL"] != "15" {
		t.Errorf("expected 15, got %s", env["POLL_INTERVAL"])
	}
	if env["EMPTY_VAL"] != "" {
		t.Errorf("expected empty string, got %s", env["EMPTY_VAL"])
	}
}

func TestEnv_LoadDotEnvFile(t *testing.T) {
	tmpDir := t.TempDir()
	envPath := filepath.Join(tmpDir, ".env")

	missing, err := LoadDotEnvFile(filepath.Join(tmpDir, "does-not-exist.env"))
	if err != nil || len(missing) != 0 {
		t.Fatalf("expected empty map for missing file, got err=%v, map=%v", err, missing)
	}

	content := "DASHBOARD_PORT=8080\nOWNER=sample-owner\n"
	if err := os.WriteFile(envPath, []byte(content), 0644); err != nil {
		t.Fatalf("failed to write test file: %v", err)
	}

	loaded, err := LoadDotEnvFile(envPath)
	if err != nil {
		t.Fatalf("LoadDotEnvFile error: %v", err)
	}
	if loaded["DASHBOARD_PORT"] != "8080" {
		t.Errorf("expected 8080, got %s", loaded["DASHBOARD_PORT"])
	}

	unreadable := filepath.Join(tmpDir, "unreadable.env")
	if err := os.WriteFile(unreadable, []byte("FOO=bar"), 0000); err == nil {
		_, _ = LoadDotEnvFile(unreadable)
	}
}

func TestEnv_CompositeAndOS(t *testing.T) {
	primary := MapEnv{"PORT": "9000", "EMPTY": ""}
	secondary := MapEnv{"PORT": "8000", "HOST": "localhost", "EMPTY": "fallback"}

	comp := CompositeEnv{Primary: primary, Secondary: secondary}

	if val, ok := comp.Lookup("PORT"); !ok || val != "9000" {
		t.Errorf("expected 9000 from primary, got %s", val)
	}
	if val, ok := comp.Lookup("HOST"); !ok || val != "localhost" {
		t.Errorf("expected localhost from secondary, got %s", val)
	}
	if val, ok := comp.Lookup("EMPTY"); !ok || val != "fallback" {
		t.Errorf("expected fallback when primary is empty, got %s", val)
	}
	if _, ok := comp.Lookup("NONEXISTENT"); ok {
		t.Errorf("expected not found for nonexistent key")
	}

	osEnv := OSEnv{}
	_, _ = osEnv.Lookup("PATH")

	cfg, err := LoadConfig(nil)
	if err != nil || cfg == nil {
		t.Fatalf("LoadConfig(nil) error: %v", err)
	}
}
