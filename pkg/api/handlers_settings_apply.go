package api

import (
	"fmt"
	"strconv"

	"github.com/el-j/run-zero/pkg/config"
	"github.com/el-j/run-zero/pkg/state"
)

func validateAndApplySettings(cfg *config.Config, st *state.State, p *SettingsPayload) (map[string]string, error) {
	effectiveMax := cfg.MaxRunners
	if p.MaxRunners != nil {
		if *p.MaxRunners < 1 {
			return nil, fmt.Errorf("max_runners must be >= 1")
		}
		effectiveMax = *p.MaxRunners
	}
	if p.MinRunners != nil {
		if *p.MinRunners < 0 {
			return nil, fmt.Errorf("min_runners must be >= 0")
		}
		if *p.MinRunners > effectiveMax {
			return nil, fmt.Errorf("min_runners cannot exceed max_runners")
		}
	}
	if p.PollInterval != nil && (*p.PollInterval < 1 || *p.PollInterval > 3600) {
		return nil, fmt.Errorf("poll_interval must be between 1 and 3600")
	}

	u := make(map[string]string)
	if p.MaxRunners != nil {
		cfg.MaxRunners = *p.MaxRunners
		st.SetMaxRunners(*p.MaxRunners)
		u["MAX_RUNNERS"] = strconv.Itoa(*p.MaxRunners)
	}
	if p.MinRunners != nil {
		cfg.MinRunners = *p.MinRunners
		u["MIN_RUNNERS"] = strconv.Itoa(*p.MinRunners)
	}
	if p.RunnerCPUs != nil && *p.RunnerCPUs >= 1 {
		cfg.RunnerCPUs = *p.RunnerCPUs
		u["RUNNER_CPUS"] = strconv.Itoa(*p.RunnerCPUs)
	}
	if p.RunnerMemory != nil && *p.RunnerMemory != "" {
		cfg.RunnerMemory = *p.RunnerMemory
		u["RUNNER_MEMORY"] = *p.RunnerMemory
	}
	if p.PollInterval != nil {
		cfg.PollInterval = *p.PollInterval
		u["POLL_INTERVAL"] = strconv.Itoa(*p.PollInterval)
	}
	if p.AutoDiscover != nil {
		cfg.AutoDiscover = *p.AutoDiscover
		u["AUTO_DISCOVER_REPOS"] = strconv.FormatBool(*p.AutoDiscover)
	}
	if p.AutoRouteVM != nil {
		cfg.AutoRouteVM = *p.AutoRouteVM
		u["AUTO_ROUTE_VM"] = strconv.FormatBool(*p.AutoRouteVM)
	}
	if p.ProxiesEnabled != nil {
		cfg.ProxiesEnabled = *p.ProxiesEnabled
		u["PROXIES_ENABLED"] = strconv.FormatBool(*p.ProxiesEnabled)
	}
	if p.CacheEnabled != nil {
		cfg.CacheEnabled = *p.CacheEnabled
		u["CACHE_ENABLED"] = strconv.FormatBool(*p.CacheEnabled)
	}
	if p.RunnerBackend != nil {
		cfg.RunnerBackend = *p.RunnerBackend
		u["RUNNER_BACKEND"] = *p.RunnerBackend
	}
	if p.RunnerArch != nil {
		cfg.RunnerArch = *p.RunnerArch
		u["RUNNER_ARCH"] = *p.RunnerArch
	}
	if p.NativeArchOverride != nil {
		cfg.NativeArchOverride = *p.NativeArchOverride
		u["NATIVE_ARCH_OVERRIDE"] = *p.NativeArchOverride
	}
	if p.HostCacheDir != nil {
		cfg.HostCacheDir = *p.HostCacheDir
		u["HOST_CACHE_DIR"] = *p.HostCacheDir
	}
	if p.AccessToken != nil && *p.AccessToken != "" {
		cfg.AccessToken = *p.AccessToken
		u["ACCESS_TOKEN"] = *p.AccessToken
	}
	return u, nil
}
