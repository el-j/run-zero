package builder

import (
	"context"
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"os"
	"path/filepath"
	"strings"
	"sync"
	"time"

	"github.com/el-j/run-zero/pkg/driver"
)

// GoldenBuilder manages VM golden image lifecycle and zero-downtime rebuilds.
type GoldenBuilder struct {
	cfg    Config
	exec   driver.CmdExecutor
	mu     sync.RWMutex
	events chan ImageEvent
}

// NewGoldenBuilder creates an initialized builder instance.
func NewGoldenBuilder(cfg Config, exec driver.CmdExecutor) *GoldenBuilder {
	if cfg.RunnerVersion == "" {
		cfg.RunnerVersion = DefaultRunnerVersion
	}
	if cfg.Distro == "" {
		cfg.Distro = "ubuntu:24.04"
	}
	if exec == nil {
		exec = &driver.OSExecutor{}
	}
	return &GoldenBuilder{
		cfg:    cfg,
		exec:   exec,
		events: make(chan ImageEvent, 32),
	}
}

// BaseImageName returns the VM name for a golden base image.
func (b *GoldenBuilder) BaseImageName(arch string) string {
	return BaseImagePrefix + arch
}

// StagingImageName returns the staging VM name while building.
func (b *GoldenBuilder) StagingImageName(arch string) string {
	return b.BaseImageName(arch) + "-building"
}

// StampPath returns the file recording which runner version the image was built with.
func (b *GoldenBuilder) StampPath(arch string) string {
	return filepath.Join(b.cfg.StateDir, b.BaseImageName(arch)+".runner-version")
}

// IsStale checks if base image runner version matches configured version.
func (b *GoldenBuilder) IsStale(arch string) bool {
	data, err := os.ReadFile(b.StampPath(arch))
	if err != nil {
		return true
	}
	return strings.TrimSpace(string(data)) != b.stampValue()
}

// WriteStamp records the runner version for a freshly built image.
func (b *GoldenBuilder) WriteStamp(arch string) error {
	p := b.StampPath(arch)
	if err := os.MkdirAll(filepath.Dir(p), 0755); err != nil {
		return err
	}
	return os.WriteFile(p, []byte(b.stampValue()+"\n"), 0644)
}

// stampValue identifies what a golden image was built from: the runner version plus a
// short hash of the toolchain provisioning script. Editing the script (new apt
// package, Node version, ...) therefore marks existing images stale and they get
// rebuilt, instead of silently keeping an outdated toolchain.
func (b *GoldenBuilder) stampValue() string {
	if b.cfg.ProvisionScriptPath == "" {
		return b.cfg.RunnerVersion
	}
	data, err := os.ReadFile(b.cfg.ProvisionScriptPath)
	if err != nil {
		return b.cfg.RunnerVersion
	}
	sum := sha256.Sum256(data)
	return b.cfg.RunnerVersion + "+" + hex.EncodeToString(sum[:])[:12]
}

// ListVMs queries OrbStack for existing virtual machine names.
func (b *GoldenBuilder) ListVMs(ctx context.Context) ([]string, error) {
	out, err := b.exec.Run(ctx, "orbctl", "list", "--format", "json")
	if err != nil {
		return nil, err
	}
	var vms []struct {
		Name string `json:"name"`
	}
	if err := json.Unmarshal(out, &vms); err != nil {
		return nil, err
	}
	names := make([]string, len(vms))
	for i, v := range vms {
		names[i] = v.Name
	}
	return names, nil
}

// BaseImageExists checks if the golden base image exists on the host.
func (b *GoldenBuilder) BaseImageExists(ctx context.Context, arch string) bool {
	names, err := b.ListVMs(ctx)
	if err != nil {
		return false
	}
	target := b.BaseImageName(arch)
	for _, n := range names {
		if n == target {
			return true
		}
	}
	return false
}

// EmitEvent dispatches a lifecycle progress notification.
func (b *GoldenBuilder) EmitEvent(status ImageStatus, arch, detail string) {
	evt := ImageEvent{
		Status: status,
		Arch:   arch,
		Detail: detail,
		Time:   time.Now().UTC(),
	}
	select {
	case b.events <- evt:
	default:
	}
}

// Events returns the notification channel.
func (b *GoldenBuilder) Events() <-chan ImageEvent {
	return b.events
}
