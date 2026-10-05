package github

import (
	"strings"
	"testing"

	"github.com/el-j/run-zero/pkg/state"
)

func TestReconciler_Reconcile(t *testing.T) {
	pm, _ := NewPriorityManager("", []string{"org/prio-repo"}, []string{"org/paused-repo"})
	reconciler := NewReconciler(pm)

	time1 := "2026-10-05T09:00:00Z"
	time2 := "2026-10-05T09:05:00Z"

	jobs := []state.QueuedJob{
		{ID: 1, Repo: "org/paused-repo", Name: "job-paused", CreatedAt: &time1},
		{ID: 2, Repo: "org/normal-repo", Name: "job-normal-1", CreatedAt: &time2},
		{ID: 3, Repo: "org/prio-repo", Name: "job-prio-1", CreatedAt: &time2},
		{ID: 4, Repo: "org/normal-repo", Name: "job-normal-2", CreatedAt: &time1},
	}

	// busyRunners: 1, maxRunners: 3 => freeSlots: 2
	result := reconciler.Reconcile(jobs, 1, 3)

	if len(result) != 4 {
		t.Fatalf("expected 4 jobs, got %d", len(result))
	}

	// Active job 1 should be org/prio-repo (priority 1)
	if result[0].ID != 3 {
		t.Errorf("expected first job to be prio-repo (id 3), got id %d", result[0].ID)
	}
	if *result[0].QueuePosition != 1 || result[0].WaitingReason != nil {
		t.Errorf("expected job 0 to have position 1 and nil waiting reason, got pos %d, reason %v", *result[0].QueuePosition, result[0].WaitingReason)
	}

	// Active job 2 should be org/normal-repo job 4 (older timestamp time1 vs time2)
	if result[1].ID != 4 {
		t.Errorf("expected second job to be normal-repo (id 4), got id %d", result[1].ID)
	}
	if *result[1].QueuePosition != 2 || result[1].WaitingReason != nil {
		t.Errorf("expected job 1 to have position 2 and nil waiting reason")
	}

	// Active job 3 should be org/normal-repo job 2 (exceeds freeSlots 2, pos 3)
	if result[2].ID != 2 {
		t.Errorf("expected third job to be normal-repo (id 2), got id %d", result[2].ID)
	}
	if *result[2].QueuePosition != 3 || result[2].WaitingReason == nil || !strings.Contains(*result[2].WaitingReason, "runner capacity reached") {
		t.Errorf("expected job 2 to be capacity-capped, got reason: %v", result[2].WaitingReason)
	}

	// Job 4 should be paused job
	if result[3].ID != 1 {
		t.Errorf("expected fourth job to be paused (id 1), got id %d", result[3].ID)
	}
	if result[3].QueuePosition != nil {
		t.Errorf("expected paused job to have nil queue position")
	}
	if result[3].WaitingReason == nil || *result[3].WaitingReason != "repository paused by administrator" {
		t.Errorf("expected administrator paused reason, got %v", result[3].WaitingReason)
	}
}

func TestReconciler_FreeSlotsClamp(t *testing.T) {
	pm, _ := NewPriorityManager("", []string{"prio-a"}, nil)
	reconciler := NewReconciler(pm)

	jobs := []state.QueuedJob{
		{ID: 10, Repo: "normal-z", Name: "j1"},
		{ID: 20, Repo: "prio-a", Name: "j2"},
		{ID: 30, Repo: "normal-a", Name: "j3"},
	}

	// Busy runners exceed max runners -> freeSlots clamps to 0
	result := reconciler.Reconcile(jobs, 5, 2)
	if len(result) != 3 {
		t.Fatalf("expected 3 jobs")
	}
	if result[0].ID != 20 {
		t.Errorf("expected prio-a to be sorted first")
	}
	if result[0].WaitingReason == nil || !strings.Contains(*result[0].WaitingReason, "runner capacity reached") {
		t.Errorf("expected runner capacity reached reason when free slots is 0")
	}
}
