package doctor

// Status represents the verdict of a diagnostic check.
type Status string

const (
	StatusOK   Status = "ok"
	StatusWarn Status = "warn"
	StatusFail Status = "fail"
	StatusSkip Status = "skip"
)

// CheckResult contains status and human-readable details of a single check.
type CheckResult struct {
	Name   string
	Status Status
	Detail string
}
