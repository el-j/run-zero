package doctor

import (
	"context"
	"errors"
	"net/http"
	"net/http/httptest"
	"os"
	"path/filepath"
	"strings"
	"testing"

	"github.com/el-j/run-zero/pkg/github"
)

type mockExecutor struct {
	runFunc func(ctx context.Context, name string, args ...string) ([]byte, error)
}

func (m *mockExecutor) Run(ctx context.Context, name string, args ...string) ([]byte, error) {
	if m.runFunc != nil {
		return m.runFunc(ctx, name, args...)
	}
	return nil, nil
}

func (m *mockExecutor) LookPath(file string) (string, error) {
	return file, nil
}

func TestCheckDocker(t *testing.T) {
	ctx := context.Background()
	mock := &mockExecutor{
		runFunc: func(ctx context.Context, name string, args ...string) ([]byte, error) {
			return []byte("27.0.3\n"), nil
		},
	}
	res := CheckDocker(ctx, mock)
	if res.Status != StatusOK || !strings.Contains(res.Detail, "27.0.3") {
		t.Fatalf("expected ok with version, got: %+v", res)
	}

	mockErr := &mockExecutor{
		runFunc: func(ctx context.Context, name string, args ...string) ([]byte, error) {
			return nil, errors.New("command not found")
		},
	}
	resErr := CheckDocker(ctx, mockErr)
	if resErr.Status != StatusFail {
		t.Fatalf("expected fail, got: %+v", resErr)
	}
}

func TestCheckOrbStack(t *testing.T) {
	ctx := context.Background()
	mock := &mockExecutor{
		runFunc: func(ctx context.Context, name string, args ...string) ([]byte, error) {
			return []byte("OrbStack is running\n"), nil
		},
	}
	res := CheckOrbStack(ctx, mock)
	if res.Status != StatusOK {
		t.Fatalf("expected ok, got: %+v", res)
	}

	mockErr := &mockExecutor{
		runFunc: func(ctx context.Context, name string, args ...string) ([]byte, error) {
			return nil, errors.New("orbctl not found")
		},
	}
	resErr := CheckOrbStack(ctx, mockErr)
	if resErr.Status != StatusWarn {
		t.Fatalf("expected warn, got: %+v", resErr)
	}
}

func TestCheckGitHub(t *testing.T) {
	ctx := context.Background()
	if res := CheckGitHub(ctx, nil); res.Status != StatusWarn {
		t.Fatalf("expected warn for nil client, got: %+v", res)
	}

	srv := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("x-ratelimit-limit", "5000")
		w.Header().Set("x-ratelimit-remaining", "4990")
		w.WriteHeader(http.StatusOK)
		_, _ = w.Write([]byte(`{"login":"octocat"}`))
	}))
	defer srv.Close()

	client := github.NewClient("fake-token", srv.URL, srv.Client())
	res := CheckGitHub(ctx, client)
	if res.Status != StatusOK || !strings.Contains(res.Detail, "@octocat") {
		t.Fatalf("expected ok for octocat, got: %+v", res)
	}

	failSrv := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		w.WriteHeader(http.StatusUnauthorized)
		_, _ = w.Write([]byte(`{"message":"Bad credentials"}`))
	}))
	defer failSrv.Close()

	failClient := github.NewClient("fake-token", failSrv.URL, failSrv.Client())
	resFail := CheckGitHub(ctx, failClient)
	if resFail.Status != StatusFail {
		t.Fatalf("expected fail, got: %+v", resFail)
	}
}

func TestCheckHostCache(t *testing.T) {
	resDis := CheckHostCache("/tmp", false)
	if len(resDis) != 1 || resDis[0].Status != StatusSkip {
		t.Fatalf("expected skip, got: %+v", resDis)
	}

	resEmp := CheckHostCache("", true)
	if len(resEmp) != 1 || resEmp[0].Status != StatusWarn {
		t.Fatalf("expected warn, got: %+v", resEmp)
	}

	resNon := CheckHostCache("/non/existent/dir/12345", true)
	if len(resNon) != 1 || resNon[0].Status != StatusFail {
		t.Fatalf("expected fail, got: %+v", resNon)
	}

	tmp := t.TempDir()
	_ = os.MkdirAll(filepath.Join(tmp, "toolcache"), 0755)
	_ = os.WriteFile(filepath.Join(tmp, "toolcache", "node.tar"), []byte("data"), 0644)
	resVal := CheckHostCache(tmp, true)
	if len(resVal) == 0 || resVal[0].Status != StatusOK {
		t.Fatalf("expected ok, got: %+v", resVal)
	}
}
