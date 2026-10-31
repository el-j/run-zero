package doctor

// Status represents the verdict of a diagnostic check.
type Status string

const (
	// StatusOK means the check passed.
	StatusOK Status = "ok"
	// StatusWarn means the check passed with a caveat.
	StatusWarn Status = "warn"
	// StatusFail means the check failed.
	StatusFail Status = "fail"
	// StatusSkip means the check was not applicable.
	StatusSkip Status = "skip"
)

// CheckResult contains status and human-readable details of a single check.
type CheckResult struct {
	Name   string
	Status Status
	Detail string
}
