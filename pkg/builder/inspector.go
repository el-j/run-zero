package builder

import (
	"context"
	"os"
	"strings"

	"github.com/el-j/run-zero/pkg/driver"
)

// ImageInspector inspects infrastructure readiness for VMs and runner containers.
type ImageInspector struct {
	gb   *GoldenBuilder
	exec driver.CmdExecutor
}

// NewImageInspector creates a new inspector instance.
func NewImageInspector(gb *GoldenBuilder, exec driver.CmdExecutor) *ImageInspector {
	if exec == nil {
		exec = &driver.OSExecutor{}
	}
	if gb == nil {
		stateDir := ".runzero-state"
		if _, err := os.Stat(stateDir); err != nil {
			_ = os.MkdirAll(stateDir, 0755)
		}
		gb = NewGoldenBuilder(Config{
			Distro:        "ubuntu:noble",
			RunnerVersion: DefaultRunnerVersion,
			StateDir:      stateDir,
		}, exec)
	}
	return &ImageInspector{
		gb:   gb,
		exec: exec,
	}
}

// Inspect collects readiness information for both VM bases and Docker runner containers.
func (ins *ImageInspector) Inspect(ctx context.Context) ImagesStatusResponse {
	vmImages := ins.inspectVMs(ctx)
	containerImages := ins.inspectContainers(ctx)

	allReady := true
	for _, img := range vmImages {
		if img.Status != string(StatusReady) {
			allReady = false
			break
		}
	}
	if allReady {
		for _, img := range containerImages {
			if img.Status != string(StatusReady) {
				allReady = false
				break
			}
		}
	}

	return ImagesStatusResponse{
		VMImages:        vmImages,
		ContainerImages: containerImages,
		AllReady:        allReady,
	}
}

func (ins *ImageInspector) inspectVMs(ctx context.Context) []InfrastructureImageStatus {
	arches := []string{"arm64", "amd64"}
	vms, err := ins.gb.ListVMs(ctx)
	vmSet := make(map[string]bool)
	if err == nil {
		for _, v := range vms {
			vmSet[v] = true
		}
	}

	results := make([]InfrastructureImageStatus, 0, len(arches))
	for _, arch := range arches {
		name := ins.gb.BaseImageName(arch)
		exists := vmSet[name]
		isStale := false
		status := "missing"
		version := ""

		if exists {
			isStale = ins.gb.IsStale(arch)
			if isStale {
				status = string(StatusStale)
			} else {
				status = string(StatusReady)
			}
			if data, err := os.ReadFile(ins.gb.StampPath(arch)); err == nil {
				version = strings.TrimSpace(string(data))
			}
		}

		results = append(results, InfrastructureImageStatus{
			ID:      name,
			Name:    name,
			Kind:    "orbstack-vm",
			Arch:    arch,
			Exists:  exists,
			IsStale: isStale,
			Version: version,
			Status:  status,
		})
	}
	return results
}

func (ins *ImageInspector) inspectContainers(ctx context.Context) []InfrastructureImageStatus {
	arches := []string{"arm64", "amd64"}
	out, err := ins.exec.Run(ctx, "docker", "images", "--format", "{{.Repository}}:{{.Tag}}|{{.ID}}|{{.Size}}|{{.CreatedAt}}")
	found := make(map[string]struct {
		id        string
		sizeHuman string
		createdAt string
	})

	if err == nil {
		lines := strings.Split(string(out), "\n")
		for _, line := range lines {
			line = strings.TrimSpace(line)
			if line == "" {
				continue
			}
			parts := strings.Split(line, "|")
			if len(parts) >= 4 {
				repoTag := parts[0]
				found[repoTag] = struct {
					id        string
					sizeHuman string
					createdAt string
				}{
					id:        parts[1],
					sizeHuman: parts[2],
					createdAt: parts[3],
				}
			}
		}
	}

	results := make([]InfrastructureImageStatus, 0, len(arches))
	for _, arch := range arches {
		tag := "local-github-runner:" + arch
		data, exists := found[tag]
		status := "missing"
		if exists {
			status = string(StatusReady)
		}

		results = append(results, InfrastructureImageStatus{
			ID:        tag,
			Name:      tag,
			Kind:      "docker-container",
			Arch:      arch,
			Exists:    exists,
			IsStale:   false,
			SizeHuman: data.sizeHuman,
			CreatedAt: data.createdAt,
			Status:    status,
		})
	}
	return results
}
