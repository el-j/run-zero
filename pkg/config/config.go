package config

import (
	"strings"
)

// LoadConfig parses and validates daemon settings from an EnvLookup source.
func LoadConfig(env EnvLookup) (*Config, error) {
	if env == nil {
		env = OSEnv{}
	}

	token, _ := env.Lookup("ACCESS_TOKEN")
	if strings.TrimSpace(token) == "" {
		token, _ = env.Lookup("GITHUB_TOKEN")
	}

	owner, _ := env.Lookup("OWNER")
	org, _ := env.Lookup("ORG")

	repos, _ := env.Lookup("REPOS")
	if strings.TrimSpace(repos) == "" {
		repos, _ = env.Lookup("REPO")
	}

	autoDiscover, err := parseBool(env, "AUTO_DISCOVER_REPOS", true)
	if err != nil {
		return nil, err
	}

	activeDays, err := parseInt(env, "ACTIVE_REPO_DAYS", 60, 1, nil)
	if err != nil {
		return nil, err
	}

	discoveryInterval, err := parseInt(env, "DISCOVERY_INTERVAL", 900, 60, nil)
	if err != nil {
		return nil, err
	}

	opts, err := loadRunnerOptions(env)
	if err != nil {
		return nil, err
	}

	pollIntervalMax := 3600
	pollInterval, err := parseInt(env, "POLL_INTERVAL", 10, 1, &pollIntervalMax)
	if err != nil {
		return nil, err
	}

	rateLimitInterval, err := parseInt(env, "RATE_LIMIT_REFRESH_INTERVAL", 60, 10, nil)
	if err != nil {
		return nil, err
	}

	billingInterval, err := parseInt(env, "ACTIONS_BILLING_REFRESH_INTERVAL", 300, 30, nil)
	if err != nil {
		return nil, err
	}

	dashEnabled, err := parseBool(env, "DASHBOARD_ENABLED", true)
	if err != nil {
		return nil, err
	}

	dashPortMax := 65535
	dashPort, err := parseInt(env, "DASHBOARD_PORT", 49505, 0, &dashPortMax)
	if err != nil {
		return nil, err
	}

	dashHost, _ := env.Lookup("DASHBOARD_HOST")
	if strings.TrimSpace(dashHost) == "" {
		dashHost = "127.0.0.1"
	}

	repoPriority, _ := env.Lookup("REPO_PRIORITY")

	return &Config{
		AccessToken:                   strings.TrimSpace(token),
		Owner:                         strings.TrimSpace(owner),
		Org:                           strings.TrimSpace(org),
		ReposConfig:                   strings.TrimSpace(repos),
		AutoDiscover:                  autoDiscover,
		ActiveDays:                    activeDays,
		DiscoveryInterval:             discoveryInterval,
		RunnerBackend:                 opts.backend,
		AutoRouteVM:                   opts.autoRouteVM,
		RunnerArch:                    opts.arch,
		ProxiesEnabled:                opts.proxies,
		CacheEnabled:                  opts.cache,
		HostCacheDir:                  opts.hostCache,
		MinRunners:                    opts.minRunners,
		MaxRunners:                    opts.maxRunners,
		PollInterval:                  pollInterval,
		RateLimitRefreshInterval:      rateLimitInterval,
		ActionsBillingRefreshInterval: billingInterval,
		BusyTimeoutSeconds:            opts.busyTimeout,
		CleanupOnShutdown:             opts.cleanup,
		NativeArchOverride:            opts.nativeArchOverride,
		DashboardEnabled:              dashEnabled,
		DashboardPort:                 dashPort,
		DashboardHost:                 strings.TrimSpace(dashHost),
		RepoPriority:                  strings.TrimSpace(repoPriority),
		RunnerCPUs:                    opts.runnerCPUs,
		RunnerMemory:                  opts.runnerMemory,
	}, nil
}
