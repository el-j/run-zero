package github

import (
	"context"
	"fmt"
	"strconv"
	"strings"
	"time"

	"github.com/el-j/run-zero/pkg/provider"
	"github.com/el-j/run-zero/pkg/state"
)

// ProviderAdapter adapts github.Client to the provider.CIProvider interface.
type ProviderAdapter struct {
	client *Client
	owner  string
	org    string
	repos  []string
}

// NewProviderAdapter creates an adapter for GitHub Actions.
func NewProviderAdapter(client *Client, owner, org string, repos []string) *ProviderAdapter {
	return &ProviderAdapter{
		client: client,
		owner:  owner,
		org:    org,
		repos:  repos,
	}
}

func (a *ProviderAdapter) ID() string {
	return "github"
}

func (a *ProviderAdapter) Name() string {
	if a.org != "" {
		return fmt.Sprintf("GitHub (%s)", a.org)
	}
	if a.owner != "" {
		return fmt.Sprintf("GitHub (@%s)", a.owner)
	}
	return "GitHub"
}

func (a *ProviderAdapter) Type() provider.ProviderType {
	return provider.TypeGitHub
}

func (a *ProviderAdapter) BaseURL() string {
	return a.client.baseURL
}

func (a *ProviderAdapter) FetchRemoteRunners(ctx context.Context) ([]state.RunnerInfo, error) {
	// First query org-level runners if configured
	if a.org != "" {
		runners, err := a.client.ListRunners(ctx, "", a.org)
		if err == nil && len(runners) > 0 {
			res := make([]state.RunnerInfo, len(runners))
			for i, r := range runners {
				res[i] = a.client.ConvertToRunnerInfo(r)
			}
			return res, nil
		}
	}

	// Otherwise query per monitored repo
	var allRunners []state.RunnerInfo
	seen := make(map[int64]bool)
	for _, repo := range a.repos {
		runners, err := a.client.ListRunners(ctx, repo, "")
		if err != nil {
			continue
		}
		for _, r := range runners {
			if !seen[r.ID] {
				seen[r.ID] = true
				allRunners = append(allRunners, a.client.ConvertToRunnerInfo(r))
			}
		}
	}
	return allRunners, nil
}

func (a *ProviderAdapter) FetchQueuedJobs(ctx context.Context) ([]state.QueuedJob, error) {
	var allJobs []state.QueuedJob
	for _, repo := range a.repos {
		jobs, err := a.client.ListQueuedJobs(ctx, repo)
		if err != nil {
			continue
		}
		allJobs = append(allJobs, jobs...)
	}
	return allJobs, nil
}

func (a *ProviderAdapter) AcquireRegistrationToken(ctx context.Context, scope string) (string, time.Time, error) {
	token, err := a.client.CreateRegistrationToken(ctx, scope, a.org)
	if err != nil {
		return "", time.Time{}, err
	}
	return token, time.Now().Add(time.Hour), nil
}

func (a *ProviderAdapter) DeregisterRunner(ctx context.Context, runnerID string) error {
	cleanID := strings.TrimPrefix(runnerID, "gh-")
	id, err := strconv.ParseInt(cleanID, 10, 64)
	if err != nil {
		return fmt.Errorf("invalid runner id: %s", runnerID)
	}

	targetRepo := ""
	if len(a.repos) > 0 {
		targetRepo = a.repos[0]
	}
	return a.client.DeleteRunner(ctx, targetRepo, a.org, id)
}
