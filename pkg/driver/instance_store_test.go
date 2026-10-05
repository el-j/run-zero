package driver

import (
	"os"
	"path/filepath"
	"testing"

	"github.com/el-j/run-zero/pkg/state"
)

func TestInstanceStore_Lifecycle(t *testing.T) {
	tmpDir, err := os.MkdirTemp("", "runzero-inst-*")
	if err != nil {
		t.Fatalf("temp dir error: %v", err)
	}
	defer os.RemoveAll(tmpDir)

	filePath := filepath.Join(tmpDir, "sub", "instances.json")
	store := NewInstanceStore(filePath)

	r1 := state.RunnerInfo{ID: "run-1", Name: "runzero-1", Status: "idle", State: "idle", Backend: "docker"}
	r2 := state.RunnerInfo{ID: "run-2", Name: "runzero-2", Status: "busy", State: "busy", Backend: "orbstack"}

	store.Register(r1)
	store.Register(r2)

	if len(store.List()) != 2 {
		t.Fatalf("expected 2 instances, got %d", len(store.List()))
	}

	got, ok := store.Get("run-1")
	if !ok || got.ID != "run-1" {
		t.Fatalf("expected to find run-1")
	}

	if !store.UpdateStatus("run-1", "busy", "running") {
		t.Fatalf("expected update to succeed")
	}
	if store.UpdateStatus("run-999", "busy", "running") {
		t.Fatalf("expected update on non-existent to fail")
	}

	gotUpdated, _ := store.Get("run-1")
	if gotUpdated.Status != "busy" {
		t.Errorf("expected busy status, got %s", gotUpdated.Status)
	}

	// Reload from new instance
	store2 := NewInstanceStore(filePath)
	if len(store2.List()) != 2 {
		t.Fatalf("expected 2 reloaded instances, got %d", len(store2.List()))
	}

	// Reconcile
	discovered := []state.RunnerInfo{
		{ID: "run-1"},
		{ID: "run-orphan"},
	}
	dead, orphans := store2.Reconcile(discovered)
	if len(dead) != 1 || dead[0] != "run-2" {
		t.Errorf("expected run-2 to be dead, got %v", dead)
	}
	if len(orphans) != 1 || orphans[0].ID != "run-orphan" {
		t.Errorf("expected run-orphan, got %v", orphans)
	}

	store2.Unregister("run-1")
	if len(store2.List()) != 1 {
		t.Errorf("expected 1 instance remaining")
	}
}

func TestInstanceStore_EmptyPathAndMalformed(t *testing.T) {
	store := NewInstanceStore("")
	store.Register(state.RunnerInfo{ID: "r"})
	if err := store.Save(); err != nil {
		t.Fatalf("expected nil error on empty path save: %v", err)
	}
	if err := store.Load(); err != nil {
		t.Fatalf("expected nil error on empty path load: %v", err)
	}

	tmpFile, _ := os.CreateTemp("", "bad-inst-*.json")
	defer os.Remove(tmpFile.Name())
	_, _ = tmpFile.WriteString("bad json")
	_ = tmpFile.Close()

	badStore := NewInstanceStore(tmpFile.Name())
	if err := badStore.Load(); err == nil {
		t.Fatal("expected error on malformed json load")
	}
}
