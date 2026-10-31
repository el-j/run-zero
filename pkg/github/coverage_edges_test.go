package github

import (
	"context"
	"errors"
	"fmt"
	"io"
	"net/http"
	"net/http/httptest"
	"strings"
	"testing"
	"time"
)

type githubRoundTripper func(*http.Request) (*http.Response, error)

func (f githubRoundTripper) RoundTrip(r *http.Request) (*http.Response, error) { return f(r) }

type githubErrorBody struct{}

func (githubErrorBody) Read([]byte) (int, error) { return 0, errors.New("read failed") }
func (githubErrorBody) Close() error             { return nil }

func TestGitHubClientRequestAndCacheFailures(t *testing.T) {
	transportErr := NewClient("", "http://example.test", &http.Client{Transport: githubRoundTripper(func(*http.Request) (*http.Response, error) { return nil, errors.New("transport") })})
	if _, err := transportErr.DoRequest(context.Background(), "GET", "/", nil, nil); err == nil {
		t.Fatal("expected transport error")
	}
	readErr := NewClient("", "http://example.test", &http.Client{Transport: githubRoundTripper(func(*http.Request) (*http.Response, error) {
		return &http.Response{StatusCode: 200, Header: make(http.Header), Body: githubErrorBody{}}, nil
	})})
	if _, err := readErr.DoRequest(context.Background(), "GET", "/", nil, new(map[string]interface{})); err == nil || !strings.Contains(err.Error(), "failed reading response") {
		t.Fatalf("read error %v", err)
	}
	cacheClient := NewClient("", "http://example.test", &http.Client{Transport: githubRoundTripper(func(*http.Request) (*http.Response, error) {
		return &http.Response{StatusCode: http.StatusNotModified, Header: make(http.Header), Body: io.NopCloser(strings.NewReader(""))}, nil
	})})
	cacheClient.etags["http://example.test/value"] = cachedResponse{etag: "etag", body: []byte("not json")}
	if _, err := cacheClient.DoRequest(context.Background(), "GET", "/value", nil, new(map[string]interface{})); err == nil || !strings.Contains(err.Error(), "failed decoding cached response") {
		t.Fatalf("cache decode error %v", err)
	}
	ctx, cancel := context.WithCancel(context.Background())
	cancel()
	if _, err := NewClient("", "http://example.test", nil).DoRequest(ctx, "GET", "/", nil, nil); err == nil {
		t.Fatal("expected canceled request")
	}
}

func TestGitHubClientETagCacheReset(t *testing.T) {
	ts := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("ETag", "fresh")
		_, _ = fmt.Fprint(w, `{}`)
	}))
	defer ts.Close()
	c := NewClient("", ts.URL, ts.Client())
	for i := 0; i < maxETagEntries; i++ {
		c.etags[fmt.Sprintf("old-%d", i)] = cachedResponse{etag: "x", body: []byte(`{}`)}
	}
	if _, err := c.DoRequest(context.Background(), "GET", "/new", nil, new(map[string]interface{})); err != nil {
		t.Fatal(err)
	}
	if len(c.etags) != 1 {
		t.Fatalf("cache was not reset: %d entries", len(c.etags))
	}
}

func TestDiscoverRepositoriesBranches(t *testing.T) {
	if got, err := NewClient("", "", nil).DiscoverRepositories(context.Background(), "", "", 0, false, " z/b, a/c,z/b , ,a/a "); err != nil || strings.Join(got, ",") != "a/a,a/c,z/b" {
		t.Fatalf("configured=%v err=%v", got, err)
	}
	if got, err := NewClient("", "", nil).DiscoverRepositories(context.Background(), "", "", 0, true, ""); err != nil || len(got) != 0 {
		t.Fatalf("disabled discovery=%v %v", got, err)
	}
	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "application/json")
		switch r.URL.Path {
		case "/users/acme":
			_, _ = fmt.Fprint(w, `{"type":"User"}`)
		case "/user/repos":
			if r.URL.Query().Get("page") == "1" {
				_, _ = fmt.Fprint(w, `[{"full_name":"acme/z","pushed_at":"bad"},{"full_name":"other/repo"},{"full_name":"acme/a","archived":true},{"full_name":"acme/b","pushed_at":""}]`)
				return
			}
			_, _ = fmt.Fprint(w, `[]`)
		default:
			http.NotFound(w, r)
		}
	}))
	defer server.Close()
	c := NewClient("token", server.URL, server.Client())
	got, err := c.DiscoverRepositories(context.Background(), "acme", "", 0, true, "")
	if err != nil || strings.Join(got, ",") != "acme/b,acme/z" {
		t.Fatalf("discovered=%v err=%v", got, err)
	}
}

