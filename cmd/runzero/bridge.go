package main

import (
	"context"
	"flag"
	"fmt"
	"io"
	"os"
	"strconv"

	"github.com/el-j/run-zero/pkg/bridge"
	"github.com/el-j/run-zero/pkg/config"
	"github.com/el-j/run-zero/pkg/daemon"
	"github.com/el-j/run-zero/pkg/driver"
)

func runBridge(args []string, stdout, stderr io.Writer) int {
	fs := flag.NewFlagSet("runzero bridge", flag.ContinueOnError)
	fs.SetOutput(stderr)

	defaultPort := 49504
	if pStr := os.Getenv("HOST_VM_BRIDGE_PORT"); pStr != "" {
		if p, err := strconv.Atoi(pStr); err == nil && p > 0 {
			defaultPort = p
		}
	}
	defaultHost := "127.0.0.1"
	if hStr := os.Getenv("HOST_VM_BRIDGE_HOST"); hStr != "" {
		defaultHost = hStr
	}

	port := fs.Int("port", defaultPort, "Host VM Bridge TCP listening port")
	host := fs.String("host", defaultHost, "Host VM Bridge listening address")
	token := fs.String("token", os.Getenv("RUNZERO_BRIDGE_TOKEN"), "Bearer authentication token for driver actions")
	envFile := fs.String("config", ".env", "Path to .env configuration file")

	if err := fs.Parse(args); err != nil {
		return 1
	}

	dotEnv, _ := config.LoadDotEnvFile(*envFile)
	if dotEnv != nil {
		if t, ok := dotEnv.Lookup("RUNZERO_BRIDGE_TOKEN"); ok && *token == "" {
			*token = t
		}
	}

	store := driver.NewInstanceStore("")
	orbDriver := driver.NewOrbStackDriver(nil, store, "")
	dockerDriver := driver.NewDockerDriver(nil, store, "", "")

	drivers := map[string]driver.RunnerDriver{
		"orbstack": orbDriver,
		"docker":   dockerDriver,
	}

	srv := bridge.NewServer(*port, *host, *token, Version, "", drivers)
	ctx, cancel := daemon.SignalContext(context.Background())
	defer cancel()

	fmt.Fprintf(stdout, "Starting Host VM Bridge on http://%s:%d (runzero v%s)...\n", *host, *port, Version)
	if err := srv.Run(ctx); err != nil {
		fmt.Fprintf(stderr, "[Bridge Error] %v\n", err)
		return 1
	}
	return 0
}
