package config

// Config holds the validated configuration for the RunZero daemon engine.
type Config struct {
	AccessToken                   string
	Owner                         string
	Org                           string
	ReposConfig                   string
	AutoDiscover                  bool
	ActiveDays                    int
	DiscoveryInterval             int
	RunnerBackend                 string
	AutoRouteVM                   bool
	VMTriggerLabels               []string
	RunnerArch                    string
	ProxiesEnabled                bool
	CacheEnabled                  bool
	HostCacheDir                  string
	MinRunners                    int
	MaxRunners                    int
	PollInterval                  int
	RateLimitRefreshInterval      int
	ActionsBillingRefreshInterval int
	BusyTimeoutSeconds            int
	CleanupOnShutdown             bool
	NativeArchOverride            string
	DashboardEnabled              bool
	DashboardPort                 int
	DashboardHost                 string
	RepoPriority                  string
	RunnerCPUs                    int
	RunnerMemory                  string
	GitLabURL                     string
	GitLabToken                   string
	GitLabGroup                   string
	GitLabProjects                string
	ProvidersConfigFile           string
	// RunnerSizing is "auto" (limit each runner's CPUs/memory) or "unlimited"
	// (no limits; every runner may claim every host core).
	RunnerSizing string
	// VMBackend is the VM engine for VM-routed jobs: auto (OrbStack, or the
	// engine RUNNER_BACKEND names), orbstack, wsl2 or multipass.
	VMBackend      string
	MultipassImage string
	WSLDistroBase  string
	WSLBaseTarball string
	WSLRunnerDir   string
}
