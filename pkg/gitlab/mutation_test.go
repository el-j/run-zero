package gitlab

import (
	"context"
	"net/http"
	"net/http/httptest"
	"testing"
	"time"
)

func TestNewClient_DefaultHTTPClientHasTimeout(t *testing.T) {
	if c := NewClient("t", "", nil); c.httpClient == nil || c.httpClient.Timeout != 15*time.Second {
		t.Fatalf("default client: %+v", c.httpClient)
	}
	custom := &http.Client{}
	if c := NewClient("t", "", custom); c.httpClient != custom {
		t.Fatal("a given client must be used as is")
	}
}

func TestDoRequest_HTTP400IsAnError(t *testing.T) {
	srv := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		w.WriteHeader(http.StatusBadRequest)
		_, _ = w.Write([]byte("[]")) // valid JSON: only the status can fail it
	}))
	defer srv.Close()
	if _, err := NewClient("t", srv.URL, srv.Client()).ListRunners(context.Background()); err == nil {
		t.Fatal("HTTP 400 must fail the request")
	}
}

func TestFetchRemoteRunners_UsesGroupEndpointOnlyWithAGroup(t *testing.T) {
	var paths []string
	srv := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		paths = append(paths, r.URL.Path)
		_, _ = w.Write([]byte(`[{"id":1,"description":"r"}]`))
	}))
	defer srv.Close()
	c := NewClient("t", srv.URL, srv.Client())

	if _, err := NewProviderAdapter("", "", c, "grp", nil).FetchRemoteRunners(context.Background()); err != nil || paths[0] != "/api/v4/groups/grp/runners" {
		t.Fatalf("group: %v %v", err, paths)
	}
	paths = nil
	if _, err := NewProviderAdapter("", "", c, "", nil).FetchRemoteRunners(context.Background()); err != nil || len(paths) != 1 || paths[0] != "/api/v4/runners" {
		t.Fatalf("instance: %v %v", err, paths)
	}
}

func TestAcquireRegistrationToken_ExpiresInTwoHours(t *testing.T) {
	_, exp, err := NewProviderAdapter("", "", NewClient("tok", "", nil), "", nil).AcquireRegistrationToken(context.Background(), "")
	if d := time.Until(exp); err != nil || d < 119*time.Minute || d > 121*time.Minute {
		t.Fatalf("expiry in %s, err %v", d, err)
	}
}

func TestConvertToRunnerInfo_FallsBackToGitLabComWithoutAHost(t *testing.T) {
	if got := NewClient("t", "relative/path", nil).ConvertToRunnerInfo(GitLabRunner{ID: 1}).TargetRepo; got != "gitlab.com" {
		t.Fatalf("no host: %q", got)
	}
	if got := NewClient("t", "https://git.example.com", nil).ConvertToRunnerInfo(GitLabRunner{ID: 1}).TargetRepo; got != "git.example.com" {
		t.Fatalf("host: %q", got)
	}
}
