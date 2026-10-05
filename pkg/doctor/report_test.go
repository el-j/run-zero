package doctor

import (
	"context"
	"net/http"
	"net/http/httptest"
	"strings"
	"testing"
)

func TestCheckProxyAndReport(t *testing.T) {
	srv := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		w.WriteHeader(http.StatusOK)
	}))
	defer srv.Close()

	resOk := CheckProxy("test-proxy", srv.URL, nil)
	if resOk.Status != StatusOK {
		t.Fatalf("expected ok, got: %+v", resOk)
	}

	resFail := CheckProxy("test-proxy", "http://127.0.0.1:54321/not-found", nil)
	if resFail.Status != StatusWarn {
		t.Fatalf("expected warn, got: %+v", resFail)
	}

	results := []CheckResult{
		{Name: "docker", Status: StatusOK, Detail: "ok"},
		{Name: "cache", Status: StatusWarn, Detail: "warn"},
		{Name: "gh", Status: StatusFail, Detail: "fail"},
		{Name: "proxy", Status: StatusSkip, Detail: "skip"},
		{Name: "unknown", Status: Status("other"), Detail: "other"},
	}
	report := FormatReport(results)
	if !strings.Contains(report, "Summary: 1 passed, 1 warnings, 1 failures") {
		t.Fatalf("unexpected report: %s", report)
	}
	if !HasFailures(results) {
		t.Fatalf("expected failures detected")
	}
	if HasFailures([]CheckResult{{Status: StatusOK}}) {
		t.Fatalf("expected no failures")
	}

	all := RunAll(context.Background(), Options{
		Exec: &mockExecutor{
			runFunc: func(ctx context.Context, name string, args ...string) ([]byte, error) {
				return []byte("ok"), nil
			},
		},
		CacheDir:     t.TempDir(),
		CacheEnabled: true,
		ProxyURL:     srv.URL,
	})
	if len(all) == 0 {
		t.Fatalf("expected RunAll results")
	}
}
