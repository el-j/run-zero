package config

import (
	"os"
	"path/filepath"
	"strings"
	"testing"
)

func TestLoadConfig_Defaults(t *testing.T) {
	env := MapEnv{}
	cfg, err := LoadConfig(env)
	if err != nil {
		t.Fatalf("unexpected error loading defaults: %v", err)
	}

	if cfg.AutoDiscover != true {
		t.Errorf("expected AutoDiscover true, got %v", cfg.AutoDiscover)
	}
	if cfg.ActiveDays != 60 {
		t.Errorf("expected ActiveDays 60, got %d", cfg.ActiveDays)
	}
	if cfg.DiscoveryInterval != 900 {
		t.Errorf("expected DiscoveryInterval 900, got %d", cfg.DiscoveryInterval)
	}
	if cfg.RunnerBackend != "auto" {
		t.Errorf("expected RunnerBackend 'auto', got %s", cfg.RunnerBackend)
	}
	if cfg.AutoRouteVM != true {
		t.Errorf("expected AutoRouteVM true, got %v", cfg.AutoRouteVM)
	}
	if cfg.RunnerArch != "both" {
		t.Errorf("expected RunnerArch 'both', got %s", cfg.RunnerArch)
	}
	if cfg.MinRunners != 0 {
		t.Errorf("expected MinRunners 0, got %d", cfg.MinRunners)
	}
	if cfg.MaxRunners != 4 {
		t.Errorf("expected MaxRunners 4, got %d", cfg.MaxRunners)
	}
	if cfg.PollInterval != 10 {
		t.Errorf("expected PollInterval 10, got %d", cfg.PollInterval)
	}
	if cfg.DashboardPort != 49505 {
		t.Errorf("expected DashboardPort 49505, got %d", cfg.DashboardPort)
	}
	if cfg.DashboardHost != "127.0.0.1" {
		t.Errorf("expected DashboardHost '127.0.0.1', got %s", cfg.DashboardHost)
	}
	if cfg.NativeArchOverride != "off" {
		t.Errorf("expected NativeArchOverride 'off', got %s", cfg.NativeArchOverride)
	}
}

func TestLoadConfig_TokenAndRepoFallbacks(t *testing.T) {
	env := MapEnv{
		"GITHUB_TOKEN": "gh_fallback_token",
		"REPO":         "org/fallback-repo",
	}
	cfg, err := LoadConfig(env)
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if cfg.AccessToken != "gh_fallback_token" {
		t.Errorf("expected AccessToken 'gh_fallback_token', got %s", cfg.AccessToken)
	}
	if cfg.ReposConfig != "org/fallback-repo" {
		t.Errorf("expected ReposConfig 'org/fallback-repo', got %s", cfg.ReposConfig)
	}

	// Primary ACCESS_TOKEN takes precedence
	env2 := MapEnv{
		"ACCESS_TOKEN": "primary_token",
		"GITHUB_TOKEN": "ignored_token",
		"REPOS":        "org/repo1,org/repo2",
		"REPO":         "ignored/repo",
	}
	cfg2, err := LoadConfig(env2)
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if cfg2.AccessToken != "primary_token" {
		t.Errorf("expected primary_token, got %s", cfg2.AccessToken)
	}
	if cfg2.ReposConfig != "org/repo1,org/repo2" {
		t.Errorf("expected org/repo1,org/repo2, got %s", cfg2.ReposConfig)
	}
}

func TestLoadConfig_ArchAliases(t *testing.T) {
	tests := []struct {
		input    string
		expected string
	}{
		{"arm64", "arm64"},
		{"aarch64", "arm64"},
		{"amd64", "amd64"},
		{"x64", "amd64"},
		{"x86_64", "amd64"},
		{"both", "both"},
	}

	for _, tt := range tests {
		env := MapEnv{"RUNNER_ARCH": tt.input}
		cfg, err := LoadConfig(env)
		if err != nil {
			t.Fatalf("unexpected error for arch %s: %v", tt.input, err)
		}
		if cfg.RunnerArch != tt.expected {
			t.Errorf("arch %s: expected %s, got %s", tt.input, tt.expected, cfg.RunnerArch)
		}
	}

	badEnv := MapEnv{"RUNNER_ARCH": "invalid-arch"}
	_, err := LoadConfig(badEnv)
	if err == nil {
		t.Fatal("expected error for invalid RUNNER_ARCH, got nil")
	}
}

