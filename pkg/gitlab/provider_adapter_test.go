package gitlab

import (
	"context"
	"fmt"
	"net/http"
	"net/http/httptest"
	"testing"

	"github.com/el-j/run-zero/pkg/provider"
)

func TestProviderAdapterIdentityAndDefaults(t *testing.T) {
	ts := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) { _, _ = fmt.Fprint(w, `[]`) }))
	defer ts.Close()
	client := NewClient("", ts.URL, ts.Client())
	a := NewProviderAdapter("", "", client, "", nil)
	if a.ID() != "gitlab" || a.Name() != "GitLab ("+ts.Listener.Addr().String()+")" || a.Type() != provider.TypeGitLab || a.BaseURL() != ts.URL+"/api/v4" {
		t.Fatalf("adapter identity: %s %s %s %s", a.ID(), a.Name(), a.Type(), a.BaseURL())
	}
	if explicit := NewProviderAdapter("custom", "My GitLab", client, "", nil); explicit.ID() != "custom" || explicit.Name() != "My GitLab" {
		t.Fatal("explicit identity ignored")
	}
	invalid := NewProviderAdapter("", "", NewClient("", "://invalid", nil), "", nil)
	if invalid.Name() != "GitLab" {
		t.Fatalf("invalid URL fallback name %q", invalid.Name())
	}
}

func TestProviderAdapterGroupFallbackJobsTokensAndDelete(t *testing.T) {
	calls := map[string]int{}
	var deleted string
	ts := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		calls[r.URL.Path]++
		w.Header().Set("Content-Type", "application/json")
		switch r.URL.EscapedPath() {
		case "/api/v4/groups/group%2Fname/runners":
			w.WriteHeader(http.StatusBadGateway)
		case "/api/v4/runners":
			_, _ = fmt.Fprint(w, `[{"id":1,"description":"runzero-local","active":true,"status":"online"}]`)
		case "/api/v4/projects/project%2Fone/jobs":
			_, _ = fmt.Fprint(w, `[{"id":2,"name":"build","stage":"test","ref":"main","pipeline":{"id":3},"tag_list":["linux"]}]`)
		case "/api/v4/projects/bad/jobs":
			w.WriteHeader(http.StatusBadGateway)
		default:
			if r.Method == http.MethodDelete {
				deleted = r.URL.Path
				w.WriteHeader(http.StatusNoContent)
				return
			}
			http.NotFound(w, r)
		}
	}))
	defer ts.Close()
	client := NewClient("  gl-token  ", ts.URL, ts.Client())
	a := NewProviderAdapter("id", "name", client, "group/name", []string{"project/one", "bad"})
	runners, err := a.FetchRemoteRunners(context.Background())
	if err != nil || len(runners) != 1 || runners[0].ID != "gl-1" {
		t.Fatalf("runners=%+v err=%v", runners, err)
	}
	jobs, err := a.FetchQueuedJobs(context.Background())
	if err != nil || len(jobs) != 1 || jobs[0].ID != 2 || jobs[0].Repo != "project/one" {
		t.Fatalf("jobs=%+v err=%v", jobs, err)
	}
	token, expiry, err := a.AcquireRegistrationToken(context.Background(), "ignored")
	if err != nil || token != "gl-token" || expiry.IsZero() {
		t.Fatalf("token=%q expiry=%v err=%v", token, expiry, err)
	}
	if err := a.DeregisterRunner(context.Background(), "17"); err != nil || deleted != "/api/v4/runners/17" {
		t.Fatalf("delete=%q err=%v", deleted, err)
	}
	if calls["/api/v4/runners"] != 1 {
		t.Fatalf("group fallback not executed: %v", calls)
	}
}

func TestProviderAdapterGroupEmptyAndErrors(t *testing.T) {
	step := 0
	ts := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "application/json")
		if r.URL.EscapedPath() == "/api/v4/groups/g/runners" {
			w.WriteHeader(http.StatusBadGateway)
			return
		}
		if r.URL.EscapedPath() == "/api/v4/runners" {
			if step == 0 {
				_, _ = fmt.Fprint(w, `[]`)
			} else {
				w.WriteHeader(http.StatusBadGateway)
			}
			return
		}
		if r.Method == http.MethodDelete {
			w.WriteHeader(http.StatusBadGateway)
			return
		}
		http.NotFound(w, r)
	}))
	defer ts.Close()
	a := NewProviderAdapter("", "", NewClient("", ts.URL, ts.Client()), "g", nil)
	if got, err := a.FetchRemoteRunners(context.Background()); err != nil || len(got) != 0 {
		t.Fatalf("fallback list: %v %v", got, err)
	}
	step++
	if _, err := a.FetchRemoteRunners(context.Background()); err == nil {
		t.Fatal("expected fallback API error")
	}
	if _, _, err := a.AcquireRegistrationToken(context.Background(), ""); err == nil {
		t.Fatal("expected missing token error")
	}
	if err := a.DeregisterRunner(context.Background(), "id"); err == nil {
		t.Fatal("expected delete error")
	}
}

func TestProviderAdapterGroupSuccess(t *testing.T) {
	ts := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "application/json")
		_, _ = fmt.Fprint(w, `[{"id":4,"name":"group runner","active":true,"status":"online"}]`)
	}))
	defer ts.Close()
	a := NewProviderAdapter("", "", NewClient("", ts.URL, ts.Client()), "group", nil)
	got, err := a.FetchRemoteRunners(context.Background())
	if err != nil || len(got) != 1 || got[0].ID != "gl-4" {
		t.Fatalf("group runners=%+v err=%v", got, err)
	}
}
