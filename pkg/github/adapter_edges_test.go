package github

import (
	"context"
	"fmt"
	"net/http"
	"net/http/httptest"
	"reflect"
	"testing"
)

func TestRegistrationScopesErrorsAndConversion(t *testing.T) {
	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "application/json")
		switch r.URL.Path {
		case "/orgs/acme/actions/runners/registration-token":
			_, _ = fmt.Fprint(w, `{"token":"org-token"}`)
		case "/users/acme/settings/billing/actions":
			_, _ = fmt.Fprint(w, `{"included_minutes":100,"total_minutes_used":4}`)
		case "/orgs/acme/actions/runners":
			_, _ = fmt.Fprint(w, `{"runners":[{"id":8,"name":"runzero-local","os":"Linux","status":"offline","labels":[{"name":"arm64"},{"name":"macos-latest"}]}]}`)
		case "/orgs/acme/actions/runners/8":
			w.WriteHeader(http.StatusNoContent)
		case "/orgs/acme/settings/billing/actions":
			w.WriteHeader(http.StatusBadGateway)
		case "/repos/acme/repo/actions/runners/registration-token":
			w.WriteHeader(http.StatusBadGateway)
		case "/repos/acme/repo/actions/runners":
			w.WriteHeader(http.StatusBadGateway)
		default:
			http.NotFound(w, r)
		}
	}))
	defer server.Close()
	client := NewClient("", server.URL, server.Client())
	if _, err := client.CreateRegistrationToken(context.Background(), "", ""); err == nil {
		t.Fatal("expected missing token scope error")
	}
	if token, err := client.CreateRegistrationToken(context.Background(), "", "acme"); err != nil || token != "org-token" {
		t.Fatalf("org token=%q err=%v", token, err)
	}
	if _, err := client.CreateRegistrationToken(context.Background(), "acme/repo", ""); err == nil {
		t.Fatal("expected API error")
	}
	if _, err := client.GetActionsBilling(context.Background(), "", ""); err == nil {
		t.Fatal("expected missing billing scope")
	}
	bill, err := client.GetActionsBilling(context.Background(), "acme", "")
	if err != nil || bill.TotalMinutesUsed != 4 {
		t.Fatalf("billing=%+v err=%v", bill, err)
	}
	if _, err := client.GetActionsBilling(context.Background(), "", "acme"); err == nil {
		t.Fatal("expected billing API error")
	}
	if _, err := client.ListRunners(context.Background(), "", ""); err == nil {
		t.Fatal("expected missing runners scope")
	}
	runners, err := client.ListRunners(context.Background(), "", "acme")
	if err != nil || len(runners) != 1 || runners[0].Scope != "orgs/acme" || runners[0].Labels[0] != "arm64" {
		t.Fatalf("runners=%+v err=%v", runners, err)
	}
	if _, err := client.ListRunners(context.Background(), "acme/repo", ""); err == nil {
		t.Fatal("expected runners API error")
	}
	info := client.ConvertToRunnerInfo(runners[0])
	if info.Origin == nil || *info.Origin != "local" || info.Backend != "docker" || info.Status != "offline" || info.TargetArch != "arm64" {
		t.Fatalf("converted info %+v", info)
	}
	if err := client.DeleteRunner(context.Background(), "", "", 1); err == nil {
		t.Fatal("expected missing delete scope")
	}
	if err := client.DeleteRunner(context.Background(), "", "acme", 8); err != nil {
		t.Fatal(err)
	}
	if err := client.DeleteRunner(context.Background(), "acme/repo", "", 8); err == nil {
		t.Fatal("expected delete API error")
	}
}

func TestConvertToRunnerInfoClassifications(t *testing.T) {
	client := NewClient("", "", nil)
	cases := []struct {
		runner                        RunnerRegistration
		origin, backend, status, arch string
		cloud                         bool
	}{
		{RunnerRegistration{Name: "hosted runner", Status: "offline", Labels: []string{"windows-2022"}}, "cloud", "cloud-hosted", "offline", "amd64", true},
		{RunnerRegistration{Name: "ordinary", Status: "online", Labels: []string{"AARCH64"}}, "external", "github-runner", "online", "arm64", false},
		{RunnerRegistration{Name: "GitHub Actions 1", Status: "online"}, "cloud", "cloud-hosted", "online", "amd64", true},
		{RunnerRegistration{Name: "external", Status: "online", Busy: true}, "external", "github-runner", "busy", "amd64", false},
		{RunnerRegistration{Name: "external", Status: "online", Labels: []string{"ubuntu-latest"}}, "cloud", "cloud-hosted", "online", "amd64", true},
	}
	for _, tc := range cases {
		got := client.ConvertToRunnerInfo(tc.runner)
		if got.Origin == nil || *got.Origin != tc.origin || got.Backend != tc.backend || got.Status != tc.status || got.TargetArch != tc.arch || got.IsCloud != tc.cloud {
			t.Errorf("%+v => %+v", tc.runner, got)
		}
	}
}

func TestCreateRegistrationTokenEmpty(t *testing.T) {
	ts := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) { _, _ = fmt.Fprint(w, `{}`) }))
	defer ts.Close()
	if _, err := NewClient("", ts.URL, ts.Client()).CreateRegistrationToken(context.Background(), "r", ""); err == nil {
		t.Fatal("expected empty token error")
	}
}

func TestPollerSetReposAndPriorityMergeDiscovered(t *testing.T) {
	p := NewPoller(nil, nil, nil, nil, 1)
	p.SetRepos([]string{"  a/b ", "", "  ", "A/C"})
	if got := p.Repos(); !reflect.DeepEqual(got, []string{"a/b", "A/C"}) {
		t.Fatalf("repos=%v", got)
	}
	pm, err := NewPriorityManager("", []string{"A/B", "base"}, nil)
	if err != nil {
		t.Fatal(err)
	}
	pm.MergeDiscovered([]string{"a/b", " new/repo ", "new/repo", " ", "Next"})
	prio, _ := pm.GetState()
	if !reflect.DeepEqual(prio, []string{"A/B", "base", "new/repo", "Next"}) {
		t.Fatalf("priority=%v", prio)
	}
}

func TestRerunJobStatuses(t *testing.T) {
	status := http.StatusAccepted
	ts := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		if r.URL.Path != "/repos/o/r/actions/jobs/7/rerun" {
			t.Errorf("path %s", r.URL.Path)
		}
		w.WriteHeader(status)
	}))
	defer ts.Close()
	c := NewClient("", ts.URL, ts.Client())
	for _, code := range []int{http.StatusOK, http.StatusCreated, http.StatusAccepted} {
		status = code
		if err := c.RerunJob(context.Background(), "o/r", 7); err != nil {
			t.Errorf("status %d: %v", code, err)
		}
	}
	status = http.StatusNoContent
	if err := c.RerunJob(context.Background(), "o/r", 7); err == nil {
		t.Fatal("expected unexpected status")
	}
}
