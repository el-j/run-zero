package daemon

import (
	"context"
	"encoding/base64"
	"net/http"
	"testing"

	"github.com/el-j/run-zero/pkg/state"
)

const servicesWorkflow = `name: CI
jobs:
  integration:
    runs-on: self-hosted
    services:
      redis:
        image: redis:7
  lint:
    runs-on: self-hosted
`

func workflowRoute(text string) map[string]string {
	return map[string]string{
		"/repos/o/a/contents/.github/workflows/ci.yml": `{"encoding":"base64","content":"` + base64.StdEncoding.EncodeToString([]byte(text)) + `"}`,
	}
}

func servicesJob(name string) state.QueuedJob {
	return state.QueuedJob{ID: 1, RunID: 2, Name: name, WorkflowPath: ".github/workflows/ci.yml", HeadSHA: "abc"}
}

func TestResolveJobBackend_RoutesServicesJobsToVM(t *testing.T) {
	f, gh := newFakeGH(t, workflowRoute(servicesWorkflow))
	cfg := baseCfg("o/a")
	cfg.AutoRouteVM = true
	s, st := newTestScaler(t, cfg, gh, nil, nil, "o/a")
	ctx := context.Background()

	if got := s.resolveJobBackend(ctx, "o/a", servicesJob("integration")); got != "orbstack" {
		t.Fatalf("services job: got %s", got)
	}
	if !hasLog(st, "its workflow gives it services") {
		t.Fatal("expected a routing log")
	}
	if got := s.resolveJobBackend(ctx, "o/a", servicesJob("lint")); got != "docker" {
		t.Fatalf("plain job: got %s", got)
	}
	// Both jobs share one workflow version: fetched once, results cached.
	s.resolveJobBackend(ctx, "o/a", servicesJob("integration"))
	if n := f.hit("GET /repos/o/a/contents/"); n != 1 {
		t.Fatalf("expected one workflow fetch, got %d", n)
	}
}

func TestResolveJobBackend_SkipsWorkflowLookupWhenNotNeeded(t *testing.T) {
	f, gh := newFakeGH(t, workflowRoute(servicesWorkflow))
	ctx := context.Background()
	cases := map[string]func(s *Scaler) state.QueuedJob{
		"routing off":          func(s *Scaler) state.QueuedJob { s.cfg.AutoRouteVM = false; return servicesJob("integration") },
		"fixed backend":        func(s *Scaler) state.QueuedJob { s.cfg.RunnerBackend = "docker"; return servicesJob("integration") },
		"standby (no job)":     func(*Scaler) state.QueuedJob { return state.QueuedJob{} },
		"no workflow metadata": func(*Scaler) state.QueuedJob { return state.QueuedJob{ID: 1, Name: "integration"} },
		"label already routes": func(*Scaler) state.QueuedJob {
			j := servicesJob("integration")
			j.Labels = []string{"vm"}
			return j
		},
	}
	for name, setup := range cases {
		cfg := baseCfg("o/a")
		cfg.AutoRouteVM, cfg.VMTriggerLabels = true, []string{"vm"}
		s, _ := newTestScaler(t, cfg, gh, nil, nil, "o/a")
		s.resolveJobBackend(ctx, "o/a", setup(s))
		if n := f.hit("GET /repos/o/a/contents/"); n != 0 {
			t.Fatalf("%s: workflow must not be fetched, got %d fetches", name, n)
		}
	}
}

func TestJobVMReason_ErrorsAndCacheBound(t *testing.T) {
	f, gh := newFakeGH(t, workflowRoute(servicesWorkflow))
	s, _ := newTestScaler(t, baseCfg("o/a"), gh, nil, nil, "o/a")
	ctx := context.Background()

	// A failed fetch counts as "no services" and is not cached.
	f.codes["/repos/o/a/contents/.github/workflows/ci.yml"] = http.StatusInternalServerError
	if s.jobVMReason(ctx, "o/a", servicesJob("integration")) != "" {
		t.Fatal("fetch error must count as no services")
	}
	delete(f.codes, "/repos/o/a/contents/.github/workflows/ci.yml")
	if s.jobVMReason(ctx, "o/a", servicesJob("integration")) != "services" {
		t.Fatal("expected services after a successful retry")
	}

	// A full cache is cleared before the next workflow is stored.
	s.cachedWorkflows = maxCachedWorkflows
	j := servicesJob("integration")
	j.HeadSHA = "def"
	s.jobVMReason(ctx, "o/a", j)
	if s.cachedWorkflows != 1 {
		t.Fatalf("expected the cache to restart at 1 entry, got %d", s.cachedWorkflows)
	}

	s.ghClient = nil
	if s.jobVMReason(ctx, "o/a", servicesJob("integration")) != "" {
		t.Fatal("no client means no lookup")
	}
}

func TestResolveJobBackend_RoutesComposeJobsToVM(t *testing.T) {
	_, gh := newFakeGH(t, workflowRoute("jobs:\n  stack:\n    steps:\n      - run: docker compose up -d\n"))
	cfg := baseCfg("o/a")
	cfg.AutoRouteVM = true
	s, st := newTestScaler(t, cfg, gh, nil, nil, "o/a")
	if got := s.resolveJobBackend(context.Background(), "o/a", servicesJob("stack")); got != "orbstack" {
		t.Fatalf("compose job: got %s", got)
	}
	if !hasLog(st, "it starts a docker compose stack") {
		t.Fatal("expected the routing log to give the reason")
	}
}

func TestPolicy_HostArch(t *testing.T) {
	s, _ := newTestScaler(t, baseCfg("o/a"), nil, nil, nil, "o/a")
	s.archOverride.HostArch = "arm64"
	if got := s.resolveJobArch(state.QueuedJob{Labels: []string{"self-hosted"}}, "o/a"); got != "arm64" {
		t.Fatalf("an unlabelled job runs on the host arch, got %s", got)
	}
	s.archOverride = nil
	if got := s.resolveJobArch(state.QueuedJob{}, "o/a"); got != "amd64" {
		t.Fatalf("an unknown host arch falls back to amd64, got %s", got)
	}
}
