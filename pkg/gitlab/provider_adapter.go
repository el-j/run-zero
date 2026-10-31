package gitlab

import (
	"context"
	"fmt"
	"net/url"
	"time"

	"github.com/el-j/run-zero/pkg/provider"
	"github.com/el-j/run-zero/pkg/state"
)

// ProviderAdapter adapts gitlab.Client to the provider.CIProvider interface.
type ProviderAdapter struct {
	client   *Client
	id       string
	name     string
	group    string
	projects []string
}

// NewProviderAdapter creates an adapter for a GitLab SaaS or self-hosted instance.
func NewProviderAdapter(id, name string, client *Client, group string, projects []string) *ProviderAdapter {
	if id == "" {
		id = "gitlab"
	}
	if name == "" {
		name = "GitLab"
		if u, err := url.Parse(client.baseURL); err == nil && u.Host != "" {
			name = fmt.Sprintf("GitLab (%s)", u.Host)
		}
	}
	return &ProviderAdapter{
		client:   client,
		id:       id,
		name:     name,
		group:    group,
		projects: projects,
	}
}

// ID returns the configured GitLab provider identifier.
func (a *ProviderAdapter) ID() string {
	return a.id
}

// Name returns the configured GitLab provider display name.
func (a *ProviderAdapter) Name() string {
	return a.name
}

// Type returns the GitLab provider family.
func (a *ProviderAdapter) Type() provider.ProviderType {
	return provider.TypeGitLab
}

// BaseURL returns the configured GitLab API root.
func (a *ProviderAdapter) BaseURL() string {
	return a.client.baseURL
}

// FetchRemoteRunners lists runners accessible to the configured group or instance.
func (a *ProviderAdapter) FetchRemoteRunners(ctx context.Context) ([]state.RunnerInfo, error) {
	if a.group != "" {
		runners, err := a.client.ListGroupRunners(ctx, a.group)
		if err == nil {
			res := make([]state.RunnerInfo, len(runners))
			for i, r := range runners {
				res[i] = a.client.ConvertToRunnerInfo(r)
			}
			return res, nil
		}
	}

	runners, err := a.client.ListRunners(ctx)
	if err != nil {
		return nil, err
	}

	res := make([]state.RunnerInfo, len(runners))
	for i, r := range runners {
		res[i] = a.client.ConvertToRunnerInfo(r)
	}
	return res, nil
}

// FetchQueuedJobs collects pending jobs from the configured projects.
func (a *ProviderAdapter) FetchQueuedJobs(ctx context.Context) ([]state.QueuedJob, error) {
	var allJobs []state.QueuedJob
	for _, proj := range a.projects {
		jobs, err := a.client.ListProjectPendingJobs(ctx, proj)
		if err != nil {
			continue
		}
		for _, j := range jobs {
			allJobs = append(allJobs, a.client.ConvertToQueuedJob(j, proj))
		}
	}
	return allJobs, nil
}

// AcquireRegistrationToken returns the configured GitLab access token and its local expiry.
func (a *ProviderAdapter) AcquireRegistrationToken(ctx context.Context, scope string) (string, time.Time, error) {
	// Returns authentication token or group token
	if a.client.token != "" {
		return a.client.token, time.Now().Add(2 * time.Hour), nil
	}
	return "", time.Time{}, fmt.Errorf("no gitlab token configured for registration")
}

// DeregisterRunner deletes a runner registration by its GitLab ID.
func (a *ProviderAdapter) DeregisterRunner(ctx context.Context, runnerID string) error {
	// In GitLab, ephemeral runners self-unregister or are removed via DELETE /runners/:id
	endpoint := fmt.Sprintf("/runners/%s", runnerID)
	_, err := a.client.DoRequest(ctx, "DELETE", endpoint, nil, nil)
	return err
}
