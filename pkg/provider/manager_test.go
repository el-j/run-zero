package provider

import (
	"context"
	"fmt"
	"testing"
	"time"

	"github.com/el-j/run-zero/pkg/state"
)

type mockProvider struct {
	id      string
	name    string
	pType   ProviderType
	baseURL string
	runners []state.RunnerInfo
	err     error
}

func (m *mockProvider) ID() string         { return m.id }
func (m *mockProvider) Name() string       { return m.name }
func (m *mockProvider) Type() ProviderType { return m.pType }
func (m *mockProvider) BaseURL() string    { return m.baseURL }
func (m *mockProvider) FetchRemoteRunners(ctx context.Context) ([]state.RunnerInfo, error) {
	return m.runners, m.err
}
func (m *mockProvider) FetchQueuedJobs(ctx context.Context) ([]state.QueuedJob, error) {
	return nil, nil
}
func (m *mockProvider) AcquireRegistrationToken(ctx context.Context, scope string) (string, time.Time, error) {
	return "mock-token", time.Now().Add(time.Hour), nil
}
func (m *mockProvider) DeregisterRunner(ctx context.Context, runnerID string) error {
	return nil
}

func TestManager_RegisterAndGet(t *testing.T) {
	mgr := NewManager()
	p1 := &mockProvider{id: "gh", name: "GitHub", pType: TypeGitHub}
	p2 := &mockProvider{id: "gl-internal", name: "GitLab Internal", pType: TypeGitLab}

	mgr.Register(p1)
	mgr.Register(p2)

	all := mgr.All()
	if len(all) != 2 {
		t.Fatalf("expected 2 providers, got %d", len(all))
	}
	if all[0].ID() != "gh" || all[1].ID() != "gl-internal" {
		t.Errorf("unexpected provider ordering: %+v", all)
	}

	found, ok := mgr.Get("gl-internal")
	if !ok || found.Name() != "GitLab Internal" {
		t.Errorf("failed to get provider by ID: %+v", found)
	}
}

func TestManager_FetchAllRemoteRunners(t *testing.T) {
	mgr := NewManager()
	cloudOrigin := "cloud"
	p1 := &mockProvider{
		id:    "gh",
		pType: TypeGitHub,
		runners: []state.RunnerInfo{
			{ID: "gh-1", Name: "GitHub Actions 1", IsCloud: true, Origin: &cloudOrigin},
		},
	}
	p2 := &mockProvider{
		id:    "gl",
		pType: TypeGitLab,
		runners: []state.RunnerInfo{
			{ID: "gl-10", Name: "GitLab Shared Runner", IsCloud: true, Origin: &cloudOrigin},
		},
	}
	p3 := &mockProvider{
		id:  "gl-err",
		err: fmt.Errorf("connection timeout"),
	}

	mgr.Register(p1)
	mgr.Register(p2)
	mgr.Register(p3)

	runners, errs := mgr.FetchAllRemoteRunners(context.Background())
	if len(runners) != 2 {
		t.Errorf("expected 2 runners, got %d", len(runners))
	}
	if len(errs) != 1 {
		t.Errorf("expected 1 error, got %d", len(errs))
	}
}

func TestManager_MergeRunners(t *testing.T) {
	localOrigin := "local"
	cloudOrigin := "cloud"

	local := []state.RunnerInfo{
		{ID: "r1", Name: "runzero-j101-r202-amd64-repo-1", Status: "running", Origin: &localOrigin},
	}
	remote := []state.RunnerInfo{
		// Duplicate of local (reported by GitHub Actions API as self-hosted)
		{ID: "gh-99", Name: "runzero-j101-r202-amd64-repo-1", Status: "online", Origin: &localOrigin},
		// Actual cloud runner
		{ID: "gh-100", Name: "GitHub Actions 1", Status: "online", IsCloud: true, Origin: &cloudOrigin},
	}

	merged := MergeRunners(local, remote)
	if len(merged) != 2 {
		t.Fatalf("expected 2 merged runners (deduplicated), got %d: %+v", len(merged), merged)
	}
	if merged[0].ID != "r1" || merged[0].Status != "running" {
		t.Errorf("expected local runner to be preserved, got %+v", merged[0])
	}
	if merged[1].ID != "gh-100" || !merged[1].IsCloud {
		t.Errorf("expected cloud runner, got %+v", merged[1])
	}
}
