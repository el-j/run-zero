package settings

import (
	"fmt"
	"strconv"
	"sync"

	"github.com/el-j/run-zero/pkg/config"
)

// SettingsUpdate holds fields that can be updated dynamically at runtime.
type SettingsUpdate struct {
	AccessToken       *string
	Owner             *string
	Org               *string
	AutoDiscover      *bool
	ActiveDays        *int
	RunnerBackend     *string
	AutoRouteVM       *bool
	RunnerArch        *string
	MinRunners        *int
	MaxRunners        *int
	PollInterval      *int
	DiscoveryInterval *int
	ProxiesEnabled    *bool
	CacheEnabled      *bool
	HostCacheDir      *string
}

// Manager coordinates live in-memory settings mutation and disk persistence.
type Manager struct {
	mu          sync.RWMutex
	cfg         *config.Config
	envPath     string
	subscribers []func(*config.Config)
}

// NewManager creates a dynamic settings manager.
func NewManager(cfg *config.Config, envPath string) *Manager {
	return &Manager{
		cfg:         cfg,
		envPath:     envPath,
		subscribers: make([]func(*config.Config), 0),
	}
}

// Get returns the current live config.
func (m *Manager) Get() *config.Config {
	m.mu.RLock()
	defer m.mu.RUnlock()
	return m.cfg
}

// Subscribe registers a listener invoked when configuration changes.
func (m *Manager) Subscribe(fn func(*config.Config)) {
	m.mu.Lock()
	defer m.mu.Unlock()
	m.subscribers = append(m.subscribers, fn)
}

// Apply validates and mutates the live config, notifies listeners, and updates .env.
func (m *Manager) Apply(update SettingsUpdate) (*config.Config, error) {
	m.mu.Lock()
	defer m.mu.Unlock()

	cfg := m.cfg
	dotEnvUpdates := make(map[string]string)

	if update.MaxRunners != nil {
		if *update.MaxRunners < 1 {
			return nil, fmt.Errorf("max_runners must be >= 1")
		}
		cfg.MaxRunners = *update.MaxRunners
		dotEnvUpdates["MAX_RUNNERS"] = strconv.Itoa(*update.MaxRunners)
	}

	if update.MinRunners != nil {
		if *update.MinRunners < 0 {
			return nil, fmt.Errorf("min_runners must be >= 0")
		}
		if *update.MinRunners > cfg.MaxRunners {
			return nil, fmt.Errorf("min_runners cannot exceed max_runners")
		}
		cfg.MinRunners = *update.MinRunners
		dotEnvUpdates["MIN_RUNNERS"] = strconv.Itoa(*update.MinRunners)
	}

	if update.PollInterval != nil {
		if *update.PollInterval < 1 || *update.PollInterval > 3600 {
			return nil, fmt.Errorf("poll_interval must be between 1 and 3600")
		}
		cfg.PollInterval = *update.PollInterval
		dotEnvUpdates["POLL_INTERVAL"] = strconv.Itoa(*update.PollInterval)
	}

	if update.AutoDiscover != nil {
		cfg.AutoDiscover = *update.AutoDiscover
		dotEnvUpdates["AUTO_DISCOVER_REPOS"] = strconv.FormatBool(*update.AutoDiscover)
	}
	if update.AutoRouteVM != nil {
		cfg.AutoRouteVM = *update.AutoRouteVM
		dotEnvUpdates["AUTO_ROUTE_VM"] = strconv.FormatBool(*update.AutoRouteVM)
	}
	if update.ProxiesEnabled != nil {
		cfg.ProxiesEnabled = *update.ProxiesEnabled
		dotEnvUpdates["PROXIES_ENABLED"] = strconv.FormatBool(*update.ProxiesEnabled)
	}
	if update.CacheEnabled != nil {
		cfg.CacheEnabled = *update.CacheEnabled
		dotEnvUpdates["CACHE_ENABLED"] = strconv.FormatBool(*update.CacheEnabled)
	}

	if m.envPath != "" && len(dotEnvUpdates) > 0 {
		_ = UpdateDotEnv(m.envPath, dotEnvUpdates)
	}

	for _, sub := range m.subscribers {
		sub(cfg)
	}

	return cfg, nil
}
