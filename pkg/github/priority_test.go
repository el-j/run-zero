package github

import (
	"os"
	"path/filepath"
	"testing"
)

func TestPriorityManager_Lifecycle(t *testing.T) {
	tmpDir, err := os.MkdirTemp("", "runzero-prio-*")
	if err != nil {
		t.Fatalf("failed creating temp dir: %v", err)
	}
	defer os.RemoveAll(tmpDir)

	filePath := filepath.Join(tmpDir, "sub", "repo_priority.json")
	pm, err := NewPriorityManager(filePath, []string{"repo-a", "repo-b"}, []string{"repo-paused"})
	if err != nil {
		t.Fatalf("failed creating priority manager: %v", err)
	}

	if !pm.IsPaused("repo-paused") {
		t.Errorf("expected repo-paused to be paused")
	}
	if pm.IsPaused("repo-a") {
		t.Errorf("expected repo-a to not be paused")
	}

	repos := []string{"repo-z", "repo-b", "repo-x", "repo-a"}
	sorted := pm.SortRepos(repos)
	if sorted[0] != "repo-a" || sorted[1] != "repo-b" {
		t.Fatalf("unexpected sorted repos: %v", sorted)
	}

	// Persist
	if err := pm.Save(); err != nil {
		t.Fatalf("failed saving priority: %v", err)
	}

	// Reload from new instance
	pm2, err := NewPriorityManager(filePath, nil, nil)
	if err != nil {
		t.Fatalf("failed loading manager: %v", err)
	}
	prio, paused := pm2.GetState()
	if len(prio) != 2 || prio[0] != "repo-a" || prio[1] != "repo-b" {
		t.Fatalf("unexpected loaded priority: %v", prio)
	}
	if len(paused) != 1 || paused[0] != "repo-paused" {
		t.Fatalf("unexpected loaded paused: %v", paused)
	}

	// Update
	if err := pm2.Update([]string{"repo-c"}, []string{"repo-d"}); err != nil {
		t.Fatalf("failed updating manager: %v", err)
	}
	if !pm2.IsPaused("repo-d") {
		t.Errorf("expected repo-d to be paused after update")
	}
}

func TestPriorityManager_EmptyFileAndMalformed(t *testing.T) {
	pm, _ := NewPriorityManager("", []string{"repo-1"}, nil)
	if err := pm.Save(); err != nil {
		t.Fatalf("save on empty path should succeed with nil: %v", err)
	}
	if err := pm.Load(); err != nil {
		t.Fatalf("load on empty path should succeed with nil: %v", err)
	}

	tmpFile, _ := os.CreateTemp("", "bad-prio-*.json")
	defer os.Remove(tmpFile.Name())
	_, _ = tmpFile.WriteString("not json")
	_ = tmpFile.Close()

	pmBad, _ := NewPriorityManager(tmpFile.Name(), nil, nil)
	if err := pmBad.Load(); err == nil {
		t.Fatal("expected error on malformed JSON")
	}
}
