package daemon

import (
	"fmt"
	"os"
	"path/filepath"
	"testing"
)

// TestMain shadows the runner CLIs with stubs that always fail. NewDaemon wires
// the real Docker/OrbStack drivers, and tests run on the same host as the live
// fleet (e.g. from the pre-commit hook): a test reaching CleanupAll through the
// real drivers once deleted every running runner VM and container mid-job.
func TestMain(m *testing.M) {
	dir, err := os.MkdirTemp("", "runzero-daemon-test-")
	if err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(1)
	}
	stub := []byte("#!/bin/sh\necho \"$0 is stubbed in daemon tests\" >&2\nexit 1\n")
	for _, name := range []string{"docker", "orbctl", "orb"} {
		if err := os.WriteFile(filepath.Join(dir, name), stub, 0o755); err != nil {
			fmt.Fprintln(os.Stderr, err)
			os.Exit(1)
		}
	}
	_ = os.Setenv("PATH", dir+string(os.PathListSeparator)+os.Getenv("PATH"))
	_ = os.Setenv("RUNZERO_STATE_DIR", filepath.Join(dir, "state"))

	code := m.Run()
	_ = os.RemoveAll(dir)
	os.Exit(code)
}
