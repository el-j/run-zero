package builder

import (
	"bufio"
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"os"
	"os/exec"
	"path/filepath"
	"strings"
	"sync"
	"time"

	"github.com/el-j/run-zero/pkg/driver"
)

// bridgePollInterval is how often a delegated bridge build is polled for progress.
var bridgePollInterval = time.Second

// LogHook is called whenever a new build log line is generated.
type LogHook func(line string)

// ProgressHook is called whenever build progress changes.
type ProgressHook func(progress ImageBuildProgress)

// BuildManager coordinates asynchronous building of golden VMs and container runners.
type BuildManager struct {
	mu           sync.RWMutex
	activeBuild  *ImageBuildProgress
	history      map[string]*ImageBuildProgress
	cancelFunc   context.CancelFunc
	gb           *GoldenBuilder
	exec         driver.CmdExecutor
	logHook      LogHook
	progressHook ProgressHook
	dockerDir    string
}

// NewBuildManager creates a new asynchronous build coordinator.
func NewBuildManager(gb *GoldenBuilder, exec driver.CmdExecutor, logHook LogHook, progressHook ProgressHook) *BuildManager {
	if exec == nil {
		exec = &driver.OSExecutor{}
	}
	if gb == nil {
		stateDir := os.Getenv("RUNZERO_STATE_DIR")
		if stateDir == "" {
			stateDir = ".runzero-state"
		}
		_ = os.MkdirAll(stateDir, 0755)
		provisionScript := os.Getenv("PROVISION_SCRIPT")
		if provisionScript == "" {
			provisionScript = "docker/provision-toolchain.sh"
		}
		gb = NewGoldenBuilder(Config{
			Distro:              "ubuntu:noble",
			RunnerVersion:       DefaultRunnerVersion,
			StateDir:            stateDir,
			ProvisionScriptPath: provisionScript,
		}, exec)
	}

	candidates := []string{"docker", "/workspace/docker", "../docker"}
	dockerDir := "docker"
	for _, cand := range candidates {
		if _, err := os.Stat(filepath.Join(cand, "Dockerfile")); err == nil {
			dockerDir = cand
			break
		}
	}

	return &BuildManager{
		history:      make(map[string]*ImageBuildProgress),
		gb:           gb,
		exec:         exec,
		logHook:      logHook,
		progressHook: progressHook,
		dockerDir:    dockerDir,
	}
}

// GetActiveBuild returns the current or most recent build progress.
func (m *BuildManager) GetActiveBuild() *ImageBuildProgress {
	m.mu.RLock()
	defer m.mu.RUnlock()
	if m.activeBuild == nil {
		return nil
	}
	cp := *m.activeBuild
	return &cp
}

// GetBuildByID returns build progress for a specific build ID.
func (m *BuildManager) GetBuildByID(id string) (*ImageBuildProgress, bool) {
	m.mu.RLock()
	defer m.mu.RUnlock()
	if m.activeBuild != nil && m.activeBuild.BuildID == id {
		cp := *m.activeBuild
		return &cp, true
	}
	b, ok := m.history[id]
	if !ok {
		return nil, false
	}
	cp := *b
	return &cp, true
}

// TriggerBuild launches an asynchronous image build.
func (m *BuildManager) TriggerBuild(ctx context.Context, req ImageBuildRequest) (*ImageBuildProgress, error) {
	m.mu.Lock()
	defer m.mu.Unlock()

	if m.activeBuild != nil && m.activeBuild.Status == string(StatusBuilding) {
		return nil, fmt.Errorf("a build is already in progress (id: %s)", m.activeBuild.BuildID)
	}

	target := req.Target
	if target == "" {
		target = "all"
	}
	arch := req.Arch
	if arch == "" {
		arch = "all"
	}

	buildID := fmt.Sprintf("build-%d", time.Now().Unix())
	now := time.Now().UTC().Format(time.RFC3339)

	progress := &ImageBuildProgress{
		BuildID:     buildID,
		Target:      target,
		Arch:        arch,
		Status:      string(StatusBuilding),
		ProgressPct: 0,
		CurrentStep: "Queued image build...",
		StartedAt:   now,
		LogLines:    make([]string, 0),
	}

	m.activeBuild = progress
	m.history[buildID] = progress

	buildCtx, cancel := context.WithCancel(context.Background())
	m.cancelFunc = cancel

	go m.runBuild(buildCtx, progress, req)

	cp := *progress
	return &cp, nil
}

