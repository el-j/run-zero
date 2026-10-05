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

var Version = "1.0.0-alpha.1"

func run(args []string, stdout, stderr io.Writer) int {
	fs := flag.NewFlagSet("runzero", flag.ContinueOnError)
	fs.SetOutput(stderr)

	envFile := fs.String("config", ".env", "Path to .env configuration file")
	showVersion := fs.Bool("version", false, "Print RunZero Go engine version and exit")
	distDir := fs.String("dist", "web/dist", "Path to Vite compiled UI distribution directory")
	staticDir := fs.String("static", "src/dashboard/static", "Path to static asset fallback directory")

	if err := fs.Parse(args); err != nil {
		return 1
	}

	if *showVersion {
		fmt.Fprintf(stdout, "runzero v%s (cloud-native go engine)\n", Version)
		return 0
	}

	dotEnv, err := config.LoadDotEnvFile(*envFile)
	if err != nil {
		fmt.Fprintf(stderr, "[Error] Failed reading %s: %v\n", *envFile, err)
		return 1
	}

	env := config.CompositeEnv{
		Primary:   config.OSEnv{},
		Secondary: dotEnv,
	}

	cfg, err := config.LoadConfig(env)
	if err != nil {
		fmt.Fprintf(stderr, "[Config Error] %v\n", err)
		return 1
	}

	d := daemon.NewDaemon(cfg, Version, *distDir, *staticDir)

	ctx, cancel := daemon.SignalContext(context.Background())
	defer cancel()

	if err := d.Run(ctx); err != nil {
		fmt.Fprintf(stderr, "[Daemon Error] %v\n", err)
		return 1
	}
	return 0
}

func main() {
	os.Exit(run(os.Args[1:], os.Stdout, os.Stderr))
}
