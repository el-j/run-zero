package config

import (
	"fmt"
	"strings"
)

type runnerOptions struct {
	backend            string
	autoRouteVM        bool
	arch               string
	proxies            bool
	cache              bool
	hostCache          string
	minRunners         int
	maxRunners         int
	nativeArchOverride string
	cleanup            bool
	busyTimeout        int
	runnerCPUs         int
	runnerMemory       string
}

func loadRunnerOptions(env EnvLookup) (*runnerOptions, error) {
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
	runnerCPUs, _ := parseInt(env, "RUNNER_CPUS", 0, 0, nil)
	runnerMemory, _ := env.Lookup("RUNNER_MEMORY")

	return &runnerOptions{
		backend:            backend,
		autoRouteVM:        autoRouteVM,
		arch:               arch,
		proxies:            proxies,
		cache:              cache,
		hostCache:          strings.TrimSpace(hostCache),
		minRunners:         minRunners,
		maxRunners:         maxRunners,
		busyTimeout:        busyTimeout,
		cleanup:            cleanup,
		nativeArchOverride: strings.ToLower(strings.TrimSpace(nativeArch)),
		runnerCPUs:         runnerCPUs,
		runnerMemory:       strings.TrimSpace(runnerMemory),
	}, nil
}
