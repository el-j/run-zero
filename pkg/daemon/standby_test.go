package daemon

import (
	"context"
	"errors"
	"testing"

	"github.com/el-j/run-zero/pkg/state"
)

func standbyRoutes(repos ...string) map[string]string {
	routes := map[string]string{}
	for _, r := range repos {
		routes["/repos/"+r+"/actions/runners/registration-token"] = `{"token":"tok","expires_at":"2030-01-01T00:00:00Z"}`
	}
	return routes
}

func TestTopUpStandby_FillsPoolRoundRobin(t *testing.T) {
	_, gh := newFakeGH(t, standbyRoutes("o/a", "o/b"))
	cfg := baseCfg("o/a", "o/b")
	cfg.MinRunners = 3
	drv := &mockDriver{}
	s, st := newTestScaler(t, cfg, gh, drv, nil, "o/a", "o/b")

	active := s.topUpStandby(context.Background(), nil, []string{"o/a", "o/b"})

	if len(active) != 3 || len(drv.spawned) != 3 {
		t.Fatalf("expected 3 standby runners, got %d active / %d spawned", len(active), len(drv.spawned))
	}
	got := []string{drv.spawned[0].Repo, drv.spawned[1].Repo, drv.spawned[2].Repo}
	if got[0] != "o/a" || got[1] != "o/b" || got[2] != "o/a" {
		t.Fatalf("expected round-robin o/a, o/b, o/a; got %v", got)
	}
	for _, spec := range drv.spawned {
		if spec.JobID != nil || spec.RunID != nil || spec.Token != "tok" {
			t.Fatalf("standby spec must have no job and a token: %+v", spec)
		}
	}
	if !hasLog(st, "(standby, ") {
		t.Fatal("expected a standby spawn log")
	}
}

func TestTopUpStandby_CountsExistingStandbyAndRespectsMax(t *testing.T) {
	_, gh := newFakeGH(t, standbyRoutes("o/a"))
	cfg := baseCfg("o/a")
	cfg.MinRunners, cfg.MaxRunners = 3, 3
	drv := &mockDriver{}
	s, _ := newTestScaler(t, cfg, gh, drv, nil, "o/a")
	jobID := int64(7)

	// One idle standby and one busy runner already exist: one more standby
	// would be needed, and MAX_RUNNERS=3 leaves room for exactly one.
	active := []state.RunnerInfo{{ID: "idle"}, {ID: "busy", JobID: &jobID}}
	active = s.topUpStandby(context.Background(), active, []string{"o/a"})
	if len(drv.spawned) != 1 || len(active) != 3 {
		t.Fatalf("expected 1 spawn up to 3 runners, got %d spawned / %d active", len(drv.spawned), len(active))
	}

	// At MAX_RUNNERS the pool cannot grow further.
	cfg.MinRunners = 5
	if s.topUpStandby(context.Background(), active, []string{"o/a"}); len(drv.spawned) != 1 {
		t.Fatalf("pool must not exceed MAX_RUNNERS, got %d spawns", len(drv.spawned))
	}
}

func TestTopUpStandby_DoesNothingWhenDisabledPausedOrFailing(t *testing.T) {
	_, gh := newFakeGH(t, standbyRoutes("o/a"))
	tracked := []string{"o/a"}

	t.Run("MIN_RUNNERS=0", func(t *testing.T) {
		drv := &mockDriver{}
		s, _ := newTestScaler(t, baseCfg("o/a"), gh, drv, nil, "o/a")
		s.topUpStandby(context.Background(), nil, tracked)
		if len(drv.spawned) != 0 {
			t.Fatal("no standby expected")
		}
	})
	t.Run("autoscaler paused", func(t *testing.T) {
		cfg := baseCfg("o/a")
		cfg.MinRunners = 1
		drv := &mockDriver{}
		s, st := newTestScaler(t, cfg, gh, drv, nil, "o/a")
		st.SetAutoscalerStatus("paused")
		s.topUpStandby(context.Background(), nil, tracked)
		if len(drv.spawned) != 0 {
			t.Fatal("no standby while paused")
		}
	})
	t.Run("every repo paused", func(t *testing.T) {
		cfg := baseCfg("o/a")
		cfg.MinRunners = 1
		drv := &mockDriver{}
		s, _ := newTestScaler(t, cfg, gh, drv, []string{"o/a"}, "o/a")
		s.topUpStandby(context.Background(), nil, tracked)
		if len(drv.spawned) != 0 {
			t.Fatal("no standby for paused repos")
		}
	})
	t.Run("no driver", func(t *testing.T) {
		cfg := baseCfg("o/a")
		cfg.MinRunners = 1
		s, _ := newTestScaler(t, cfg, gh, nil, nil, "o/a")
		s.driver = nil
		if got := s.topUpStandby(context.Background(), nil, tracked); len(got) != 0 {
			t.Fatal("no standby without a driver")
		}
	})
	t.Run("spawn failure stops the top-up", func(t *testing.T) {
		cfg := baseCfg("o/a")
		cfg.MinRunners = 3
		drv := &mockDriver{spawnErr: errors.New("boom")}
		s, _ := newTestScaler(t, cfg, gh, drv, nil, "o/a")
		s.topUpStandby(context.Background(), nil, tracked)
		if len(drv.spawned) != 1 {
			t.Fatalf("expected one failed attempt, got %d", len(drv.spawned))
		}
	})
}
