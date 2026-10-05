package api

import (
	"encoding/json"
	"net/http"

	"github.com/el-j/run-zero/pkg/config"
	"github.com/el-j/run-zero/pkg/state"
)

type SettingsPayload struct {
	AccessTokenConfigured *bool   `json:"access_token_configured,omitempty"`
	AccessToken           *string `json:"access_token,omitempty"`
	Owner                 *string `json:"owner,omitempty"`
	Org                   *string `json:"org,omitempty"`
	AutoDiscover          *bool   `json:"auto_discover,omitempty"`
	ActiveDays            *int    `json:"active_days,omitempty"`
	RunnerBackend         *string `json:"runner_backend,omitempty"`
	AutoRouteVM           *bool   `json:"auto_route_vm,omitempty"`
	RunnerArch            *string `json:"runner_arch,omitempty"`
	MinRunners            *int    `json:"min_runners,omitempty"`
	MaxRunners            *int    `json:"max_runners,omitempty"`
	PollInterval          *int    `json:"poll_interval,omitempty"`
	DiscoveryInterval     *int    `json:"discovery_interval,omitempty"`
	ProxiesEnabled        *bool   `json:"proxies_enabled,omitempty"`
	CacheEnabled          *bool   `json:"cache_enabled,omitempty"`
	HostCacheDir          *string `json:"host_cache_dir,omitempty"`
	NativeArchOverride    *string `json:"native_arch_override,omitempty"`
}

func handleSettings(cfg *config.Config, st *state.State) http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		switch r.Method {
		case http.MethodGet:
			tokenConfigured := cfg.AccessToken != ""
			settings := map[string]interface{}{
				"access_token_configured": tokenConfigured,
				"owner":                   cfg.Owner,
				"org":                     cfg.Org,
				"auto_discover":           cfg.AutoDiscover,
				"active_days":             cfg.ActiveDays,
				"runner_backend":          cfg.RunnerBackend,
				"auto_route_vm":           cfg.AutoRouteVM,
				"runner_arch":             cfg.RunnerArch,
				"min_runners":             cfg.MinRunners,
				"max_runners":             cfg.MaxRunners,
				"poll_interval":           cfg.PollInterval,
				"discovery_interval":      cfg.DiscoveryInterval,
				"proxies_enabled":         cfg.ProxiesEnabled,
				"cache_enabled":           cfg.CacheEnabled,
				"host_cache_dir":          cfg.HostCacheDir,
				"native_arch_override":    cfg.NativeArchOverride,
			}
			writeJSON(w, http.StatusOK, settings)

		case http.MethodPost:
			var payload SettingsPayload
			if err := json.NewDecoder(r.Body).Decode(&payload); err != nil {
				writeError(w, http.StatusBadRequest, "Invalid JSON payload")
				return
			}

			if payload.MaxRunners != nil {
				if *payload.MaxRunners < 1 {
					writeError(w, http.StatusBadRequest, "max_runners must be >= 1")
					return
				}
				cfg.MaxRunners = *payload.MaxRunners
				st.SetMaxRunners(*payload.MaxRunners)
			}
			if payload.MinRunners != nil {
				if *payload.MinRunners < 0 {
					writeError(w, http.StatusBadRequest, "min_runners must be >= 0")
					return
				}
				if *payload.MinRunners > cfg.MaxRunners {
					writeError(w, http.StatusBadRequest, "min_runners cannot exceed max_runners")
					return
				}
				cfg.MinRunners = *payload.MinRunners
			}
			if payload.PollInterval != nil {
				if *payload.PollInterval < 1 || *payload.PollInterval > 3600 {
					writeError(w, http.StatusBadRequest, "poll_interval must be between 1 and 3600")
					return
				}
				cfg.PollInterval = *payload.PollInterval
			}
			if payload.AutoDiscover != nil {
				cfg.AutoDiscover = *payload.AutoDiscover
			}
			if payload.AutoRouteVM != nil {
				cfg.AutoRouteVM = *payload.AutoRouteVM
			}
			if payload.ProxiesEnabled != nil {
				cfg.ProxiesEnabled = *payload.ProxiesEnabled
			}
			if payload.CacheEnabled != nil {
				cfg.CacheEnabled = *payload.CacheEnabled
			}

			st.AppendLog("[Go Engine] ⚙️ Updated runtime system settings.")
			writeJSON(w, http.StatusOK, map[string]interface{}{
				"ok":      true,
				"message": "Settings updated successfully",
			})

		default:
			writeError(w, http.StatusMethodNotAllowed, "Method not allowed")
		}
	}
}