func TestLoadConfig_ValidationErrors(t *testing.T) {
	tests := []struct {
		name string
		env  MapEnv
	}{
		{"min > max runners", MapEnv{"MIN_RUNNERS": "5", "MAX_RUNNERS": "3"}},
		{"bad integer", MapEnv{"MAX_RUNNERS": "four"}},
		{"int below min", MapEnv{"MAX_RUNNERS": "0"}},
		{"int above max", MapEnv{"POLL_INTERVAL": "5000"}},
		{"bad boolean", MapEnv{"AUTO_DISCOVER_REPOS": "maybe"}},
		{"bad backend", MapEnv{"RUNNER_BACKEND": "kubernetes"}},
		{"bad dashboard port", MapEnv{"DASHBOARD_PORT": "70000"}},
		{"negative dashboard port", MapEnv{"DASHBOARD_PORT": "-1"}},
		{"bad active days", MapEnv{"ACTIVE_REPO_DAYS": "0"}},
		{"bad discovery interval", MapEnv{"DISCOVERY_INTERVAL": "10"}},
		{"bad auto route vm", MapEnv{"AUTO_ROUTE_VM": "invalid"}},
		{"bad proxies enabled", MapEnv{"PROXIES_ENABLED": "invalid"}},
		{"bad cache enabled", MapEnv{"CACHE_ENABLED": "invalid"}},
		{"bad min runners", MapEnv{"MIN_RUNNERS": "-1"}},
		{"bad rate limit interval", MapEnv{"RATE_LIMIT_REFRESH_INTERVAL": "1"}},
		{"bad billing interval", MapEnv{"ACTIONS_BILLING_REFRESH_INTERVAL": "5"}},
		{"bad busy timeout", MapEnv{"RUNNER_BUSY_TIMEOUT_SECONDS": "10"}},
		{"bad cleanup on shutdown", MapEnv{"CLEANUP_RUNNERS_ON_SHUTDOWN": "nope"}},
		{"bad dashboard enabled", MapEnv{"DASHBOARD_ENABLED": "not-bool"}},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			_, err := LoadConfig(tt.env)
			if err == nil {
				t.Fatalf("expected error for %s, got nil", tt.name)
			}
			cfgErr, ok := err.(*ConfigError)
			if !ok {
				t.Errorf("expected *ConfigError, got %T: %v", err, err)
			}
			if cfgErr.Error() == "" {
				t.Errorf("expected non-empty error message")
			}
		})
	}
}

func TestLoadConfig_Booleans(t *testing.T) {
	trues := []string{"true", "1", "yes", "on"}
	for _, val := range trues {
		env := MapEnv{"PROXIES_ENABLED": val}
		cfg, err := LoadConfig(env)
		if err != nil || !cfg.ProxiesEnabled {
			t.Errorf("expected true for %s, got err=%v, val=%v", val, err, cfg.ProxiesEnabled)
		}
	}

	falses := []string{"false", "0", "no", "off"}
	for _, val := range falses {
		env := MapEnv{"PROXIES_ENABLED": val}
		cfg, err := LoadConfig(env)
		if err != nil || cfg.ProxiesEnabled {
			t.Errorf("expected false for %s, got err=%v, val=%v", val, err, cfg.ProxiesEnabled)
		}
	}
}

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

	// Missing file should return empty map, no error
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

	// Unreadable file causes os.Open error that is not ErrNotExist
	unreadable := filepath.Join(tmpDir, "unreadable.env")
	if err := os.WriteFile(unreadable, []byte("FOO=bar"), 0000); err == nil {
		_, err = LoadDotEnvFile(unreadable)
		if err == nil {
			t.Log("os.Open succeeded on unreadable file (e.g. root)")
		}
	}
}

func TestChoice_EmptyWhitespace(t *testing.T) {
	env1 := MapEnv{"RUNNER_BACKEND": "   "}
	cfg1, err := LoadConfig(env1)
	if err != nil || cfg1.RunnerBackend != "auto" {
		t.Fatalf("expected auto default for whitespace, got %v, %v", cfg1.RunnerBackend, err)
	}

	env2 := MapEnv{"RUNNER_BACKEND": ""}
	cfg2, err := LoadConfig(env2)
	if err != nil || cfg2.RunnerBackend != "auto" {
		t.Fatalf("expected auto default for empty string, got %v, %v", cfg2.RunnerBackend, err)
	}

	env3 := MapEnv{"RUNNER_ARCH": ""}
	cfg3, err := LoadConfig(env3)
	if err != nil || cfg3.RunnerArch != "both" {
		t.Fatalf("expected both default for empty arch, got %v, %v", cfg3.RunnerArch, err)
	}

	env4 := MapEnv{"RUNNER_BACKEND": "DOCKER"}
	cfg4, err := LoadConfig(env4)
	if err != nil || cfg4.RunnerBackend != "docker" {
		t.Fatalf("expected docker for valid choice, got %v, %v", cfg4.RunnerBackend, err)
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

	// Test LoadConfig with nil env uses OSEnv
	cfg, err := LoadConfig(nil)
	if err != nil {
		t.Fatalf("LoadConfig(nil) error: %v", err)
	}
	if cfg == nil {
		t.Fatal("expected non-nil config")
	}
}
