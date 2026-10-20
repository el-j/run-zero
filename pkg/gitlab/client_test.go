package gitlab

import (
	"context"
	"net/http"
	"net/http/httptest"
	"testing"
)

func TestGitLabClient_HeadersAndAuth(t *testing.T) {
	var tokenSeen string
	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		tokenSeen = r.Header.Get("PRIVATE-TOKEN")
		w.Header().Set("Content-Type", "application/json")
		_, _ = w.Write([]byte(`{"status": "ok"}`))
	}))
	defer server.Close()

	client := NewClient("glpat-secret123", server.URL, server.Client())
	var result map[string]string
	resp, err := client.DoRequest(context.Background(), "GET", "/test", nil, &result)
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if resp.StatusCode != http.StatusOK {
		t.Errorf("expected 200, got %d", resp.StatusCode)
	}
	if tokenSeen != "glpat-secret123" {
		t.Errorf("expected glpat-secret123, got %s", tokenSeen)
	}
	if result["status"] != "ok" {
		t.Errorf("expected ok status, got %s", result["status"])
	}
}

func TestGitLabClient_ErrorHandling(t *testing.T) {
	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		w.WriteHeader(http.StatusUnauthorized)
		_, _ = w.Write([]byte(`{"message": "401 Unauthorized"}`))
	}))
	defer server.Close()

	client := NewClient("bad-token", server.URL, server.Client())
	var result map[string]string
	_, err := client.DoRequest(context.Background(), "GET", "/runners", nil, &result)
	if err == nil {
		t.Fatal("expected error on 401 response, got nil")
	}
}
