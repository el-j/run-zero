package parity

// Decision represents the engine's scheduling decision for a job.
type Decision struct {
	Backend      string   `json:"backend"`
	Arch         string   `json:"arch"`
	RequiresVM   bool     `json:"requires_vm"`
	TriggerMatch string   `json:"trigger_match"`
	Labels       []string `json:"labels"`
	CPUs         string   `json:"cpus"`
	MemoryMB     int      `json:"memory_mb"`
}

// TestCase represents an end-to-end parity test scenario.
type TestCase struct {
	Name             string
	Repo             string
	WorkflowYAML     string
	JobName          string
	JobLabels        []string
	HostArch         string
	ArchOverride     string
	CapacityCPUs     int
	CapacityMemoryMB int
	MaxRunners       int
	Expected         Decision
}

// Result records the evaluation result of a parity scenario.
type Result struct {
	Name    string
	Passed  bool
	DiffMsg string
}
