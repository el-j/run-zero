package doctor

import (
	"context"
	"fmt"
	"strings"

	"github.com/el-j/run-zero/pkg/driver"
	"github.com/el-j/run-zero/pkg/github"
)

// Options holds parameters needed to run diagnostic checks.
type Options struct {
	Exec         driver.CmdExecutor
	GHClient     *github.Client
	CacheDir     string
	CacheEnabled bool
	ProxyURL     string
}

// RunAll executes the complete suite of diagnostic checks.
func RunAll(ctx context.Context, opts Options) []CheckResult {
	results := make([]CheckResult, 0, 8)
	results = append(results, CheckDocker(ctx, opts.Exec))
	results = append(results, CheckOrbStack(ctx, opts.Exec))
	if opts.GHClient != nil {
		results = append(results, CheckGitHub(ctx, opts.GHClient))
	}
	results = append(results, CheckHostCache(opts.CacheDir, opts.CacheEnabled)...)
	if opts.ProxyURL != "" {
		results = append(results, CheckProxy("squid", opts.ProxyURL, nil))
	}
	return results
}

// Symbol returns the visual indicator for a status.
func Symbol(s Status) string {
	switch s {
	case StatusOK:
		return "✅"
	case StatusWarn:
		return "⚠️"
	case StatusFail:
		return "❌"
	case StatusSkip:
		return "⏭️"
	default:
		return "❓"
	}
}

// FormatReport creates a formatted terminal output of check results.
func FormatReport(results []CheckResult) string {
	var sb strings.Builder
	sb.WriteString("=== runzero Doctor Diagnostics ===\n")
	okCount, warnCount, failCount := 0, 0, 0

	for _, r := range results {
		sb.WriteString(fmt.Sprintf("%s [%s] %s: %s\n",
			Symbol(r.Status), strings.ToUpper(string(r.Status)), r.Name, r.Detail))
		switch r.Status {
		case StatusOK:
			okCount++
		case StatusWarn:
			warnCount++
		case StatusFail:
			failCount++
		}
	}

	sb.WriteString("----------------------------------\n")
	sb.WriteString(fmt.Sprintf("Summary: %d passed, %d warnings, %d failures\n",
		okCount, warnCount, failCount))
	return sb.String()
}

// HasFailures returns true if any check failed.
func HasFailures(results []CheckResult) bool {
	for _, r := range results {
		if r.Status == StatusFail {
			return true
		}
	}
	return false
}
