package bridge

import (
	"bytes"
	"context"
	"errors"
	"log"
	"os"
	"strings"
	"testing"

	"github.com/el-j/run-zero/pkg/builder"
	"github.com/el-j/run-zero/pkg/driver"
)

// stopRecorder records which runner ID the bridge asked a driver to stop.
type stopRecorder struct {
	mockDriver
	stoppedID string
}

func (s *stopRecorder) StopRunner(_ context.Context, id string) error {
	s.stoppedID = id
	return nil
}

func TestStop_RunnerIDTakesPrecedenceOverID(t *testing.T) {
	rec := &stopRecorder{mockDriver: mockDriver{backend: "orbstack"}}
	s := newTestServer(t, "tok", map[string]driver.RunnerDriver{"orbstack": rec})
	do(s, "POST", "/api/drivers/orbstack/stop", `{"runner_id":"abc","id":"other"}`, "tok")
	if rec.stoppedID != "abc" {
		t.Fatalf("stopped %q", rec.stoppedID)
	}
	do(s, "POST", "/api/drivers/orbstack/stop", `{"id":"fallback"}`, "tok")
	if rec.stoppedID != "fallback" {
		t.Fatalf("stopped %q", rec.stoppedID)
	}
}

func TestIsSafeRunnerName_CharacterClassLimits(t *testing.T) {
	for _, ok := range []string{"a", "z", "A", "Z", "0", "9", "-", "_", ".", ":"} {
		if !isSafeRunnerName(ok) {
			t.Errorf("%q must be safe", ok)
		}
	}
	for _, bad := range []string{"`", "{", "@", "[", "/", ";", " ", "$"} {
		if isSafeRunnerName(bad) {
			t.Errorf("%q must be unsafe", bad)
		}
	}
}

func TestNewServer_UsesStateDirFromEnvironment(t *testing.T) {
	dir := t.TempDir()
	t.Setenv("RUNZERO_STATE_DIR", dir)
	s := NewServer(0, "", "", "v", "sha", nil)
	if !strings.HasPrefix(s.gb.StampPath("amd64"), dir) {
		t.Fatalf("stamp path %q not under %q", s.gb.StampPath("amd64"), dir)
	}
	t.Setenv("RUNZERO_STATE_DIR", "")
	if s := NewServer(0, "", "", "v", "sha", nil); !strings.HasPrefix(s.gb.StampPath("amd64"), ".runzero-state") {
		t.Fatalf("default stamp path %q", s.gb.StampPath("amd64"))
	}
}

func TestStopGoldenTemplates_LogsOnlyWhatItStopped(t *testing.T) {
	var buf bytes.Buffer
	log.SetOutput(&buf)
	defer log.SetOutput(os.Stderr)
	run := func(listing string, err error) string {
		buf.Reset()
		s := newTestServer(t, "", nil)
		s.gb = builder.NewGoldenBuilder(builder.Config{StateDir: t.TempDir()}, fakeExec{run: func(_ context.Context, name string, args ...string) ([]byte, error) {
			if len(args) > 0 && args[0] == "list" {
				return []byte(listing), err
			}
			return nil, nil
		}})
		s.stopGoldenTemplates(context.Background())
		return buf.String()
	}
	if out := run(`[{"name":"runzero-vm-base-amd64","state":"running"}]`, nil); !strings.Contains(out, "runzero-vm-base-amd64") {
		t.Fatalf("expected the stopped template in the log, got %q", out)
	}
	if out := run(`[]`, nil); out != "" {
		t.Fatalf("nothing stopped means no log, got %q", out)
	}
	if out := run(`[{"name":"runzero-vm-base-amd64","state":"running"}]`, errors.New("orbctl missing")); out != "" {
		t.Fatalf("a listing error means no log, got %q", out)
	}
	s := newTestServer(t, "", nil)
	s.gb = nil
	s.stopGoldenTemplates(context.Background())
}
