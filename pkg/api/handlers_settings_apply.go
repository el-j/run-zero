package api

import (
	"fmt"
	"strconv"

	"github.com/el-j/run-zero/pkg/config"
	"github.com/el-j/run-zero/pkg/state"
)

func validateAndApplySettings(cfg *config.Config, st *state.State, p *SettingsPayload) (map[string]string, error) {
	if err := validateSettings(cfg.MaxRunners, p); err != nil {
		return nil, err
	}

	u := make(map[string]string)
	if p.MaxRunners != nil {
		st.SetMaxRunners(*p.MaxRunners)
	}
	applyInt(u, "MAX_RUNNERS", &cfg.MaxRunners, p.MaxRunners)
	applyInt(u, "MIN_RUNNERS", &cfg.MinRunners, p.MinRunners)
	if p.RunnerCPUs != nil && *p.RunnerCPUs >= 1 {
		applyInt(u, "RUNNER_CPUS", &cfg.RunnerCPUs, p.RunnerCPUs)
	}
	applyString(u, "RUNNER_MEMORY", &cfg.RunnerMemory, nonEmpty(p.RunnerMemory))
	applyInt(u, "POLL_INTERVAL", &cfg.PollInterval, p.PollInterval)
	applyBool(u, "AUTO_DISCOVER_REPOS", &cfg.AutoDiscover, p.AutoDiscover)
	applyBool(u, "AUTO_ROUTE_VM", &cfg.AutoRouteVM, p.AutoRouteVM)
	applyBool(u, "PROXIES_ENABLED", &cfg.ProxiesEnabled, p.ProxiesEnabled)
	applyBool(u, "CACHE_ENABLED", &cfg.CacheEnabled, p.CacheEnabled)
	applyString(u, "RUNNER_BACKEND", &cfg.RunnerBackend, p.RunnerBackend)
	applyString(u, "RUNNER_ARCH", &cfg.RunnerArch, p.RunnerArch)
	applyString(u, "NATIVE_ARCH_OVERRIDE", &cfg.NativeArchOverride, p.NativeArchOverride)
	applyString(u, "HOST_CACHE_DIR", &cfg.HostCacheDir, p.HostCacheDir)
	applyString(u, "ACCESS_TOKEN", &cfg.AccessToken, nonEmpty(p.AccessToken))
	return u, nil
}

// validateSettings checks the payload's runner bounds against the current
// maxRunners (or the new one, when the payload changes it).
func validateSettings(maxRunners int, p *SettingsPayload) error {
	if p.MaxRunners != nil {
		if *p.MaxRunners < 1 {
			return fmt.Errorf("max_runners must be >= 1")
		}
		maxRunners = *p.MaxRunners
	}
	if p.MinRunners != nil {
		if *p.MinRunners < 0 {
			return fmt.Errorf("min_runners must be >= 0")
		}
		if *p.MinRunners > maxRunners {
			return fmt.Errorf("min_runners cannot exceed max_runners")
		}
	}
	if p.PollInterval != nil && (*p.PollInterval < 1 || *p.PollInterval > 3600) {
		return fmt.Errorf("poll_interval must be between 1 and 3600")
	}
	return nil
}

// applyInt, applyBool and applyString set *dst and record the .env update when
// the payload carries a value (v != nil).
func applyInt(u map[string]string, key string, dst, v *int) {
	if v != nil {
		*dst = *v
		u[key] = strconv.Itoa(*v)
	}
}

func applyBool(u map[string]string, key string, dst, v *bool) {
	if v != nil {
		*dst = *v
		u[key] = strconv.FormatBool(*v)
	}
}

func applyString(u map[string]string, key string, dst, v *string) {
	if v != nil {
		*dst = *v
		u[key] = *v
	}
}

// nonEmpty treats an empty string as "not provided".
func nonEmpty(v *string) *string {
	if v == nil || *v == "" {
		return nil
	}
	return v
}
