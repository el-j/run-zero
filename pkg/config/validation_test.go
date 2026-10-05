package config

import (
	"testing"
)

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