// CancelBuild terminates any in-flight image build.
func (m *BuildManager) CancelBuild() error {
	m.mu.Lock()
	defer m.mu.Unlock()

	if m.activeBuild == nil || m.activeBuild.Status != string(StatusBuilding) {
		return nil
	}

	if m.cancelFunc != nil {
		m.cancelFunc()
		m.cancelFunc = nil
	}

	m.activeBuild.Status = string(StatusFailed)
	m.activeBuild.Error = "Build cancelled by operator"
	m.activeBuild.CompletedAt = time.Now().UTC().Format(time.RFC3339)
	m.appendLogLocked("[BUILD] ⚠ Build cancelled by operator.")

	if m.progressHook != nil {
		m.progressHook(*m.activeBuild)
	}
	return nil
}

func (m *BuildManager) runBuild(ctx context.Context, progress *ImageBuildProgress, req ImageBuildRequest) {
	defer m.finishBuild(progress)

	m.appendLog(fmt.Sprintf("[BUILD] Starting build job %s (target: %s, arch: %s)", progress.BuildID, progress.Target, progress.Arch))

	targets := buildTargets(progress.Target, progress.Arch)
	totalSteps := len(targets)
	for i, t := range targets {
		if ctx.Err() != nil {
			m.failBuild(progress, "Build cancelled")
			return
		}

		pct := int(float64(i) / float64(totalSteps) * 100)
		stepMsg := fmt.Sprintf("[%d/%d] Building %s image for %s...", i+1, totalSteps, t.kind, t.arch)
		m.updateStep(progress, stepMsg, pct)

		var err error
		if t.kind == "container" {
			err = m.buildContainerImage(ctx, t.arch)
		} else {
			err = m.buildVMImage(ctx, t.arch)
		}

		if err != nil {
			m.failBuild(progress, fmt.Sprintf("Failed building %s (%s): %v", t.kind, t.arch, err))
			return
		}
	}
}

// finishBuild marks a build that is still running as ready, clears the cancel
// hook and publishes the final progress.
func (m *BuildManager) finishBuild(progress *ImageBuildProgress) {
	m.mu.Lock()
	m.cancelFunc = nil
	if progress.Status == string(StatusBuilding) {
		progress.Status = string(StatusReady)
		progress.ProgressPct = 100
		progress.CompletedAt = time.Now().UTC().Format(time.RFC3339)
		progress.CurrentStep = "All target images built successfully."
	}
	m.mu.Unlock()

	if m.progressHook != nil {
		m.progressHook(*progress)
	}
}

type buildTarget struct {
	kind string
	arch string
}

// buildTargets expands a request's target ("all", "container", "vm") and arch
// ("all", "both", "arm64", "amd64") into the images to build: containers first,
// arm64 before amd64.
func buildTargets(target, arch string) []buildTarget {
	var archs []string
	for _, a := range []string{"arm64", "amd64"} {
		if arch == "all" || arch == "both" || arch == a {
			archs = append(archs, a)
		}
	}
	targets := make([]buildTarget, 0, 4)
	for _, kind := range []string{"container", "vm"} {
		if target != "all" && target != kind {
			continue
		}
		for _, a := range archs {
			targets = append(targets, buildTarget{kind: kind, arch: a})
		}
	}
	return targets
}

func (m *BuildManager) buildContainerImage(ctx context.Context, arch string) error {
	tag := fmt.Sprintf("local-github-runner:%s", arch)
	platform := fmt.Sprintf("linux/%s", arch)
	buildDir := m.dockerDir
	if _, err := os.Stat(filepath.Join(buildDir, "Dockerfile")); err != nil {
		for _, cand := range []string{"docker", "/workspace/docker", "../docker"} {
			if _, err := os.Stat(filepath.Join(cand, "Dockerfile")); err == nil {
				buildDir = cand
				break
			}
		}
	}
	m.appendLog(fmt.Sprintf("[BUILD:CONTAINER] Executing docker build -t %s --platform %s %s", tag, platform, buildDir))

	cmd := exec.CommandContext(ctx, "docker", "build", "--platform", platform, "-t", tag, buildDir)
	return m.streamCommandOutput(cmd, "[DOCKER]")
}

