package github

import (
	"context"
	"fmt"
	"strings"

	"github.com/el-j/run-zero/pkg/state"
)

type registrationTokenResponse struct {
	Token     string `json:"token"`
	ExpiresAt string `json:"expires_at"`
}

// RunnerRegistration represents a runner registered with GitHub Actions API.
type RunnerRegistration struct {
	ID     int64    `json:"id"`
	Name   string   `json:"name"`
	OS     string   `json:"os,omitempty"`
	Status string   `json:"status"`
	Busy   bool     `json:"busy"`
	Labels []string `json:"labels,omitempty"`
	Scope  string   `json:"scope,omitempty"`
}

type actionsRunnersResponse struct {
	TotalCount int `json:"total_count"`
	Runners    []struct {
		ID     int64  `json:"id"`
		Name   string `json:"name"`
		OS     string `json:"os"`
		Status string `json:"status"`
		Busy   bool   `json:"busy"`
		Labels []struct {
			ID   int64  `json:"id"`
			Name string `json:"name"`
			Type string `json:"type"`
		} `json:"labels"`
	} `json:"runners"`
}

// CreateRegistrationToken generates a short-lived runner registration token.
func (c *Client) CreateRegistrationToken(ctx context.Context, repo, org string) (string, error) {
	var endpoint string
	if repo != "" {
		endpoint = fmt.Sprintf("/repos/%s/actions/runners/registration-token", repo)
	} else if org != "" {
		endpoint = fmt.Sprintf("/orgs/%s/actions/runners/registration-token", org)
	} else {
		return "", fmt.Errorf("must provide either repo or org to create registration token")
	}

	var resp registrationTokenResponse
	if _, err := c.DoRequest(ctx, "POST", endpoint, nil, &resp); err != nil {
		return "", fmt.Errorf("failed creating runner registration token: %w", err)
	}

	if resp.Token == "" {
		return "", fmt.Errorf("received empty registration token from GitHub")
	}
	return resp.Token, nil
}

// GetActionsBilling retrieves current GitHub Actions billing statistics.
func (c *Client) GetActionsBilling(ctx context.Context, owner, org string) (*state.ActionsBilling, error) {
	target := org
	endpoint := fmt.Sprintf("/orgs/%s/settings/billing/actions", target)
	if target == "" {
		target = owner
		endpoint = fmt.Sprintf("/users/%s/settings/billing/actions", target)
	}
	if target == "" {
		return nil, fmt.Errorf("must provide either owner or org to query actions billing")
	}

	var billing state.ActionsBilling
	if _, err := c.DoRequest(ctx, "GET", endpoint, nil, &billing); err != nil {
		return nil, fmt.Errorf("failed fetching actions billing: %w", err)
	}

	return &billing, nil
}

// ListRunners retrieves live runner registrations for a repository or organization.
func (c *Client) ListRunners(ctx context.Context, repo, org string) ([]RunnerRegistration, error) {
	var endpoint string
	var scope string
	if repo != "" {
		endpoint = fmt.Sprintf("/repos/%s/actions/runners?per_page=100", repo)
		scope = "repos/" + repo
	} else if org != "" {
		endpoint = fmt.Sprintf("/orgs/%s/actions/runners?per_page=100", org)
		scope = "orgs/" + org
	} else {
		return nil, fmt.Errorf("must provide either repo or org to list runners")
	}

	var resp actionsRunnersResponse
	if _, err := c.DoRequest(ctx, "GET", endpoint, nil, &resp); err != nil {
		return nil, fmt.Errorf("failed listing GitHub runners: %w", err)
	}

	results := make([]RunnerRegistration, len(resp.Runners))
	for i, r := range resp.Runners {
		labels := make([]string, len(r.Labels))
		for j, l := range r.Labels {
			labels[j] = l.Name
		}
		results[i] = RunnerRegistration{
			ID:     r.ID,
			Name:   r.Name,
			OS:     r.OS,
			Status: r.Status,
			Busy:   r.Busy,
			Labels: labels,
			Scope:  scope,
		}
	}
	return results, nil
}

// ConvertToRunnerInfo maps a GitHub RunnerRegistration to the unified RunZero RunnerInfo model.
func (c *Client) ConvertToRunnerInfo(r RunnerRegistration) state.RunnerInfo {
	providerName := "github"
	instanceHost := "github.com"

	origin := "external"
	isCloud := false
	nameLower := strings.ToLower(r.Name)

	if strings.HasPrefix(nameLower, "runzero-") {
		origin = "local"
		isCloud = false
	} else if strings.Contains(nameLower, "github actions") || strings.Contains(nameLower, "hosted") {
		origin = "cloud"
		isCloud = true
	} else {
		for _, lbl := range r.Labels {
			lblLower := strings.ToLower(lbl)
			if strings.Contains(lblLower, "ubuntu-latest") || strings.Contains(lblLower, "macos-") || strings.Contains(lblLower, "windows-") {
				origin = "cloud"
				isCloud = true
				break
			}
		}
	}

	status := r.Status
	if r.Busy {
		status = "busy"
	}

	stateVal := "active"
	if status == "offline" {
		stateVal = "offline"
	}

	backend := "cloud-hosted"
	if origin == "local" {
		backend = "docker"
	} else if origin == "external" {
		backend = "github-runner"
	}

	targetArch := "amd64"
	for _, lbl := range r.Labels {
		lblLower := strings.ToLower(lbl)
		if strings.Contains(lblLower, "arm64") || strings.Contains(lblLower, "aarch64") {
			targetArch = "arm64"
			break
		}
	}

	return state.RunnerInfo{
		ID:           fmt.Sprintf("gh-%d", r.ID),
		Name:         r.Name,
		Status:       status,
		State:        stateVal,
		TargetRepo:   r.Scope,
		TargetArch:   targetArch,
		Backend:      backend,
		Provider:     &providerName,
		ProviderInst: &instanceHost,
		Origin:       &origin,
		IsCloud:      isCloud,
		Tags:         r.Labels,
	}
}

// DeleteRunner removes a registered runner from a repository or organization.
func (c *Client) DeleteRunner(ctx context.Context, repo, org string, runnerID int64) error {
	var endpoint string
	if repo != "" {
		endpoint = fmt.Sprintf("/repos/%s/actions/runners/%d", repo, runnerID)
	} else if org != "" {
		endpoint = fmt.Sprintf("/orgs/%s/actions/runners/%d", org, runnerID)
	} else {
		return fmt.Errorf("must provide either repo or org to delete runner")
	}

	_, err := c.DoRequest(ctx, "DELETE", endpoint, nil, nil)
	return err
}
