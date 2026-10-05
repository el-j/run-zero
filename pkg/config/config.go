package config

import (
	"fmt"
	"strings"
)

// Config holds the validated configuration for the RunZero daemon engine.
type Config struct {
	AccessToken                  string
	Owner                        string
	Org                          string
	ReposConfig                  string
	AutoDiscover                 bool
	ActiveDays                   int
	DiscoveryInterval            int
	RunnerBackend                string
	AutoRouteVM                  bool
	RunnerArch                   string
	ProxiesEnabled               bool
	CacheEnabled                 bool
	HostCacheDir                 string
	MinRunners                   int
	MaxRunners                   int
	PollInterval                 int
	RateLimitRefreshInterval     int
	ActionsBillingRefreshInterval int
	BusyTimeoutSeconds           int
	CleanupOnShutdown            bool
	NativeArchOverride           string
	DashboardEnabled             bool
	DashboardPort                int
	DashboardHost                string
	RepoPriority                 string
}

// LoadConfig parses and validates daemon settings from an EnvLookup source.
func LoadConfig(env EnvLookup) (*Config, error) {
	if env == nil {
		env = OSEnv{}
	}

	token, _ := env.Lookup("ACCESS_TOKEN")
	if strings.TrimSpace(token) == "" {
		token, _ = env.Lookup("GITHUB_TOKEN")
	}
	token = strings.TrimSpace(token)

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

	backend, err := parseChoice(env, "RUNNER_BACKEND", "auto", validBackends)
	if err != nil {
		return nil, err
	}

	autoRouteVM, err := parseBool(env, "AUTO_ROUTE_VM", true)
	if err != nil {
		return nil, err
	}

	arch, err := parseArch(env, "RUNNER_ARCH", "both")
	if err != nil {
		return nil, err
	}

	proxies, err := parseBool(env, "PROXIES_ENABLED", true)
	if err != nil {
		return nil, err
	}

	cache, err := parseBool(env, "CACHE_ENABLED", true)
	if err != nil {
		return nil, err
	}

	hostCache, _ := env.Lookup("HOST_CACHE_DIR")
	hostCache = strings.TrimSpace(hostCache)

	minRunners, err := parseInt(env, "MIN_RUNNERS", 0, 0, nil)
	if err != nil {
		return nil, err
	}

	maxRunners, err := parseInt(env, "MAX_RUNNERS", 4, 1, nil)
	if err != nil {
		return nil, err
	}

	if minRunners > maxRunners {
		return nil, &ConfigError{Message: fmt.Sprintf("MIN_RUNNERS=%d cannot exceed MAX_RUNNERS=%d", minRunners, maxRunners)}
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

	busyTimeout, err := parseInt(env, "RUNNER_BUSY_TIMEOUT_SECONDS", 7200, 60, nil)
	if err != nil {
		return nil, err
	}

	cleanup, err := parseBool(env, "CLEANUP_RUNNERS_ON_SHUTDOWN", false)
	if err != nil {
		return nil, err
	}

	nativeArch, _ := env.Lookup("NATIVE_ARCH_OVERRIDE")
	if strings.TrimSpace(nativeArch) == "" {
		nativeArch = "off"
	}
	nativeArch = strings.ToLower(strings.TrimSpace(nativeArch))

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
		AccessToken:                  token,
		Owner:                        strings.TrimSpace(owner),
		Org:                          strings.TrimSpace(org),
		ReposConfig:                  strings.TrimSpace(repos),
		AutoDiscover:                 autoDiscover,
		ActiveDays:                   activeDays,
		DiscoveryInterval:            discoveryInterval,
		RunnerBackend:                backend,
		AutoRouteVM:                  autoRouteVM,
		RunnerArch:                   arch,
		ProxiesEnabled:               proxies,
		CacheEnabled:                 cache,
		HostCacheDir:                 hostCache,
		MinRunners:                   minRunners,
		MaxRunners:                   maxRunners,
		PollInterval:                 pollInterval,
		RateLimitRefreshInterval:     rateLimitInterval,
		ActionsBillingRefreshInterval: billingInterval,
		BusyTimeoutSeconds:           busyTimeout,
		CleanupOnShutdown:            cleanup,
		NativeArchOverride:           nativeArch,
		DashboardEnabled:             dashEnabled,
		DashboardPort:                dashPort,
		DashboardHost:                strings.TrimSpace(dashHost),
		RepoPriority:                 strings.TrimSpace(repoPriority),
	}, nil
}
