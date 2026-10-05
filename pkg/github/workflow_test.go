package github

import (
	"context"
	"net/http"
	"net/http/httptest"
	"strings"
	"testing"
)

func TestClient_TriggerWorkflowAction(t *testing.T) {
	ts := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		if strings.HasSuffix(r.URL.Path, "/cancel") {
			w.WriteHeader(http.StatusAccepted)
			return
		}
		if strings.HasSuffix(r.URL.Path, "/rerun") {
			w.WriteHeader(http.StatusCreated)
			return
		}
		if strings.HasSuffix(r.URL.Path, "/rerun-failed-jobs") {
			w.WriteHeader(http.StatusOK)
			return
		}
		w.WriteHeader(http.StatusNotFound)
	}))
	defer ts.Close()

	client := NewClient("test-token", ts.URL, nil)

	if err := client.TriggerWorkflowAction(context.Background(), "owner/repo", 123, "cancel"); err != nil {
		t.Fatalf("unexpected cancel error: %v", err)
	}
	if err := client.TriggerWorkflowAction(context.Background(), "owner/repo", 123, "rerun"); err != nil {
		t.Fatalf("unexpected rerun error: %v", err)
	}
	if err := client.TriggerWorkflowAction(context.Background(), "owner/repo", 123, "rerun-failed"); err != nil {
		t.Fatalf("unexpected rerun-failed error: %v", err)
	}

	// Unsupported action
	if err := client.TriggerWorkflowAction(context.Background(), "owner/repo", 123, "invalid"); err == nil {
		t.Fatal("expected error on unsupported action")
	}
}

func TestClient_TriggerWorkflowAction_ServerError(t *testing.T) {
	ts := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		w.WriteHeader(http.StatusBadGateway)
		_, _ = w.Write([]byte(`bad gateway`))
	}))
	defer ts.Close()

	client := NewClient("test-token", ts.URL, nil)
	if err := client.TriggerWorkflowAction(context.Background(), "owner/repo", 123, "cancel"); err == nil {
		t.Fatal("expected error on 502 bad gateway")
	}
}
