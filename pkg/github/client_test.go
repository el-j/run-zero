package github

import (
	"context"
	"net/http"
	"net/http/httptest"
	"strings"
	"testing"
	"time"
)

func TestNewClient_Defaults(t *testing.T) {
	c := NewClient("token", "", nil)
	if c.baseURL != "https://api.github.com" {
		t.Errorf("expected default baseURL, got %s", c.baseURL)
	}
	if c.httpClient == nil {
		t.Errorf("expected default httpClient")
	}
}

func TestClient_DoRequest_Success(t *testing.T) {
	ts := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		if r.Header.Get("Authorization") != "Bearer secret-token" {
			t.Errorf("expected Bearer secret-token, got %s", r.Header.Get("Authorization"))
		}
		if r.Header.Get("Accept") != "application/vnd.github+json" {
			t.Errorf("expected vnd.github+json accept header")
		}
		w.Header().Set("X-RateLimit-Remaining", "4990")
		w.Header().Set("X-RateLimit-Limit", "5000")
		w.Header().Set("X-RateLimit-Reset", "1700000000")
		w.WriteHeader(http.StatusOK)
		_, _ = w.Write([]byte(`{"message": "pong"}`))
	}))
	defer ts.Close()

	client := NewClient("secret-token", ts.URL, nil)
	var out struct {
		Message string `json:"message"`
	}
	resp, err := client.DoRequest(context.Background(), http.MethodGet, "/test", nil, &out)
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if resp.StatusCode != http.StatusOK {
		t.Fatalf("expected 200, got %d", resp.StatusCode)
	}
	if out.Message != "pong" {
		t.Fatalf("expected message pong, got %s", out.Message)
	}

	rl := client.RateLimit()
	if rl.Remaining != 4990 || rl.Limit != 5000 {
		t.Fatalf("unexpected rate limit: %+v", rl)
	}
	if rl.Reset.UTC() != time.Unix(1700000000, 0).UTC() {
		t.Fatalf("unexpected reset time: %v", rl.Reset)
	}
}

func TestClient_DoRequest_ErrorAndBody(t *testing.T) {
	ts := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		if r.Header.Get("Content-Type") != "application/json" {
			t.Errorf("expected Content-Type application/json")
		}
		w.WriteHeader(http.StatusNotFound)
		_, _ = w.Write([]byte(`{"error": "not found"}`))
	}))
	defer ts.Close()

	client := NewClient("", ts.URL, http.DefaultClient)
	_, err := client.DoRequest(context.Background(), http.MethodPost, "/missing", strings.NewReader(`{}`), nil)
	if err == nil {
		t.Fatal("expected error on 404, got nil")
	}

	// Test invalid URL
	_, err = client.DoRequest(context.Background(), "INVALID METHOD\x7f", "/test", nil, nil)
	if err == nil {
		t.Fatal("expected error on invalid method")
	}
}

func TestClient_DoRequest_DecodeError(t *testing.T) {
	ts := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		w.WriteHeader(http.StatusOK)
		_, _ = w.Write([]byte(`invalid-json`))
	}))
	defer ts.Close()

	client := NewClient("", ts.URL, nil)
	var out map[string]interface{}
	_, err := client.DoRequest(context.Background(), http.MethodGet, "/bad-json", nil, &out)
	if err == nil {
		t.Fatal("expected error decoding bad json")
	}
}

func TestClient_RefreshRateLimit(t *testing.T) {
	body, code := `{"resources":{"core":{"limit":5000,"remaining":42,"reset":1900000000}}}`, http.StatusOK
	ts := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		if r.URL.Path != "/rate_limit" {
			t.Errorf("unexpected path %s", r.URL.Path)
		}
		w.WriteHeader(code)
		_, _ = w.Write([]byte(body))
	}))
	defer ts.Close()
	c := NewClient("tok", ts.URL, ts.Client())

	// An exhausted quota must not stop the refresh itself.
	c.rateLimit = RateLimit{Limit: 5000, Remaining: 0, Reset: time.Now().Add(time.Hour)}
	if err := c.RefreshRateLimit(context.Background()); err != nil {
		t.Fatalf("refresh: %v", err)
	}
	if rl := c.RateLimit(); rl.Remaining != 42 || rl.Limit != 5000 || rl.Reset.Unix() != 1900000000 {
		t.Fatalf("unexpected rate limit %+v", rl)
	}

	for name, tc := range map[string]struct {
		body string
		code int
	}{
		"http error":    {`{}`, http.StatusInternalServerError},
		"bad json":      {`{`, http.StatusOK},
		"no core quota": {`{}`, http.StatusOK},
	} {
		body, code = tc.body, tc.code
		if err := c.RefreshRateLimit(context.Background()); err == nil {
			t.Errorf("%s: expected error", name)
		}
	}
	if c.RateLimit().Remaining != 42 {
		t.Error("failed refreshes must keep the last good quota")
	}

	if err := NewClient("tok", "http://127.0.0.1:1", nil).RefreshRateLimit(context.Background()); err == nil {
		t.Error("expected connection error")
	}
	if err := NewClient("tok", "://bad", nil).RefreshRateLimit(context.Background()); err == nil {
		t.Error("expected request build error")
	}
}
