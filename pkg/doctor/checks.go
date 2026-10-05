package doctor

import (
	"context"
	"fmt"
	"net/http"
	"os"
	"strings"
	"time"

	"github.com/el-j/run-zero/pkg/cache"
	"github.com/el-j/run-zero/pkg/driver"
	"github.com/el-j/run-zero/pkg/github"
)

// CheckDocker tests Docker CLI presence and daemon connectivity.
func CheckDocker(ctx context.Context, exec driver.CmdExecutor) CheckResult {
	if exec == nil {
		exec = &driver.OSExecutor{}
	}
	out, err := exec.Run(ctx, "docker", "info", "--format", "{{.ServerVersion}}")
	if err != nil {
		return CheckResult{Name: "docker daemon", Status: StatusFail, Detail: "daemon unreachable or docker CLI not found"}
	}
	ver := strings.TrimSpace(string(out))
	return CheckResult{Name: "docker daemon", Status: StatusOK, Detail: fmt.Sprintf("running (version %s)", ver)}
}

// CheckOrbStack tests OrbStack CLI presence and machine status.
func CheckOrbStack(ctx context.Context, exec driver.CmdExecutor) CheckResult {
	if exec == nil {
		exec = &driver.OSExecutor{}
	}
	out, err := exec.Run(ctx, "orbctl", "status")
	if err != nil {
		return CheckResult{Name: "orbctl CLI", Status: StatusWarn, Detail: "orbctl not installed or OrbStack not running"}
	}
	status := strings.TrimSpace(string(out))
	return CheckResult{Name: "orbctl CLI", Status: StatusOK, Detail: status}
}

// CheckGitHub verifies token authentication and rate limit availability.
func CheckGitHub(ctx context.Context, client *github.Client) CheckResult {
	if client == nil {
		return CheckResult{Name: "github API", Status: StatusWarn, Detail: "client not configured"}
	}
	var userResp struct {
		Login string `json:"login"`
	}
	_, err := client.DoRequest(ctx, http.MethodGet, "/user", nil, &userResp)
	if err != nil {
		return CheckResult{Name: "github API", Status: StatusFail, Detail: fmt.Sprintf("authentication failed: %v", err)}
	}
	rl := client.RateLimit()
	detail := fmt.Sprintf("authenticated as @%s", userResp.Login)
	if rl.Limit > 0 {
		detail += fmt.Sprintf(" (%d/%d API calls remaining)", rl.Remaining, rl.Limit)
	}
	return CheckResult{Name: "github API", Status: StatusOK, Detail: detail}
}

// CheckHostCache inspects host cache directories and calculates disk usage.
func CheckHostCache(dir string, enabled bool) []CheckResult {
	if !enabled {
		return []CheckResult{{Name: "host cache", Status: StatusSkip, Detail: "CACHE_ENABLED=false"}}
	}
	if strings.TrimSpace(dir) == "" {
		return []CheckResult{{Name: "host cache", Status: StatusWarn, Detail: "HOST_CACHE_DIR not configured"}}
	}
	if info, err := os.Stat(dir); err != nil || !info.IsDir() {
		return []CheckResult{{Name: "host cache", Status: StatusFail, Detail: fmt.Sprintf("directory %s does not exist", dir)}}
	}

	stats := cache.CalculateStats(dir)
	results := []CheckResult{
		{Name: "host cache", Status: StatusOK, Detail: fmt.Sprintf("%s (%s)", dir, stats.TotalHuman)},
	}
	for _, c := range stats.Categories {
		results = append(results, CheckResult{
			Name:   fmt.Sprintf("cache category %s", c.Category),
			Status: StatusOK,
			Detail: c.HumanReadable,
		})
	}
	return results
}

// CheckProxy tests connectivity of an HTTP proxy endpoint.
func CheckProxy(name, url string, client *http.Client) CheckResult {
	if client == nil {
		client = &http.Client{Timeout: 1 * time.Second}
	}
	resp, err := client.Get(url)
	if err != nil {
		return CheckResult{Name: "proxy " + name, Status: StatusWarn, Detail: fmt.Sprintf("unreachable at %s", url)}
	}
	_ = resp.Body.Close()
	return CheckResult{Name: "proxy " + name, Status: StatusOK, Detail: fmt.Sprintf("reachable at %s", url)}
}
