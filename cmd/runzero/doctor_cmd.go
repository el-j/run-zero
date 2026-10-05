package main

import (
	"context"
	"flag"
	"fmt"
	"io"
	"time"

	"github.com/el-j/run-zero/pkg/config"
	"github.com/el-j/run-zero/pkg/doctor"
	"github.com/el-j/run-zero/pkg/driver"
	"github.com/el-j/run-zero/pkg/github"
)

func runDoctor(args []string, stdout, stderr io.Writer) int {
	fs := flag.NewFlagSet("runzero doctor", flag.ContinueOnError)
	fs.SetOutput(stderr)

	envFile := fs.String("config", ".env", "Path to .env configuration file")
	timeout := fs.Duration("timeout", 10*time.Second, "Diagnostic timeout")

	if err := fs.Parse(args); err != nil {
		return 1
	}

	ctx, cancel := context.WithTimeout(context.Background(), *timeout)
	defer cancel()

	var cfg *config.Config
	if dotEnv, err := config.LoadDotEnvFile(*envFile); err == nil {
		env := config.CompositeEnv{Primary: config.OSEnv{}, Secondary: dotEnv}
		cfg, _ = config.LoadConfig(env)
	}

	opts := doctor.Options{
		Exec: &driver.OSExecutor{},
	}

	if cfg != nil {
		opts.CacheDir = cfg.HostCacheDir
		opts.CacheEnabled = cfg.CacheEnabled
		if cfg.AccessToken != "" {
			opts.GHClient = github.NewClient(cfg.AccessToken, "https://api.github.com", nil)
		}
		if cfg.ProxiesEnabled {
			opts.ProxyURL = "http://127.0.0.1:3128"
		}
	}

	results := doctor.RunAll(ctx, opts)
	report := doctor.FormatReport(results)
	fmt.Fprint(stdout, report)

	if doctor.HasFailures(results) {
		return 1
	}
	return 0
}
