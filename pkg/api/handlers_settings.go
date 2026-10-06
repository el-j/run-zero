package api

import (
	"encoding/json"
	"net/http"

	"github.com/el-j/run-zero/pkg/config"
	"github.com/el-j/run-zero/pkg/settings"
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
	RunnerCPUs            *int    `json:"runner_cpus,omitempty"`
	RunnerMemory          *string `json:"runner_memory,omitempty"`
	RepoPriority          *string `json:"repo_priority,omitempty"`
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
			writeJSON(w, http.StatusOK, map[string]interface{}{
				"access_token_configured": cfg.AccessToken != "",
				"owner":                   cfg.Owner,
				"org":                     cfg.Org,
				"auto_discover":           cfg.AutoDiscover,
				"active_days":             cfg.ActiveDays,
				"runner_backend":          cfg.RunnerBackend,
				"auto_route_vm":           cfg.AutoRouteVM,
				"runner_arch":             cfg.RunnerArch,
				"min_runners":             cfg.MinRunners,
				"max_runners":             cfg.MaxRunners,
				"runner_cpus":             cfg.RunnerCPUs,
				"runner_memory":           cfg.RunnerMemory,
				"repo_priority":           cfg.RepoPriority,
				"poll_interval":           cfg.PollInterval,
				"discovery_interval":      cfg.DiscoveryInterval,
				"proxies_enabled":         cfg.ProxiesEnabled,
				"cache_enabled":           cfg.CacheEnabled,
				"host_cache_dir":          cfg.HostCacheDir,
				"native_arch_override":    cfg.NativeArchOverride,
			})
		case http.MethodPost:
			var p SettingsPayload
			if err := json.NewDecoder(r.Body).Decode(&p); err != nil {
				writeError(w, http.StatusBadRequest, "Invalid JSON payload")
				return
			}
			envUp, err := validateAndApplySettings(cfg, st, &p)
			if err != nil {
				writeError(w, http.StatusBadRequest, err.Error())
				return
			}
			_ = settings.UpdateDotEnv(".env", envUp)
			st.AppendLog("[Go Engine] ⚙️ Updated runtime system settings (.env updated).")
			writeJSON(w, http.StatusOK, map[string]interface{}{"ok": true, "message": "Settings updated successfully"})
		default:
			writeError(w, http.StatusMethodNotAllowed, "Method not allowed")
		}
	}
}
