package gitlab

import (
	"context"
	"net/http"
	"net/http/httptest"
	"testing"
)

func TestGitLab_ListRunners(t *testing.T) {
	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "application/json")
		_, _ = w.Write([]byte(`[
			{
				"id": 1,
				"description": "shared-cloud-runner-1",
				"active": true,
				"paused": false,
				"is_shared": true,
				"runner_type": "instance_type",
				"online": true,
				"status": "online",
				"tag_list": ["docker", "amd64"]
			},
			{
				"id": 2,
				"description": "runzero-gl-j10-arm64",
				"active": true,
				"paused": false,
				"is_shared": false,
				"runner_type": "project_type",
				"online": true,
				"status": "online",
				"tag_list": ["arm64"]
			},
			{
				"id": 3,
				"description": "office-mac-mini-runner",
				"active": true,
				"paused": true,
				"is_shared": false,
				"runner_type": "group_type",
				"online": false,
				"status": "offline",
				"tag_list": ["shell", "darwin"]
			}
		]`))
	}))
	defer server.Close()

	client := NewClient("token", server.URL, server.Client())
	runners, err := client.ListRunners(context.Background())
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if len(runners) != 3 {
		t.Fatalf("expected 3 runners, got %d", len(runners))
	}

	info1 := client.ConvertToRunnerInfo(runners[0])
	if *info1.Provider != "gitlab" || *info1.Origin != "cloud" || !info1.IsCloud || info1.Status != "online" {
		t.Errorf("unexpected cloud runner conversion: %+v", info1)
	}

	info2 := client.ConvertToRunnerInfo(runners[1])
	if *info2.Origin != "local" || info2.IsCloud || info2.TargetArch != "arm64" {
		t.Errorf("unexpected local runner conversion: %+v", info2)
	}

	info3 := client.ConvertToRunnerInfo(runners[2])
	if *info3.Origin != "external" || info3.IsCloud || info3.State != "paused" || info3.Status != "paused" {
		t.Errorf("unexpected external runner conversion: %+v", info3)
	}
}

func TestGitLab_ListGroupRunners(t *testing.T) {
	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "application/json")
		_, _ = w.Write([]byte(`[{"id": 42, "description": "group-runner", "active": true, "online": true}]`))
	}))
	defer server.Close()

	client := NewClient("token", server.URL, server.Client())
	runners, err := client.ListGroupRunners(context.Background(), "my-group")
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if len(runners) != 1 || runners[0].ID != 42 {
		t.Fatalf("unexpected group runners: %+v", runners)
	}
}