func TestDiscoverOrganizationPaginationAndErrors(t *testing.T) {
	old := time.Now().UTC().AddDate(0, 0, -200).Format(time.RFC3339)
	pageOne := make([]string, 0, 100)
	for i := 0; i < 99; i++ {
		pageOne = append(pageOne, fmt.Sprintf(`{"full_name":"org/r%02d"}`, i))
	}
	pageOne = append(pageOne, `{"full_name":"org/old","pushed_at":"`+old+`"}`)
	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "application/json")
		switch r.URL.Path {
		case "/users/org":
			_, _ = fmt.Fprint(w, `{"type":"Organization"}`)
		case "/orgs/org/repos":
			if r.URL.Query().Get("page") == "1" {
				_, _ = fmt.Fprintf(w, "[%s]", strings.Join(pageOne, ","))
				return
			}
			_, _ = fmt.Fprint(w, `[{"full_name":"org/last"}]`)
		default:
			http.NotFound(w, r)
		}
	}))
	defer server.Close()
	got, err := NewClient("token", server.URL, server.Client()).DiscoverRepositories(context.Background(), "", "org", 1, true, "")
	if err != nil || len(got) != 99 || got[98] != "org/r98" {
		t.Fatalf("pagination count=%d err=%v last=%v", len(got), err, got[len(got)-1])
	}
	failing := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) { w.WriteHeader(http.StatusBadGateway) }))
	defer failing.Close()
	c := NewClient("token", failing.URL, failing.Client())
	if _, err := c.DiscoverRepositories(context.Background(), "owner", "", 5, true, ""); err == nil {
		t.Fatal("expected first-page error")
	}
	partial := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		if r.URL.Query().Get("page") == "1" {
			w.Header().Set("Content-Type", "application/json")
			_, _ = fmt.Fprint(w, `[{"full_name":"owner/repo"}]`)
			return
		}
		w.WriteHeader(http.StatusBadGateway)
	}))
	defer partial.Close()
	got, err = NewClient("token", partial.URL, partial.Client()).DiscoverRepositories(context.Background(), "owner", "", 5, true, "")
	if err != nil || len(got) != 1 || got[0] != "owner/repo" {
		t.Fatalf("partial results=%v err=%v", got, err)
	}
}

func TestDiscoverUserLookupFailureAndTargetFiltering(t *testing.T) {
	ts := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "application/json")
		if r.URL.Path == "/users/org" {
			w.WriteHeader(http.StatusNotFound)
			return
		}
		_, _ = fmt.Fprint(w, `[{"full_name":"org/ok"},{"full_name":"other/x"},{"full_name":"org/too-old","pushed_at":"2000-01-01T00:00:00Z"}]`)
	}))
	defer ts.Close()
	got, err := NewClient("token", ts.URL, ts.Client()).DiscoverRepositories(context.Background(), "owner", "org", 1, true, "")
	if err != nil || len(got) != 1 || got[0] != "org/ok" {
		t.Fatalf("filtered=%v err=%v", got, err)
	}
}

func TestDiscoverPaginationContinuesAfterFullPage(t *testing.T) {
	items := make([]string, 100)
	for i := range items {
		items[i] = fmt.Sprintf(`{"full_name":"owner/repo-%03d"}`, i)
	}
	ts := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "application/json")
		if r.URL.Query().Get("page") == "1" {
			_, _ = fmt.Fprintf(w, "[%s]", strings.Join(items, ","))
			return
		}
		_, _ = fmt.Fprint(w, `[]`)
	}))
	defer ts.Close()
	got, err := NewClient("token", ts.URL, ts.Client()).DiscoverRepositories(context.Background(), "owner", "", 1, true, "")
	if err != nil || len(got) != 100 {
		t.Fatalf("got %d repositories, err=%v", len(got), err)
	}
}

func TestWorkflowActionUnexpectedSuccessStatus(t *testing.T) {
	ts := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) { w.WriteHeader(http.StatusNoContent) }))
	defer ts.Close()
	c := NewClient("", ts.URL, ts.Client())
	if err := c.TriggerWorkflowAction(context.Background(), "o/r", 1, "cancel"); err == nil {
		t.Fatal("expected unexpected status error")
	}
}

func TestDiscoverPartialResultsThenPageError(t *testing.T) {
	items := make([]string, 100)
	for i := range items {
		items[i] = fmt.Sprintf(`{"full_name":"owner/repo-%03d"}`, i)
	}
	ts := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		if r.URL.Query().Get("page") == "1" {
			w.Header().Set("Content-Type", "application/json")
			_, _ = fmt.Fprintf(w, "[%s]", strings.Join(items, ","))
			return
		}
		w.WriteHeader(http.StatusBadGateway)
	}))
	defer ts.Close()
	got, err := NewClient("token", ts.URL, ts.Client()).DiscoverRepositories(context.Background(), "owner", "", 1, true, "")
	if err != nil || len(got) != 100 {
		t.Fatalf("partial page results=%d err=%v", len(got), err)
	}
}
