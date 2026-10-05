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
}
