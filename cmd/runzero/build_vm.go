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
)

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
		fmt.Fprintf(stderr, "Unknown architecture: %s\n", *archFlag)
		return 1
	}

	cfg := builder.Config{
		StateDir: ".runzero-state",
	}
	gb := builder.NewGoldenBuilder(cfg, nil)

	ctx, cancel := daemon.SignalContext(context.Background())
	defer cancel()

	for _, arch := range targetArches {
		fmt.Fprintf(stdout, "Building golden OrbStack VM base image for %s...\n", arch)
		built, err := gb.BuildBaseImage(ctx, arch)
		if err != nil {
			fmt.Fprintf(stderr, "Failed building base image for %s: %v\n", arch, err)
			return 1
		}
		if built {
			fmt.Fprintf(stdout, "Successfully built golden base image: %s\n", gb.BaseImageName(arch))
		} else {
			fmt.Fprintf(stdout, "Golden base image %s is already up to date.\n", gb.BaseImageName(arch))
		}
	}

	return 0
}
