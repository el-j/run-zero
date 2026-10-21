package docker_test

import (
	"os"
	"regexp"
	"testing"
)

// Runner containers share the host Docker daemon with every other concurrent
// job (and anything else on the host, e.g. a local k3s cluster). A runner that
// stops "every container created since I started" therefore kills other jobs'
// buildx builders and service containers mid-run (observed: landing staging
// builds failing with buildkit "graceful_stop" EOFs, a local Zitadel pod
// restarted 74 times). start.sh must never stop or remove containers it does
// not own; each job's own actions clean up what they create.
func TestStartScript_DoesNotStopSharedDaemonContainers(t *testing.T) {
	script, err := os.ReadFile("start.sh")
	if err != nil {
		t.Fatalf("read start.sh: %v", err)
	}
	for _, pattern := range []string{`docker\s+stop\b`, `docker\s+rm\b`, `docker\s+kill\b`, `docker\s+(container\s+)?prune\b`} {
		if loc := regexp.MustCompile(pattern).FindIndex(script); loc != nil {
			t.Errorf("start.sh matches %q at byte %d: runners must not stop containers on the shared daemon", pattern, loc[0])
		}
	}
}
