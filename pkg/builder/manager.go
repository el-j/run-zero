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
	"strings"
	"sync"
	"time"

	"github.com/el-j/run-zero/pkg/driver"
)

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

	dockerDir := "docker"
	if _, err := os.Stat("docker/Dockerfile"); err != nil {
		if _, err := os.Stat("../docker/Dockerfile"); err == nil {
			dockerDir = "../docker"
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
	defer func() {
		m.mu.Lock()
		if m.cancelFunc != nil {
			m.cancelFunc = nil
		}
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
	}()

	m.appendLog(fmt.Sprintf("[BUILD] Starting build job %s (target: %s, arch: %s)", progress.BuildID, progress.Target, progress.Arch))

	targets := make([]struct {
		kind string
		arch string
	}, 0)

	// Determine Docker targets
	if progress.Target == "all" || progress.Target == "container" {
		if progress.Arch == "all" || progress.Arch == "both" || progress.Arch == "arm64" {
			targets = append(targets, struct {
				kind string
				arch string
			}{"container", "arm64"})
		}
		if progress.Arch == "all" || progress.Arch == "both" || progress.Arch == "amd64" {
			targets = append(targets, struct {
				kind string
				arch string
			}{"container", "amd64"})
		}
	}

	// Determine VM targets
	if progress.Target == "all" || progress.Target == "vm" {
		if progress.Arch == "all" || progress.Arch == "both" || progress.Arch == "arm64" {
			targets = append(targets, struct {
				kind string
				arch string
			}{"vm", "arm64"})
		}
		if progress.Arch == "all" || progress.Arch == "both" || progress.Arch == "amd64" {
			targets = append(targets, struct {
				kind string
				arch string
			}{"vm", "amd64"})
		}
	}

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

func (m *BuildManager) buildContainerImage(ctx context.Context, arch string) error {
	tag := fmt.Sprintf("local-github-runner:%s", arch)
	platform := fmt.Sprintf("linux/%s", arch)
	m.appendLog(fmt.Sprintf("[BUILD:CONTAINER] Executing docker build -t %s --platform %s %s", tag, platform, m.dockerDir))

	cmd := exec.CommandContext(ctx, "docker", "build", "--platform", platform, "-t", tag, m.dockerDir)
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
	return nil
}

func (m *BuildManager) buildVMImageViaBridge(ctx context.Context, bridgeURL, arch string) error {
	m.appendLog(fmt.Sprintf("[BUILD:VM] Delegating VM build to Host VM Bridge at %s...", bridgeURL))
	reqURL := strings.TrimSuffix(bridgeURL, "/") + "/api/actions/build-image"
	payload, err := json.Marshal(ImageBuildRequest{
		Target: "vm",
		Arch:   arch,
	})
	if err != nil {
		return err
	}

	httpReq, err := http.NewRequestWithContext(ctx, http.MethodPost, reqURL, bytes.NewReader(payload))
	if err != nil {
		return err
	}
	httpReq.Header.Set("Content-Type", "application/json")
	if token := os.Getenv("RUNZERO_BRIDGE_TOKEN"); token != "" {
		httpReq.Header.Set("Authorization", "Bearer "+token)
	}

	client := &http.Client{Timeout: 30 * time.Second}
	resp, err := client.Do(httpReq)
	if err != nil {
		return fmt.Errorf("failed to contact bridge: %w", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK && resp.StatusCode != http.StatusAccepted {
		var errResp map[string]string
		_ = json.NewDecoder(resp.Body).Decode(&errResp)
		if msg, ok := errResp["error"]; ok {
			return fmt.Errorf("bridge build error: %s", msg)
		}
		return fmt.Errorf("bridge returned HTTP %d", resp.StatusCode)
	}

	var initProg ImageBuildProgress
	if err := json.NewDecoder(resp.Body).Decode(&initProg); err != nil {
		return fmt.Errorf("failed to parse bridge response: %w", err)
	}

	pollURL := fmt.Sprintf("%s/api/images/build/%s", strings.TrimSuffix(bridgeURL, "/"), initProg.BuildID)
	token := os.Getenv("RUNZERO_BRIDGE_TOKEN")
	lastLogIndex := 0

	ticker := time.NewTicker(1 * time.Second)
	defer ticker.Stop()

	for {
		select {
		case <-ctx.Done():
			cancelURL := strings.TrimSuffix(bridgeURL, "/") + "/api/actions/build-image/cancel"
			cPayload, _ := json.Marshal(map[string]string{"build_id": initProg.BuildID})
			cReq, _ := http.NewRequest(http.MethodPost, cancelURL, bytes.NewReader(cPayload))
			if cReq != nil {
				cReq.Header.Set("Content-Type", "application/json")
				if token != "" {
					cReq.Header.Set("Authorization", "Bearer "+token)
				}
				_, _ = client.Do(cReq)
			}
			return ctx.Err()
		case <-ticker.C:
			pReq, err := http.NewRequestWithContext(ctx, http.MethodGet, pollURL, nil)
			if err != nil {
				continue
			}
			if token != "" {
				pReq.Header.Set("Authorization", "Bearer "+token)
			}
			pResp, err := client.Do(pReq)
			if err != nil {
				continue
			}
			var curProg ImageBuildProgress
			err = json.NewDecoder(pResp.Body).Decode(&curProg)
			pResp.Body.Close()
			if err != nil {
				continue
			}

			if len(curProg.LogLines) > lastLogIndex {
				for _, line := range curProg.LogLines[lastLogIndex:] {
					m.appendLog(line)
				}
				lastLogIndex = len(curProg.LogLines)
			}

			if curProg.CurrentStep != "" {
				m.mu.Lock()
				if m.activeBuild != nil {
					m.activeBuild.CurrentStep = curProg.CurrentStep
				}
				m.mu.Unlock()
			}

			if curProg.Status == string(StatusReady) {
				return nil
			}
			if curProg.Status == string(StatusFailed) {
				if curProg.Error != "" {
					return fmt.Errorf("%s", curProg.Error)
				}
				return fmt.Errorf("bridge build failed")
			}
		}
	}
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

func (m *BuildManager) appendLogLocked(line string) {
	if m.activeBuild != nil {
		if len(m.activeBuild.LogLines) > 1000 {
			m.activeBuild.LogLines = m.activeBuild.LogLines[len(m.activeBuild.LogLines)-1000:]
		}
		m.activeBuild.LogLines = append(m.activeBuild.LogLines, line)
	}
	if m.logHook != nil {
		m.logHook(line)
	}
}
