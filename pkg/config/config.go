package config

import (
	"strings"
)

// LoadConfig parses and validates daemon settings from an EnvLookup source.
// Settings are validated in a fixed order, so the first invalid one is reported.
func LoadConfig(env EnvLookup) (*Config, error) {
	if env == nil {
		env = OSEnv{}
	}
	cfg := &Config{}
	for _, load := range []func(EnvLookup, *Config) error{
		loadGitHubSettings,
		loadRunnerSettings,
		loadIntervalSettings,
		loadDashboardSettings,
	} {
		if err := load(env, cfg); err != nil {
			return nil, err
		}
	}
	loadProviderSettings(env, cfg)
	return cfg, nil
}

// lookupTrimmed returns the trimmed value of key, or "" when unset.
func lookupTrimmed(env EnvLookup, key string) string {
	v, _ := env.Lookup(key)
	return strings.TrimSpace(v)
}

// lookupFirst returns the first non-blank value among keys.
func lookupFirst(env EnvLookup, keys ...string) string {
	for _, k := range keys {
		if v := lookupTrimmed(env, k); v != "" {
			return v
		}
	}
	return ""
}

func loadGitHubSettings(env EnvLookup, cfg *Config) error {
	cfg.AccessToken = lookupFirst(env, "ACCESS_TOKEN", "GITHUB_TOKEN")
	cfg.Owner = lookupTrimmed(env, "OWNER")
	cfg.Org = lookupTrimmed(env, "ORG")
	cfg.ReposConfig = lookupFirst(env, "REPOS", "REPO")
	cfg.RepoPriority = lookupTrimmed(env, "REPO_PRIORITY")

	var err error
	if cfg.AutoDiscover, err = parseBool(env, "AUTO_DISCOVER_REPOS", true); err != nil {
		return err
	}
	if cfg.ActiveDays, err = parseInt(env, "ACTIVE_REPO_DAYS", 60, 1, nil); err != nil {
		return err
	}
	cfg.DiscoveryInterval, err = parseInt(env, "DISCOVERY_INTERVAL", 900, 60, nil)
	return err
}

func loadRunnerSettings(env EnvLookup, cfg *Config) error {
	opts, err := loadRunnerOptions(env)
	if err != nil {
		return err
	}
	cfg.RunnerBackend = opts.backend
	cfg.AutoRouteVM = opts.autoRouteVM
	cfg.VMTriggerLabels = opts.vmTriggerLabels
	cfg.RunnerArch = opts.arch
	cfg.ProxiesEnabled = opts.proxies
	cfg.CacheEnabled = opts.cache
	cfg.HostCacheDir = opts.hostCache
	cfg.MinRunners = opts.minRunners
	cfg.MaxRunners = opts.maxRunners
	cfg.BusyTimeoutSeconds = opts.busyTimeout
	cfg.CleanupOnShutdown = opts.cleanup
	cfg.NativeArchOverride = opts.nativeArchOverride
	cfg.RunnerCPUs = opts.runnerCPUs
	cfg.RunnerMemory = opts.runnerMemory
	return nil
}

func loadIntervalSettings(env EnvLookup, cfg *Config) error {
	pollIntervalMax := 3600
	var err error
	if cfg.PollInterval, err = parseInt(env, "POLL_INTERVAL", 10, 1, &pollIntervalMax); err != nil {
		return err
	}
	if cfg.RateLimitRefreshInterval, err = parseInt(env, "RATE_LIMIT_REFRESH_INTERVAL", 60, 10, nil); err != nil {
		return err
	}
	cfg.ActionsBillingRefreshInterval, err = parseInt(env, "ACTIONS_BILLING_REFRESH_INTERVAL", 300, 30, nil)
	return err
}

func loadDashboardSettings(env EnvLookup, cfg *Config) error {
	var err error
	if cfg.DashboardEnabled, err = parseBool(env, "DASHBOARD_ENABLED", true); err != nil {
		return err
	}
	dashPortMax := 65535
	if cfg.DashboardPort, err = parseInt(env, "DASHBOARD_PORT", 49505, 0, &dashPortMax); err != nil {
		return err
	}
	cfg.DashboardHost = lookupTrimmed(env, "DASHBOARD_HOST")
	if cfg.DashboardHost == "" {
		cfg.DashboardHost = "127.0.0.1"
	}
	return nil
}

func loadProviderSettings(env EnvLookup, cfg *Config) {
	cfg.GitLabURL = lookupTrimmed(env, "GITLAB_URL")
	cfg.GitLabToken = lookupTrimmed(env, "GITLAB_TOKEN")
	cfg.GitLabGroup = lookupTrimmed(env, "GITLAB_GROUP")
	cfg.GitLabProjects = lookupTrimmed(env, "GITLAB_PROJECTS")
	cfg.ProvidersConfigFile = lookupTrimmed(env, "PROVIDERS_CONFIG")
}
