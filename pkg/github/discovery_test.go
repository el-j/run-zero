package github

import (
	"context"
	"net/http"
	"net/http/httptest"
	"testing"
	"time"
)

func TestDiscoverRepositories_ExplicitConfig(t *testing.T) {
	client := NewClient("token", "", nil)
	repos, err := client.DiscoverRepositories(context.Background(), "owner", "", 60, true, "el-j/herbful, el-j/run-zero, el-j/herbful")
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if len(repos) != 2 {
		t.Fatalf("expected 2 repos, got %d", len(repos))
	}
	if repos[0] != "el-j/herbful" || repos[1] != "el-j/run-zero" {
		t.Errorf("expected sorted unique repos, got %v", repos)
	}
}

func TestDiscoverRepositories_AutoDiscoverOrg(t *testing.T) {
	now := time.Now().UTC().Format(time.RFC3339)
	oldTime := time.Now().UTC().AddDate(0, 0, -100).Format(time.RFC3339)

	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		switch r.URL.Path {
		case "/users/my-org":
			w.Header().Set("Content-Type", "application/json")
			_, _ = w.Write([]byte(`{"type": "Organization"}`))
		case "/orgs/my-org/repos":
			w.Header().Set("Content-Type", "application/json")
			_, _ = w.Write([]byte(`[
				{"full_name": "my-org/repo1", "archived": false, "pushed_at": "` + now + `"},
				{"full_name": "my-org/archived-repo", "archived": true, "pushed_at": "` + now + `"},
				{"full_name": "other/repo", "archived": false, "pushed_at": "` + now + `"},
				{"full_name": "my-org/old-repo", "archived": false, "pushed_at": "` + oldTime + `"}
			]`))
		default:
			http.NotFound(w, r)
		}
	}))
	defer server.Close()

	client := NewClient("token", server.URL, server.Client())
	repos, err := client.DiscoverRepositories(context.Background(), "my-org", "", 60, true, "")
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if len(repos) != 1 || repos[0] != "my-org/repo1" {
		t.Errorf("expected ['my-org/repo1'], got %v", repos)
	}
}
