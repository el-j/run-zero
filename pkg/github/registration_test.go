package github

import (
	"context"
	"net/http"
	"net/http/httptest"
	"testing"
)

func TestClient_CreateRegistrationToken(t *testing.T) {
	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		if r.URL.Path == "/repos/owner/repo/actions/runners/registration-token" && r.Method == "POST" {
			w.Header().Set("Content-Type", "application/json")
			_, _ = w.Write([]byte(`{"token": "secret-token-123", "expires_at": "2026-10-06T22:00:00Z"}`))
			return
		}
		http.NotFound(w, r)
	}))
	defer server.Close()

	client := NewClient("token", server.URL, server.Client())
	token, err := client.CreateRegistrationToken(context.Background(), "owner/repo", "")
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if token != "secret-token-123" {
		t.Errorf("expected 'secret-token-123', got %s", token)
	}
}

func TestClient_GetActionsBilling(t *testing.T) {
	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		if r.URL.Path == "/users/test-user/settings/billing/actions" {
			w.Header().Set("Content-Type", "application/json")
			_, _ = w.Write([]byte(`{"total_minutes_used": 142, "included_minutes": 2000, "total_paid_minutes_used": 0}`))
			return
		}
		http.NotFound(w, r)
	}))
	defer server.Close()

	client := NewClient("token", server.URL, server.Client())
	billing, err := client.GetActionsBilling(context.Background(), "test-user", "")
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if billing.TotalMinutesUsed != 142 || billing.IncludedMinutes != 2000 {
		t.Errorf("unexpected billing data: %+v", billing)
	}
}

func TestClient_ListRunners(t *testing.T) {
	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		if r.URL.Path == "/repos/owner/repo/actions/runners" {
			w.Header().Set("Content-Type", "application/json")
			_, _ = w.Write([]byte(`{
				"total_count": 1,
				"runners": [{"id": 42, "name": "runner-1", "os": "Linux", "status": "online", "busy": true}]
			}`))
			return
		}
		http.NotFound(w, r)
	}))
	defer server.Close()

	client := NewClient("token", server.URL, server.Client())
	runners, err := client.ListRunners(context.Background(), "owner/repo", "")
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if len(runners) != 1 || runners[0].Name != "runner-1" || !runners[0].Busy {
		t.Errorf("unexpected runners: %+v", runners)
	}
}
