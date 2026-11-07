package main

import (
	"context"
	"flag"
	"fmt"
	"io"
	"os"

	"github.com/el-j/run-zero/pkg/config"
	"github.com/el-j/run-zero/pkg/daemon"
)

// Version is the RunZero engine version reported by -version and the bridge.
var Version = "1.0.0-alpha.1"

func run(args []string, stdout, stderr io.Writer) int {
	if len(args) > 0 {
		switch args[0] {
		case "doctor", "-doctor", "--doctor":
			return runDoctor(args[1:], stdout, stderr)
		case "bridge", "-bridge", "--bridge":
			return runBridge(args[1:], stdout, stderr)
		case "build-vm-base", "-build-vm-base", "--build-vm-base":
			return runBuildVMBase(args[1:], stdout, stderr)
		case "parity", "-parity", "--parity":
			return runParity(stdout)
		}
	}

	fs := flag.NewFlagSet("runzero", flag.ContinueOnError)
	fs.SetOutput(stderr)

	envFile := fs.String("config", ".env", "Path to .env configuration file")
	showVersion := fs.Bool("version", false, "Print RunZero Go engine version and exit")
	distDir := fs.String("dist", "web/dist", "Path to Vite compiled UI distribution directory")
	staticDir := fs.String("static", "web/dist", "Path to static asset fallback directory")

	if err := fs.Parse(args); err != nil {
		return 1
	}

	if *showVersion {
		_, _ = fmt.Fprintf(stdout, "runzero v%s (cloud-native go engine)\n", Version)
		return 0
	}

	dotEnv, err := config.LoadDotEnvFile(*envFile)
	if err != nil {
		_, _ = fmt.Fprintf(stderr, "[Error] Failed reading %s: %v\n", *envFile, err)
		return 1
	}

	env := config.CompositeEnv{
		Primary:   config.OSEnv{},
		Secondary: dotEnv,
	}

	cfg, err := config.LoadConfig(env)
	if err != nil {
		_, _ = fmt.Fprintf(stderr, "[Config Error] %v\n", err)
		return 1
	}

	d := daemon.NewDaemon(cfg, Version, *distDir, *staticDir)

	ctx, cancel := daemon.SignalContext(context.Background())
	defer cancel()

	if err := d.Run(ctx); err != nil {
		_, _ = fmt.Fprintf(stderr, "[Daemon Error] %v\n", err)
		return 1
	}
	return 0
}

// exit is os.Exit, replaceable in tests.
var exit = os.Exit

func main() {
	exit(run(os.Args[1:], os.Stdout, os.Stderr))
}
