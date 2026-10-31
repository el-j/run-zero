package gitlab

import (
	"context"
	"errors"
	"fmt"
	"io"
	"net/http"
	"net/http/httptest"
	"strings"
	"testing"
)

type gitlabRoundTripper func(*http.Request) (*http.Response, error)

func (f gitlabRoundTripper) RoundTrip(r *http.Request) (*http.Response, error) { return f(r) }

type gitlabErrorBody struct{}

func (gitlabErrorBody) Read([]byte) (int, error) { return 0, errors.New("read failed") }
func (gitlabErrorBody) Close() error             { return nil }

func TestGitLabClientDefaultsErrorsAndNoContent(t *testing.T) {
	c := NewClient(" token ", "", nil)
	if c.BaseURL() != "https://gitlab.com/api/v4" {
		t.Fatalf("default URL %q", c.BaseURL())
	}
	if NewClient("", "https://git.example/api/v4/", nil).BaseURL() != "https://git.example/api/v4" {
		t.Fatal("API URL normalization failed")
	}
	if _, err := c.DoRequest(context.Background(), "BAD METHOD", "/", nil, nil); err == nil || !strings.Contains(err.Error(), "create request failed") {
		t.Fatalf("request creation error %v", err)
	}
	broken := &Client{baseURL: "http://example.test", httpClient: &http.Client{Transport: gitlabRoundTripper(func(*http.Request) (*http.Response, error) { return nil, errors.New("transport") })}}
	if _, err := broken.DoRequest(context.Background(), "GET", "/", nil, nil); err == nil || !strings.Contains(err.Error(), "http request failed") {
		t.Fatalf("transport error %v", err)
	}
	for _, out := range []interface{}{nil, new(map[string]interface{})} {
		c := &Client{baseURL: "http://example.test", httpClient: &http.Client{Transport: gitlabRoundTripper(func(*http.Request) (*http.Response, error) {
			return &http.Response{StatusCode: http.StatusNoContent, Header: make(http.Header), Body: io.NopCloser(strings.NewReader("ignored"))}, nil
		})}}
		if _, err := c.DoRequest(context.Background(), "GET", "/", nil, out); err != nil {
			t.Fatalf("204 error: %v", err)
		}
	}
	bodyClient := &Client{baseURL: "http://example.test", token: "token", httpClient: &http.Client{Transport: gitlabRoundTripper(func(req *http.Request) (*http.Response, error) {
		if req.Header.Get("Content-Type") != "application/json" || req.Header.Get("PRIVATE-TOKEN") != "token" {
			t.Errorf("headers: %v", req.Header)
		}
		return &http.Response{StatusCode: 200, Header: make(http.Header), Body: io.NopCloser(strings.NewReader(`{}`))}, nil
	})}}
	if _, err := bodyClient.DoRequest(context.Background(), "POST", "/", strings.NewReader(`{}`), nil); err != nil {
		t.Fatal(err)
	}
	badJSON := &Client{baseURL: "http://example.test", httpClient: &http.Client{Transport: gitlabRoundTripper(func(*http.Request) (*http.Response, error) {
		return &http.Response{StatusCode: 200, Header: make(http.Header), Body: io.NopCloser(strings.NewReader("{"))}, nil
	})}}
	if _, err := badJSON.DoRequest(context.Background(), "GET", "/", nil, new(map[string]interface{})); err == nil || !strings.Contains(err.Error(), "parse json failed") {
		t.Fatalf("json error %v", err)
	}
	readErr := &Client{baseURL: "http://example.test", httpClient: &http.Client{Transport: gitlabRoundTripper(func(*http.Request) (*http.Response, error) {
		return &http.Response{StatusCode: 200, Header: make(http.Header), Body: gitlabErrorBody{}}, nil
	})}}
	if _, err := readErr.DoRequest(context.Background(), "GET", "/", nil, new(map[string]interface{})); err == nil || !strings.Contains(err.Error(), "read response failed") {
		t.Fatalf("body read error %v", err)
	}
}

func TestGitLabJobsRunnerMethodsAndConversionBranches(t *testing.T) {
	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "application/json")
		switch r.URL.EscapedPath() {
		case "/api/v4/projects/path%2Fproject/jobs":
			_, _ = fmt.Fprint(w, `[{"id":4,"name":"test","stage":"verify","ref":"main","pipeline":{"id":2},"tag_list":["linux"],"web_url":"job"}]`)
		case "/api/v4/groups/group%2Fid/runners":
			_, _ = fmt.Fprint(w, `[{"id":8,"description":"shared","is_shared":true,"active":true,"online":true,"tag_list":["aarch64"]}]`)
		case "/api/v4/runners":
			_, _ = fmt.Fprint(w, `[{"id":9,"name":"named","active":false,"paused":true,"tag_list":["arm64"]}]`)
		default:
			w.WriteHeader(http.StatusBadGateway)
		}
	}))
	defer server.Close()
	c := NewClient("", server.URL, server.Client())
	jobs, err := c.ListProjectPendingJobs(context.Background(), "path/project")
	if err != nil || len(jobs) != 1 {
		t.Fatalf("jobs=%+v err=%v", jobs, err)
	}
	queued := c.ConvertToQueuedJob(jobs[0], "path/project")
	if queued.Status != "queued" || queued.RunID != 2 || queued.WorkflowName == nil || *queued.WorkflowName != "verify" {
		t.Fatalf("queued %+v", queued)
	}
	group, err := c.ListGroupRunners(context.Background(), "group/id")
	if err != nil || len(group) != 1 {
		t.Fatalf("group=%+v err=%v", group, err)
	}
	groupInfo := c.ConvertToRunnerInfo(group[0])
	if groupInfo.Origin == nil || *groupInfo.Origin != "cloud" || groupInfo.TargetArch != "arm64" || groupInfo.Status != "online" {
		t.Fatalf("group conversion %+v", groupInfo)
	}
	all, err := c.ListRunners(context.Background())
	if err != nil || len(all) != 1 {
		t.Fatalf("all=%+v err=%v", all, err)
	}
	info := c.ConvertToRunnerInfo(all[0])
	if info.Name != "named" || info.Status != "paused" || info.State != "paused" || info.TargetArch != "arm64" {
		t.Fatalf("runner conversion %+v", info)
	}
	fallback := c.ConvertToRunnerInfo(GitLabRunner{ID: 11, Online: false, Active: true})
	if fallback.Name != "gitlab-runner-11" || fallback.Status != "offline" || fallback.State != "active" {
		t.Fatalf("fallback conversion %+v", fallback)
	}
	invalidClient := &Client{baseURL: "://bad"}
	brokenURLInfo := invalidClient.ConvertToRunnerInfo(GitLabRunner{ID: 1, Name: "runner"})
	if brokenURLInfo.ProviderInst == nil || *brokenURLInfo.ProviderInst != "gitlab.com" {
		t.Fatalf("URL fallback %+v", brokenURLInfo)
	}
}

func TestGitLabJobAndRunnerAPIErrors(t *testing.T) {
	ts := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) { w.WriteHeader(http.StatusBadGateway) }))
	defer ts.Close()
	c := NewClient("", ts.URL, ts.Client())
	if _, err := c.ListProjectPendingJobs(context.Background(), "x"); err == nil {
		t.Fatal("expected jobs error")
	}
	if _, err := c.ListGroupRunners(context.Background(), "x"); err == nil {
		t.Fatal("expected group error")
	}
	if _, err := c.ListRunners(context.Background()); err == nil {
		t.Fatal("expected runners error")
	}
}
