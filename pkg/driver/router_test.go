package driver

import (
	"context"
	"fmt"
	"testing"

	"github.com/el-j/run-zero/pkg/state"
)

type dummyDriver struct {
	backend    string
	spawnFunc  func(spec RunnerSpec) (*state.RunnerInfo, error)
	listFunc   func() ([]state.RunnerInfo, error)
	stopFunc   func(id string) error
	cleanFunc  func() error
}

func (d *dummyDriver) Backend() string { return d.backend }
func (d *dummyDriver) SpawnRunner(ctx context.Context, spec RunnerSpec) (*state.RunnerInfo, error) {
	if d.spawnFunc != nil {
		return d.spawnFunc(spec)
	}
	return &state.RunnerInfo{ID: spec.ID, Backend: d.backend}, nil
}
func (d *dummyDriver) ListRunners(ctx context.Context) ([]state.RunnerInfo, error) {
	if d.listFunc != nil {
		return d.listFunc()
	}
	return []state.RunnerInfo{{ID: "r-" + d.backend, Backend: d.backend}}, nil
}
func (d *dummyDriver) StopRunner(ctx context.Context, id string) error {
	if d.stopFunc != nil {
		return d.stopFunc(id)
	}
	return nil
}
func (d *dummyDriver) CleanupAll(ctx context.Context) error {
	if d.cleanFunc != nil {
		return d.cleanFunc()
	}
	return nil
}

func TestNewRouter_Defaults(t *testing.T) {
	r := NewRouter(nil, nil, "", false, nil)
	if r.Backend() != "auto" {
		t.Errorf("expected auto default mode, got %s", r.Backend())
	}
}

func TestRouter_SelectDriver(t *testing.T) {
	docker := &dummyDriver{backend: "docker"}
	orb := &dummyDriver{backend: "orbstack"}
	store := NewInstanceStore("")

	router := NewRouter(docker, orb, "auto", true, store)
	if router.Backend() != "auto" {
		t.Errorf("expected auto backend, got %s", router.Backend())
	}

	// 1. Explicit backend in spec
	d1 := router.SelectDriver(RunnerSpec{Backend: "orbstack"})
	if d1.Backend() != "orbstack" {
		t.Errorf("expected orbstack, got %s", d1.Backend())
	}
	d2 := router.SelectDriver(RunnerSpec{Backend: "docker"})
	if d2.Backend() != "docker" {
		t.Errorf("expected docker, got %s", d2.Backend())
	}

	// 2. Auto-route by label
	d3 := router.SelectDriver(RunnerSpec{Labels: []string{"self-hosted", "vm"}})
	if d3.Backend() != "orbstack" {
		t.Errorf("expected orbstack by label vm, got %s", d3.Backend())
	}

	// 3. Default fallback
	d4 := router.SelectDriver(RunnerSpec{Labels: []string{"ubuntu-latest"}})
	if d4.Backend() != "docker" {
		t.Errorf("expected docker fallback, got %s", d4.Backend())
	}

	// 4. Default mode orbstack
	routerVM := NewRouter(docker, orb, "orbstack", false, store)
	d5 := routerVM.SelectDriver(RunnerSpec{})
	if d5.Backend() != "orbstack" {
		t.Errorf("expected orbstack default mode, got %s", d5.Backend())
	}
}

func TestRouter_Lifecycle(t *testing.T) {
	docker := &dummyDriver{backend: "docker"}
	orb := &dummyDriver{backend: "orbstack"}
	store := NewInstanceStore("")
	store.Register(state.RunnerInfo{ID: "r-orb", Backend: "orbstack"})
	store.Register(state.RunnerInfo{ID: "r-dock", Backend: "docker"})

	router := NewRouter(docker, orb, "auto", true, store)

	info, err := router.SpawnRunner(context.Background(), RunnerSpec{ID: "new-runner"})
	if err != nil || info.ID != "new-runner" {
		t.Fatalf("unexpected spawn: %v, %+v", err, info)
	}

	runners, err := router.ListRunners(context.Background())
	if err != nil || len(runners) != 2 {
		t.Fatalf("expected 2 merged runners, got %d (err: %v)", len(runners), err)
	}

	if err := router.StopRunner(context.Background(), "r-orb"); err != nil {
		t.Fatalf("unexpected stop r-orb: %v", err)
	}
	if err := router.StopRunner(context.Background(), "r-dock"); err != nil {
		t.Fatalf("unexpected stop r-dock: %v", err)
	}
	if err := router.StopRunner(context.Background(), "r-unknown"); err != nil {
		t.Fatalf("unexpected stop unknown: %v", err)
	}

	if err := router.CleanupAll(context.Background()); err != nil {
		t.Fatalf("unexpected cleanup: %v", err)
	}

	// Test StopRunner when docker fails and falls back to vm
	failingDocker := &dummyDriver{
		backend:  "docker",
		stopFunc: func(id string) error { return fmt.Errorf("fail") },
	}
	routerFallback := NewRouter(failingDocker, orb, "auto", false, nil)
	if err := routerFallback.StopRunner(context.Background(), "any"); err != nil {
		t.Errorf("expected fallback to vm to succeed: %v", err)
	}
}

func TestRouter_Errors(t *testing.T) {
	dockerErr := &dummyDriver{
		backend:   "docker",
		cleanFunc: func() error { return fmt.Errorf("docker clean err") },
	}
	router := NewRouter(dockerErr, nil, "docker", false, nil)
	if err := router.CleanupAll(context.Background()); err == nil {
		t.Fatal("expected cleanup error")
	}
}
