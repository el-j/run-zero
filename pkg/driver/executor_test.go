package driver

import (
	"context"
	"testing"
)

func TestOSExecutor(t *testing.T) {
	exec := &OSExecutor{}
	out, err := exec.Run(context.Background(), "echo", "runzero")
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if len(out) == 0 {
		t.Errorf("expected non-empty output from echo")
	}

	path, err := exec.LookPath("echo")
	if err != nil || path == "" {
		t.Errorf("expected to find echo executable: %v", err)
	}
}
