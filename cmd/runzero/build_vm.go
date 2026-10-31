package main

import (
	"context"
	"flag"
	"fmt"
	"io"
	"os"
	"strings"

	"github.com/el-j/run-zero/pkg/builder"
	"github.com/el-j/run-zero/pkg/daemon"
	"github.com/el-j/run-zero/pkg/driver"
)

// goldenExec overrides the command executor used for golden builds (nil = real OS).
var goldenExec driver.CmdExecutor

func runBuildVMBase(args []string, stdout, stderr io.Writer) int {
	fs := flag.NewFlagSet("runzero build-vm-base", flag.ContinueOnError)
	fs.SetOutput(stderr)

	defaultArch := os.Getenv("RUNNER_ARCH")
	if defaultArch == "" {
		defaultArch = "both"
	}

	archFlag := fs.String("arch", defaultArch, "Target runner architecture (arm64, amd64, or both)")
	if err := fs.Parse(args); err != nil {
		return 1
	}

	var targetArches []string
	switch strings.ToLower(*archFlag) {
	case "both", "":
		targetArches = []string{"arm64", "amd64"}
	case "arm64", "aarch64":
		targetArches = []string{"arm64"}
	case "amd64", "x86_64":
		targetArches = []string{"amd64"}
	default:
		_, _ = fmt.Fprintf(stderr, "Unknown architecture: %s\n", *archFlag)
		return 1
	}

	// The shared toolchain script (Node/nvm, pnpm, .NET, Chrome, Playwright deps) is
	// what makes the golden VM equivalent to the runner container image. Without it
	// the VM only has Docker and the runner binary, so fail loudly instead of
	// silently building a bare image.
	provisionScript := os.Getenv("PROVISION_SCRIPT")
	if provisionScript == "" {
		provisionScript = "docker/provision-toolchain.sh"
	}
	if _, err := os.Stat(provisionScript); err != nil {
		_, _ = fmt.Fprintf(stderr, "Cannot read toolchain provisioning script %q (run from the repo root or set PROVISION_SCRIPT): %v\n", provisionScript, err)
		return 1
	}

	cfg := builder.Config{
		StateDir:            ".runzero-state",
		ProvisionScriptPath: provisionScript,
	}
	gb := builder.NewGoldenBuilder(cfg, goldenExec)

	ctx, cancel := daemon.SignalContext(context.Background())
	defer cancel()

	for _, arch := range targetArches {
		_, _ = fmt.Fprintf(stdout, "Building golden OrbStack VM base image for %s...\n", arch)
		built, err := gb.BuildBaseImage(ctx, arch)
		if err != nil {
			_, _ = fmt.Fprintf(stderr, "Failed building base image for %s: %v\n", arch, err)
			return 1
		}
		if built {
			_, _ = fmt.Fprintf(stdout, "Successfully built golden base image: %s\n", gb.BaseImageName(arch))
		} else {
			_, _ = fmt.Fprintf(stdout, "Golden base image %s is already up to date.\n", gb.BaseImageName(arch))
		}
	}

	if stopped, err := gb.EnsureBaseImagesStopped(ctx); err == nil && len(stopped) > 0 {
		_, _ = fmt.Fprintf(stdout, "Verified base VM templates are stopped: %v\n", stopped)
	}

	return 0
}
