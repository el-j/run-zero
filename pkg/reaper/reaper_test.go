package reaper

import (
	"context"
	"testing"
	"time"

	"github.com/el-j/run-zero/pkg/driver"
	"github.com/el-j/run-zero/pkg/state"
)

type mockDriver struct {
	driver.RunnerDriver
	stopped []string
}

func (m *mockDriver) StopRunner(ctx context.Context, id string) error {
	m.stopped = append(m.stopped, id)
	return nil
}

func TestClassify(t *testing.T) {
	timeouts := Timeouts{
		IdleSeconds:         600,
		UnregisteredSeconds: 180,
		BusySeconds:         7200,
	}

	// 1. Not registered, conclusive, past grace period
	if act := Classify(200, nil, true, timeouts); act != ActionReapUnregistered {
		t.Errorf("expected ReapUnregistered, got %s", act)
	}
	// 2. Not registered, inconclusive
	if act := Classify(200, nil, false, timeouts); act != ActionKeep {
		t.Errorf("expected Keep for inconclusive, got %s", act)
	}

	// 3. Registered & busy
	busyReg := &Registration{Busy: true}
	if act := Classify(1000, busyReg, true, timeouts); act != ActionKeep {
		t.Errorf("expected Keep for busy runner within limit, got %s", act)
	}
	if act := Classify(8000, busyReg, true, timeouts); act != ActionCheckStaleBusy {
		t.Errorf("expected CheckStaleBusy, got %s", act)
	}

	// 4. Registered & idle
	idleReg := &Registration{Busy: false}
	if act := Classify(300, idleReg, true, timeouts); act != ActionKeep {
		t.Errorf("expected Keep for idle runner within timeout, got %s", act)
	}
	if act := Classify(700, idleReg, true, timeouts); act != ActionReapIdle {
		t.Errorf("expected ReapIdle, got %s", act)
	}
}

func TestReconcileLocalRunners(t *testing.T) {
	d := &mockDriver{}
	reaper := NewReaper(d, nil, Timeouts{})

	createdOld := time.Unix(1000, 0).UTC().Format(time.RFC3339)
	createdNew := time.Unix(1900, 0).UTC().Format(time.RFC3339)

	runners := []state.RunnerInfo{
		{ID: "r-unreg", Name: "runzero-unreg", CreatedAt: &createdOld},
		{ID: "r-idle-standby", Name: "runzero-idle-1", CreatedAt: &createdOld},
		{ID: "r-idle-reap", Name: "runzero-idle-2", CreatedAt: &createdOld},
		{ID: "r-fresh", Name: "runzero-fresh", CreatedAt: &createdNew},
	}

	registrations := map[string]Registration{
		"runzero-idle-1": {Name: "runzero-idle-1", Busy: false},
		"runzero-idle-2": {Name: "runzero-idle-2", Busy: false},
		"runzero-fresh":  {Name: "runzero-fresh", Busy: false},
	}

	now := float64(2000)
	reaped := reaper.ReconcileLocalRunners(context.Background(), runners, registrations, true, now, 1)

	if len(reaped) != 2 {
		t.Fatalf("expected 2 reaped runners (r-unreg, r-idle-reap), got %d: %v", len(reaped), reaped)
	}
	if reaped[0] != "r-unreg" || reaped[1] != "r-idle-reap" {
		t.Errorf("unexpected reaped list: %v", reaped)
	}
	if len(d.stopped) != 2 {
		t.Errorf("expected 2 stops executed on driver, got %d", len(d.stopped))
	}
}

func TestScopes(t *testing.T) {
	if RepoScope("owner/repo") != "repos/owner/repo" {
		t.Errorf("unexpected repo scope")
	}
	if OrgScope("my-org") != "orgs/my-org" {
		t.Errorf("unexpected org scope")
	}
}
