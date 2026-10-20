package gitlab

import (
	"context"
	"fmt"
	"net/url"
	"strings"

	"github.com/el-j/run-zero/pkg/state"
)

// GitLabRunner represents a runner entry returned by GitLab API v4.
type GitLabRunner struct {
	ID          int64    `json:"id"`
	Description string   `json:"description"`
	Active      bool     `json:"active"`
	Paused      bool     `json:"paused"`
	IsShared    bool     `json:"is_shared"`
	RunnerType  string   `json:"runner_type"` // instance_type, group_type, project_type
	Name        string   `json:"name"`
	Online      bool     `json:"online"`
	Status      string   `json:"status"` // online, offline, paused, not_connected
	TagList     []string `json:"tag_list"`
	IPAddress   string   `json:"ip_address,omitempty"`
}

// ListRunners retrieves all runners accessible to the token (instance-wide or all user runners).
func (c *Client) ListRunners(ctx context.Context) ([]GitLabRunner, error) {
	var runners []GitLabRunner
	// Request active and paused runners
	endpoint := "/runners?per_page=100"
	_, err := c.DoRequest(ctx, "GET", endpoint, nil, &runners)
	if err != nil {
		return nil, err
	}
	return runners, nil
}

// ListGroupRunners retrieves runners registered under a specific group.
func (c *Client) ListGroupRunners(ctx context.Context, groupID string) ([]GitLabRunner, error) {
	var runners []GitLabRunner
	endpoint := fmt.Sprintf("/groups/%s/runners?per_page=100", url.PathEscape(groupID))
	_, err := c.DoRequest(ctx, "GET", endpoint, nil, &runners)
	if err != nil {
		return nil, err
	}
	return runners, nil
}

// ConvertToRunnerInfo maps a GitLab runner to the unified RunZero RunnerInfo model.
func (c *Client) ConvertToRunnerInfo(r GitLabRunner) state.RunnerInfo {
	providerName := "gitlab"
	instanceHost := "gitlab.com"
	if u, err := url.Parse(c.baseURL); err == nil && u.Host != "" {
		instanceHost = u.Host
	}

	name := r.Description
	if name == "" {
		name = r.Name
	}
	if name == "" {
		name = fmt.Sprintf("gitlab-runner-%d", r.ID)
	}

	// Classify origin:
	// - Cloud: Shared / instance-level runners provided by SaaS or instance admins
	// - Local: Ephemeral runners spawned by RunZero on this host (prefixed with runzero-)
	// - External: Project/group specific static self-hosted runners
	origin := "external"
	isCloud := false
	if r.IsShared || r.RunnerType == "instance_type" {
		origin = "cloud"
		isCloud = true
	} else if strings.HasPrefix(strings.ToLower(name), "runzero-") {
		origin = "local"
		isCloud = false
	}

	status := r.Status
	if status == "" {
		if r.Online {
			status = "online"
		} else {
			status = "offline"
		}
	}
	if r.Paused {
		status = "paused"
	}

	stateVal := "active"
	if r.Paused || !r.Active {
		stateVal = "paused"
	}

	backend := "cloud-hosted"
	if origin == "local" {
		backend = "docker"
	} else if origin == "external" {
		backend = "gitlab-runner"
	}

	targetArch := "amd64"
	for _, tag := range r.TagList {
		tagLower := strings.ToLower(tag)
		if strings.Contains(tagLower, "arm64") || strings.Contains(tagLower, "aarch64") {
			targetArch = "arm64"
			break
		}
	}

	return state.RunnerInfo{
		ID:           fmt.Sprintf("gl-%d", r.ID),
		Name:         name,
		Status:       status,
		State:        stateVal,
		TargetRepo:   instanceHost,
		TargetArch:   targetArch,
		Backend:      backend,
		Provider:     &providerName,
		ProviderInst: &instanceHost,
		Origin:       &origin,
		IsCloud:      isCloud,
		Tags:         r.TagList,
	}
}
