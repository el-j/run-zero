package github

import (
	"context"
	"fmt"
	"net/http"
	"net/http/httptest"
	"reflect"
	"testing"

	"github.com/el-j/run-zero/pkg/provider"
)

func TestProviderAdapterIdentityAndOrgRunners(t *testing.T) {
	ts := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "application/json")
		_, _ = fmt.Fprint(w, `{"runners":[{"id":1,"name":"hosted runner","status":"online","labels":[{"name":"arm64"}]}]}`)
	}))
	defer ts.Close()
	client := NewClient("", ts.URL, ts.Client())
	a := NewProviderAdapter(client, "owner", "org", nil)
	if a.ID() != "github" || a.Name() != "GitHub (org)" || a.Type() != provider.TypeGitHub || a.BaseURL() != ts.URL {
		t.Fatalf("adapter identity mismatch")
	}
	runners, err := a.FetchRemoteRunners(context.Background())
	if err != nil || len(runners) != 1 || runners[0].ID != "gh-1" {
		t.Fatalf("runners=%+v err=%v", runners, err)
	}
	if NewProviderAdapter(client, "owner", "", nil).Name() != "GitHub (@owner)" || NewProviderAdapter(client, "", "", nil).Name() != "GitHub" {
		t.Fatal("name fallback mismatch")
	}
}

func TestProviderAdapterRepositoryFallbackAndFailures(t *testing.T) {
	calls := map[string]int{}
	ts := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		calls[r.URL.Path]++
		w.Header().Set("Content-Type", "application/json")
		switch r.URL.Path {
		case "/orgs/o/actions/runners":
			w.WriteHeader(http.StatusBadGateway)
		case "/repos/a/actions/runners":
			_, _ = fmt.Fprint(w, `{"runners":[{"id":1,"name":"a"},{"id":2,"name":"b"}]}`)
		case "/repos/b/actions/runners":
			_, _ = fmt.Fprint(w, `{"runners":[{"id":2,"name":"duplicate"},{"id":3,"name":"c"}]}`)
		case "/repos/c/actions/runners":
			w.WriteHeader(http.StatusBadGateway)
		case "/repos/a/actions/runs":
			_, _ = fmt.Fprint(w, `{"workflow_runs":[]}`)
		case "/repos/b/actions/runs":
			w.WriteHeader(http.StatusBadGateway)
		default:
			http.NotFound(w, r)
		}
	}))
	defer ts.Close()
	a := NewProviderAdapter(NewClient("", ts.URL, ts.Client()), "", "o", []string{"a", "b", "c"})
	runners, err := a.FetchRemoteRunners(context.Background())
	if err != nil || len(runners) != 3 || runners[1].Name != "b" {
		t.Fatalf("runners=%+v err=%v", runners, err)
	}
	jobs, err := a.FetchQueuedJobs(context.Background())
	if err != nil || len(jobs) != 0 {
		t.Fatalf("jobs=%+v err=%v", jobs, err)
	}
	if calls["/repos/c/actions/runners"] != 1 || calls["/repos/b/actions/runs"] != 1 {
		t.Fatalf("calls %v", calls)
	}
}

func TestProviderAdapterTokenAndDeregister(t *testing.T) {
	var deleted string
	ts := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		if r.Method == http.MethodPost {
			w.Header().Set("Content-Type", "application/json")
			_, _ = fmt.Fprint(w, `{"token":"reg"}`)
			return
		}
		deleted = r.URL.Path
		w.WriteHeader(http.StatusNoContent)
	}))
	defer ts.Close()
	a := NewProviderAdapter(NewClient("", ts.URL, ts.Client()), "", "org", []string{"owner/repo"})
	if _, _, err := NewProviderAdapter(NewClient("", ts.URL, ts.Client()), "", "", nil).AcquireRegistrationToken(context.Background(), ""); err == nil {
		t.Fatal("expected missing scope error")
	}
	token, expires, err := a.AcquireRegistrationToken(context.Background(), "owner/repo")
	if err != nil || token != "reg" || expires.IsZero() {
		t.Fatalf("token=%q expiry=%v err=%v", token, expires, err)
	}
	if err := a.DeregisterRunner(context.Background(), "nope"); err == nil {
		t.Fatal("expected invalid id")
	}
	if err := a.DeregisterRunner(context.Background(), "gh-42"); err != nil {
		t.Fatal(err)
	}
	if deleted != "/repos/owner/repo/actions/runners/42" {
		t.Fatalf("delete path %q", deleted)
	}
	b := NewProviderAdapter(NewClient("", ts.URL, ts.Client()), "", "org", nil)
	if err := b.DeregisterRunner(context.Background(), "9"); err != nil || deleted != "/orgs/org/actions/runners/9" {
		t.Fatalf("org deletion: %q, %v", deleted, err)
	}
}

func TestProviderAdapterRunnerEmptyOrgFallback(t *testing.T) {
	ts := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "application/json")
		if r.URL.Path == "/orgs/o/actions/runners" {
			_, _ = fmt.Fprint(w, `{"runners":[]}`)
			return
		}
		_, _ = fmt.Fprint(w, `{"runners":[{"id":7,"name":"repo runner"}]}`)
	}))
	defer ts.Close()
	a := NewProviderAdapter(NewClient("", ts.URL, ts.Client()), "", "o", []string{"repo"})
	got, err := a.FetchRemoteRunners(context.Background())
	if err != nil || !reflect.DeepEqual([]string{got[0].Name}, []string{"repo runner"}) {
		t.Fatalf("got=%+v err=%v", got, err)
	}
}
