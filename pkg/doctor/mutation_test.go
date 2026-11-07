package doctor

import (
	"context"
	"net/http"
	"net/http/httptest"
	"strings"
	"testing"
	"time"

	"github.com/el-j/run-zero/pkg/github"
)

func githubServer(t *testing.T, withQuota bool) *github.Client {
	t.Helper()
	srv := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		if withQuota {
			w.Header().Set("X-RateLimit-Remaining", "4990")
			w.Header().Set("X-RateLimit-Limit", "5000")
		}
		_, _ = w.Write([]byte(`{"login":"el-j"}`))
	}))
	t.Cleanup(srv.Close)
	return github.NewClient("t", srv.URL, srv.Client())
}

func TestCheckGitHub_ReportsQuotaOnlyWhenKnown(t *testing.T) {
	if r := CheckGitHub(context.Background(), githubServer(t, true)); r.Detail != "authenticated as @el-j (4990/5000 API calls remaining)" {
		t.Fatalf("with quota: %q", r.Detail)
	}
	if r := CheckGitHub(context.Background(), githubServer(t, false)); r.Detail != "authenticated as @el-j" {
		t.Fatalf("without quota: %q", r.Detail)
	}
}

func TestRunAll_ChecksGitHubOnlyWithAClient(t *testing.T) {
	exec := &mockExecutor{runFunc: func(context.Context, string, ...string) ([]byte, error) { return []byte("ok"), nil }}
	has := func(results []CheckResult) bool {
		for _, r := range results {
			if r.Name == "github API" {
				return true
			}
		}
		return false
	}
	if !has(RunAll(context.Background(), Options{Exec: exec, GHClient: githubServer(t, true)})) {
		t.Error("a configured client must be checked")
	}
	if has(RunAll(context.Background(), Options{Exec: exec})) {
		t.Error("no client means no GitHub check")
	}
}

func TestCheckProxy_DefaultClientTimesOut(t *testing.T) {
	block := make(chan struct{})
	srv := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) { <-block }))
	defer func() { close(block); srv.Close() }()

	start := time.Now()
	r := CheckProxy("squid", srv.URL, nil)
	if r.Status != StatusWarn || !strings.Contains(r.Detail, "unreachable") || time.Since(start) > 5*time.Second {
		t.Fatalf("a hanging proxy must time out after about 1s: %+v after %s", r, time.Since(start))
	}
}

func TestRunAll_ChecksProxyOnlyWhenConfigured(t *testing.T) {
	exec := &mockExecutor{runFunc: func(context.Context, string, ...string) ([]byte, error) { return []byte("ok"), nil }}
	srv := httptest.NewServer(http.HandlerFunc(func(http.ResponseWriter, *http.Request) {}))
	defer srv.Close()
	hasProxy := func(results []CheckResult) bool {
		for _, r := range results {
			if r.Name == "proxy squid" {
				return true
			}
		}
		return false
	}
	if !hasProxy(RunAll(context.Background(), Options{Exec: exec, ProxyURL: srv.URL})) {
		t.Error("a configured proxy must be checked")
	}
	if hasProxy(RunAll(context.Background(), Options{Exec: exec})) {
		t.Error("no proxy URL means no proxy check")
	}
}
