package reaper

// Action represents the reconciliation verdict for a runner instance.
type Action string

const (
	// ActionKeep leaves the runner untouched.
	ActionKeep Action = "keep"
	// ActionReapUnregistered removes a runner that never registered.
	ActionReapUnregistered Action = "reap-unregistered"
	// ActionReapIdle removes an idle runner that is no longer needed.
	ActionReapIdle Action = "reap-idle"
	// ActionCheckStaleBusy flags a busy runner that may be stuck.
	ActionCheckStaleBusy Action = "check-stale-busy"
)

// Timeouts defines thresholds in seconds for runner expiration and reaping.
type Timeouts struct {
	IdleSeconds         int
	UnregisteredSeconds int
	BusySeconds         int
}

// DefaultTimeouts provides standard production reaper timeouts.
func DefaultTimeouts() Timeouts {
	return Timeouts{
		IdleSeconds:         600,
		UnregisteredSeconds: 180,
		BusySeconds:         7200,
	}
}

// Registration describes a runner registered with GitHub Actions API.
type Registration struct {
	ID     int64  `json:"id"`
	Name   string `json:"name"`
	Status string `json:"status"`
	Busy   bool   `json:"busy"`
	Scope  string `json:"scope,omitempty"`
}

// RepoScope formats repository runner API scope ("repos/owner/name").
func RepoScope(repo string) string {
	return "repos/" + repo
}

// OrgScope formats organization runner API scope ("orgs/org").
func OrgScope(org string) string {
	return "orgs/" + org
}
