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
