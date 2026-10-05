package driver

import (
	"context"
	"os/exec"
)

// CmdExecutor executes shell commands.
type CmdExecutor interface {
	Run(ctx context.Context, name string, args ...string) ([]byte, error)
	LookPath(file string) (string, error)
}

// OSExecutor executes commands via os/exec.
type OSExecutor struct{}

// Run executes command with context and returns combined stdout/stderr.
func (e *OSExecutor) Run(ctx context.Context, name string, args ...string) ([]byte, error) {
	cmd := exec.CommandContext(ctx, name, args...)
	return cmd.CombinedOutput()
}

// LookPath checks whether executable exists in system PATH.
func (e *OSExecutor) LookPath(file string) (string, error) {
	return exec.LookPath(file)
}