func (m *BuildManager) buildVMImage(ctx context.Context, arch string) error {
	m.appendLog(fmt.Sprintf("[BUILD:VM] Provisioning OrbStack golden base VM for %s...", arch))
	if bridgeURL := os.Getenv("HOST_VM_BRIDGE_URL"); bridgeURL != "" && bridgeURL != "none" {
		if _, err := m.exec.Run(ctx, "orbctl", "version"); err != nil {
			return m.buildVMImageViaBridge(ctx, bridgeURL, arch)
		}
	}
	built, err := m.gb.BuildBaseImage(ctx, arch)
	if err != nil {
		return err
	}
	if built {
		m.appendLog(fmt.Sprintf("[BUILD:VM] Successfully built and promoted %s", m.gb.BaseImageName(arch)))
	} else {
		m.appendLog(fmt.Sprintf("[BUILD:VM] Golden base %s is already up to date.", m.gb.BaseImageName(arch)))
	}
	if stopped, err := m.gb.EnsureBaseImagesStopped(ctx); err == nil && len(stopped) > 0 {
		m.appendLog(fmt.Sprintf("[BUILD:VM] Verified golden base VMs are stopped: %v", stopped))
	}
	return nil
}

// bridgeBuildTimeout bounds each request to the host bridge during a VM build.
var bridgeBuildTimeout = 30 * time.Second

func (m *BuildManager) buildVMImageViaBridge(ctx context.Context, bridgeURL, arch string) error {
	m.appendLog(fmt.Sprintf("[BUILD:VM] Delegating VM build to Host VM Bridge at %s...", bridgeURL))
	base := strings.TrimSuffix(bridgeURL, "/")
	token := os.Getenv("RUNZERO_BRIDGE_TOKEN")
	client := &http.Client{Timeout: bridgeBuildTimeout}

	buildID, err := startBridgeBuild(ctx, client, base, token, arch)
	if err != nil {
		return err
	}

	pollURL := fmt.Sprintf("%s/api/images/build/%s", base, buildID)
	lastLogIndex := 0
	ticker := time.NewTicker(bridgePollInterval)
	defer ticker.Stop()

	for {
		select {
		case <-ctx.Done():
			cancelBridgeBuild(client, base, token, buildID)
			return ctx.Err()
		case <-ticker.C:
			prog, ok := fetchBridgeProgress(ctx, client, pollURL, token)
			if !ok {
				continue
			}
			lastLogIndex = m.mirrorBridgeProgress(prog, lastLogIndex)
			if prog.Status == string(StatusReady) {
				return nil
			}
			if prog.Status == string(StatusFailed) {
				if prog.Error != "" {
					return fmt.Errorf("%s", prog.Error)
				}
				return fmt.Errorf("bridge build failed")
			}
		}
	}
}

// startBridgeBuild asks the host bridge to build the VM image for arch and
// returns the bridge's build ID.
func startBridgeBuild(ctx context.Context, client *http.Client, base, token, arch string) (string, error) {
	// Marshaling a struct of plain strings cannot fail.
	payload, _ := json.Marshal(ImageBuildRequest{
		Target: "vm",
		Arch:   arch,
	})
	httpReq, err := http.NewRequestWithContext(ctx, http.MethodPost, base+"/api/actions/build-image", bytes.NewReader(payload))
	if err != nil {
		return "", err
	}
	httpReq.Header.Set("Content-Type", "application/json")
	if token != "" {
		httpReq.Header.Set("Authorization", "Bearer "+token)
	}

	resp, err := client.Do(httpReq)
	if err != nil {
		return "", fmt.Errorf("failed to contact bridge: %w", err)
	}
	defer func() { _ = resp.Body.Close() }()

	if resp.StatusCode != http.StatusOK && resp.StatusCode != http.StatusAccepted {
		var errResp map[string]string
		_ = json.NewDecoder(resp.Body).Decode(&errResp)
		if msg, ok := errResp["error"]; ok {
			return "", fmt.Errorf("bridge build error: %s", msg)
		}
		return "", fmt.Errorf("bridge returned HTTP %d", resp.StatusCode)
	}

	var initProg ImageBuildProgress
	if err := json.NewDecoder(resp.Body).Decode(&initProg); err != nil {
		return "", fmt.Errorf("failed to parse bridge response: %w", err)
	}
	return initProg.BuildID, nil
}

