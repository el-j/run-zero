package config

import (
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
