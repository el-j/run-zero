package main

import (
	"context"
	"flag"
	"fmt"
	"io"
	"os"
	"path/filepath"
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

	// Persist spawn metadata so VMs keep their repo mapping across bridge restarts.
	storePath := ""
	if home, err := os.UserHomeDir(); err == nil {
		storePath = filepath.Join(home, ".local-github-runner", "state", "bridge-instances.json")
	}
	store := driver.NewInstanceStore(storePath)
	if err := store.Load(); err != nil {
		_, _ = fmt.Fprintf(stderr, "[Bridge] could not load %s: %v\n", storePath, err)
	}
	vm := bridgeVMSettings(dotEnv)
	wslDir := vm.WSLRunnerDir
	if wslDir == "" && storePath != "" {
		wslDir = filepath.Join(filepath.Dir(storePath), "wsl")
	}
	drivers := map[string]driver.RunnerDriver{
		"orbstack":  driver.NewOrbStackDriver(nil, store, ""),
		"docker":    driver.NewDockerDriver(nil, store, "", ""),
		"multipass": driver.NewMultipassDriver(nil, store, vm.MultipassImage),
		"wsl2":      driver.NewWSLDriver(nil, store, vm.WSLDistroBase, vm.WSLBaseTarball, wslDir),
	}

	srv := bridge.NewServer(*port, *host, *token, Version, "", drivers)
	ctx, cancel := daemon.SignalContext(context.Background())
	defer cancel()

	_, _ = fmt.Fprintf(stdout, "Starting Host VM Bridge on http://%s:%d (runzero v%s)...\n", *host, *port, Version)
	if err := srv.Run(ctx); err != nil {
		_, _ = fmt.Fprintf(stderr, "[Bridge Error] %v\n", err)
		return 1
	}
	return 0
}

// bridgeVMSettings reads the Multipass/WSL2 settings from the environment and
// the .env file; invalid configuration falls back to the drivers' defaults.
func bridgeVMSettings(dotEnv config.EnvLookup) *config.Config {
	env := config.EnvLookup(config.OSEnv{})
	if dotEnv != nil {
		env = config.CompositeEnv{Primary: config.OSEnv{}, Secondary: dotEnv}
	}
	cfg, err := config.LoadConfig(env)
	if err != nil {
		return &config.Config{}
	}
	return cfg
}
