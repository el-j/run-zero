package provider

import (
	"context"
	"time"

	"github.com/el-j/run-zero/pkg/state"
)

// ProviderType identifies the CI/CD platform engine.
type ProviderType string

const (
	// TypeGitHub identifies the GitHub Actions provider.
	TypeGitHub ProviderType = "github"
	// TypeGitLab identifies the GitLab CI provider.
	TypeGitLab ProviderType = "gitlab"
	// TypeGitea identifies the Gitea Actions provider.
	TypeGitea ProviderType = "gitea"
)

// RunnerOrigin categorizes the execution scope of a runner.
type RunnerOrigin string

const (
	// OriginLocalEphemeral identifies an on-demand local runner.
	OriginLocalEphemeral RunnerOrigin = "local"
	// OriginCloudHosted identifies a provider-hosted runner.
	OriginCloudHosted RunnerOrigin = "cloud"
	// OriginExternalStatic identifies a separately managed runner.
	OriginExternalStatic RunnerOrigin = "external"
)

// CIProvider defines operations required to monitor, discover, and scale runners across CI platforms.
type CIProvider interface {
	// ID returns the unique identifier for this provider instance (e.g. "github", "gitlab-eckelmann").
	ID() string

	// Name returns the human-readable display name.
	Name() string

	// Type returns the platform family (github, gitlab, etc.).
	Type() ProviderType

	// BaseURL returns the root API URL for this provider instance.
	BaseURL() string

	// FetchRemoteRunners retrieves all runners registered on this platform instance (both local and cloud/shared).
	FetchRemoteRunners(ctx context.Context) ([]state.RunnerInfo, error)

	// FetchQueuedJobs retrieves pending workflow jobs or pipeline builds awaiting a runner.
	FetchQueuedJobs(ctx context.Context) ([]state.QueuedJob, error)

	// AcquireRegistrationToken requests an ephemeral token to register an on-demand runner.
	AcquireRegistrationToken(ctx context.Context, scope string) (token string, expiresAt time.Time, err error)

	// DeregisterRunner removes a registered runner from the platform after job completion.
	DeregisterRunner(ctx context.Context, runnerID string) error
}