// cancelBridgeBuild asks the bridge to cancel buildID (best effort; the
// caller's context is already done, so it is not used).
func cancelBridgeBuild(client *http.Client, base, token, buildID string) {
	cPayload, _ := json.Marshal(map[string]string{"build_id": buildID})
	cReq, _ := http.NewRequest(http.MethodPost, base+"/api/actions/build-image/cancel", bytes.NewReader(cPayload))
	if cReq != nil {
		cReq.Header.Set("Content-Type", "application/json")
		if token != "" {
			cReq.Header.Set("Authorization", "Bearer "+token)
		}
		_, _ = client.Do(cReq)
	}
}

// fetchBridgeProgress polls the bridge build once; ok is false when the poll
// failed and should simply be retried.
func fetchBridgeProgress(ctx context.Context, client *http.Client, pollURL, token string) (ImageBuildProgress, bool) {
	var prog ImageBuildProgress
	pReq, err := http.NewRequestWithContext(ctx, http.MethodGet, pollURL, nil)
	if err != nil {
		return prog, false
	}
	if token != "" {
		pReq.Header.Set("Authorization", "Bearer "+token)
	}
	pResp, err := client.Do(pReq)
	if err != nil {
		return prog, false
	}
	err = json.NewDecoder(pResp.Body).Decode(&prog)
	_ = pResp.Body.Close()
	return prog, err == nil
}

// mirrorBridgeProgress copies new bridge log lines and the current step into the
// local build, returning the new log offset.
func (m *BuildManager) mirrorBridgeProgress(prog ImageBuildProgress, lastLogIndex int) int {
	for _, line := range prog.LogLines[min(lastLogIndex, len(prog.LogLines)):] {
		m.appendLog(line)
	}
	lastLogIndex = max(lastLogIndex, len(prog.LogLines))
	if prog.CurrentStep != "" {
		m.mu.Lock()
		if m.activeBuild != nil {
			m.activeBuild.CurrentStep = prog.CurrentStep
		}
		m.mu.Unlock()
	}
	return lastLogIndex
}

func (m *BuildManager) streamCommandOutput(cmd *exec.Cmd, prefix string) error {
	stdout, err := cmd.StdoutPipe()
	if err != nil {
		return err
	}
	stderr, err := cmd.StderrPipe()
	if err != nil {
		return err
	}

	if err := cmd.Start(); err != nil {
		return err
	}

	var wg sync.WaitGroup
	wg.Add(2)

	scanStream := func(r io.Reader) {
		defer wg.Done()
		scanner := bufio.NewScanner(r)
		for scanner.Scan() {
			line := scanner.Text()
			m.appendLog(fmt.Sprintf("%s %s", prefix, line))
		}
	}

	go scanStream(stdout)
	go scanStream(stderr)

	wg.Wait()
	return cmd.Wait()
}

func (m *BuildManager) updateStep(p *ImageBuildProgress, step string, pct int) {
	m.mu.Lock()
	p.CurrentStep = step
	p.ProgressPct = pct
	m.mu.Unlock()

	if m.progressHook != nil {
		m.progressHook(*p)
	}
}

func (m *BuildManager) failBuild(p *ImageBuildProgress, errText string) {
	m.mu.Lock()
	p.Status = string(StatusFailed)
	p.Error = errText
	p.CompletedAt = time.Now().UTC().Format(time.RFC3339)
	m.appendLogLocked(fmt.Sprintf("[BUILD] ✗ %s", errText))
	m.mu.Unlock()

	if m.progressHook != nil {
		m.progressHook(*p)
	}
}

func (m *BuildManager) appendLog(line string) {
	m.mu.Lock()
	m.appendLogLocked(line)
	m.mu.Unlock()
}

// maxBuildLogLines bounds the log kept for the active build.
const maxBuildLogLines = 1000

func (m *BuildManager) appendLogLocked(line string) {
	if m.activeBuild != nil {
		lines := append(m.activeBuild.LogLines, line)
		m.activeBuild.LogLines = lines[max(len(lines)-maxBuildLogLines, 0):]
	}
	if m.logHook != nil {
		m.logHook(line)
	}
}
