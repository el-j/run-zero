package main

import (
	"fmt"
	"io"

	"github.com/el-j/run-zero/pkg/parity"
)

// runParity checks the autoscaler's scheduling decisions (backend, arch and
// sizing) against the canonical baseline scenarios and exits 1 on any drift.
func runParity(stdout io.Writer) int {
	return reportParity(stdout, parity.RunAllParity(parity.BaselineScenarios()))
}

func reportParity(stdout io.Writer, results []parity.Result) int {
	failed := 0
	for _, r := range results {
		if r.Passed {
			_, _ = fmt.Fprintf(stdout, "PASS  %s\n", r.Name)
			continue
		}
		failed++
		_, _ = fmt.Fprintf(stdout, "FAIL  %s: %s\n", r.Name, r.DiffMsg)
	}
	_, _ = fmt.Fprintf(stdout, "%d/%d scheduling scenarios match\n", len(results)-failed, len(results))
	if failed > 0 {
		return 1
	}
	return 0
}
