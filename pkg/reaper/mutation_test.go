package reaper

import (
	"context"
	"net/http"
	"net/http/httptest"
	"strings"
	"testing"
	"time"

	"github.com/el-j/run-zero/pkg/github"
	"github.com/el-j/run-zero/pkg/state"
)

func TestClassify_TimeoutsAreStrict(t *testing.T) {
	to := Timeouts{IdleSeconds: 600, UnregisteredSeconds: 180, BusySeconds: 7200}
	cases := []struct {
		name string
		age  float64
		reg  *Registration
		want Action
	}{
		{"unregistered at limit", 180, nil, ActionKeep},
		{"offline at limit", 180, &Registration{Status: "offline"}, ActionKeep},
		{"busy at limit", 7200, &Registration{Status: "online", Busy: true}, ActionKeep},
		{"idle at limit", 600, &Registration{Status: "online"}, ActionKeep},
		{"unregistered past limit", 181, nil, ActionReapUnregistered},
		{"offline past limit", 181, &Registration{Status: "offline"}, ActionReapUnregistered},
		{"busy past limit", 7201, &Registration{Status: "online", Busy: true}, ActionCheckStaleBusy},
		{"idle past limit", 601, &Registration{Status: "online"}, ActionReapIdle},
	}
	for _, c := range cases {
		if got := Classify(c.age, c.reg, true, to); got != c.want {
			t.Errorf("%s: got %s, want %s", c.name, got, c.want)
		}
	}
}

func TestDeleteReapedRegistrations(t *testing.T) {
	var deletes []string
	srv := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		if r.Method == http.MethodDelete {
			deletes = append(deletes, r.URL.Path)
		}
		w.WriteHeader(http.StatusNoContent)
	}))
	defer srv.Close()
	r := NewReaper(nil, github.NewClient("t", srv.URL, srv.Client()), Timeouts{})
	runners := []state.RunnerInfo{{ID: "a", Name: "runzero-a", TargetRepo: "o/r"}, {ID: "b", Name: "runzero-b", TargetRepo: "o/r"}}
	regs := map[string]Registration{"runzero-a": {ID: 7}, "runzero-b": {ID: 8}}

	r.deleteReapedRegistrations(context.Background(), runners, regs, nil)
	if len(deletes) != 0 {
		t.Fatalf("nothing reaped means nothing deleted, got %v", deletes)
	}
	r.deleteReapedRegistrations(context.Background(), runners, regs, []string{"a"})
	if len(deletes) != 1 || !strings.HasSuffix(deletes[0], "/runners/7") {
		t.Fatalf("expected only runner 7 deleted, got %v", deletes)
	}
}

func TestRunnerAge_TrustsPastCreationTimesOnly(t *testing.T) {
	r := NewReaper(nil, nil, Timeouts{})
	now := time.Unix(1_000_000, 0)
	at := func(t time.Time) *string { s := t.UTC().Format(time.RFC3339); return &s }

	if age := r.runnerAge(state.RunnerInfo{ID: "now", CreatedAt: at(now)}, float64(now.Unix())); age != 0 {
		t.Fatalf("created now: age %v", age)
	}
	if _, tracked := r.firstSeen["now"]; tracked {
		t.Fatal("a runner with a usable creation time must not be tracked by first sight")
	}
	if age := r.runnerAge(state.RunnerInfo{ID: "past", CreatedAt: at(now.Add(-time.Minute))}, float64(now.Unix())); age != 60 {
		t.Fatalf("created a minute ago: age %v", age)
	}
	if age := r.runnerAge(state.RunnerInfo{ID: "future", CreatedAt: at(now.Add(time.Minute))}, float64(now.Unix())); age != 0 {
		t.Fatalf("future creation time: age %v", age)
	}
	if _, tracked := r.firstSeen["future"]; !tracked {
		t.Fatal("a future creation time must fall back to first sight")
	}
}

func TestRunnerKey(t *testing.T) {
	if runnerKey(state.RunnerInfo{ID: "id", Name: "n"}) != "id" || runnerKey(state.RunnerInfo{Name: "n"}) != "n" {
		t.Fatal("runnerKey must prefer the ID and fall back to the name")
	}
}
