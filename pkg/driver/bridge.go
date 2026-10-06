package driver

import (
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"net/http"
	"strings"
	"time"

	"github.com/el-j/run-zero/pkg/state"
)

// BridgeDriver proxies runner lifecycle requests over HTTP to the Host VM Bridge.
type BridgeDriver struct {
	baseURL string
	backend string
	token   string
	client  *http.Client
}

// NewBridgeDriver creates a client that calls the Host VM Bridge server.
func NewBridgeDriver(baseURL, backend, token string, client *http.Client) *BridgeDriver {
	if baseURL == "" {
		baseURL = "http://host.docker.internal:49504"
	}
	if backend == "" {
		backend = "orbstack"
	}
	if client == nil {
		client = &http.Client{Timeout: 60 * time.Second}
	}
	return &BridgeDriver{
		baseURL: strings.TrimSuffix(baseURL, "/"),
		backend: strings.ToLower(strings.TrimSpace(backend)),
		token:   token,
		client:  client,
	}
}

// Backend returns the target backend name.
func (b *BridgeDriver) Backend() string {
	return b.backend
}

// SpawnRunner invokes POST /api/drivers/{backend}/spawn on the bridge.
func (b *BridgeDriver) SpawnRunner(ctx context.Context, spec RunnerSpec) (*state.RunnerInfo, error) {
	url := fmt.Sprintf("%s/api/drivers/%s/spawn", b.baseURL, b.backend)
	payload := map[string]any{
		"repo":         spec.Repo,
		"arch":         spec.Arch,
		"labels":       strings.Join(spec.Labels, ","),
		"runner_token": spec.Token,
		"name":         spec.Name,
		"extra_env":    spec.Env,
	}
	body, err := json.Marshal(payload)
	if err != nil {
		return nil, err
	}

	req, err := http.NewRequestWithContext(ctx, http.MethodPost, url, bytes.NewReader(body))
	if err != nil {
		return nil, err
	}
	req.Header.Set("Content-Type", "application/json")
	if b.token != "" {
		req.Header.Set("Authorization", "Bearer "+b.token)
	}

	resp, err := b.client.Do(req)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		return nil, fmt.Errorf("bridge spawn returned status %d", resp.StatusCode)
	}

	var res struct {
		RunnerID string `json:"runner_id"`
		Error    string `json:"error"`
	}
	if err := json.NewDecoder(resp.Body).Decode(&res); err != nil {
		return nil, err
	}
	if res.Error != "" {
		return nil, fmt.Errorf("bridge spawn error: %s", res.Error)
	}

	now := time.Now().UTC().Format(time.RFC3339)
	return &state.RunnerInfo{
		ID:         res.RunnerID,
		Name:       spec.Name,
		Status:     "running",
		State:      "running",
		TargetRepo: spec.Repo,
		TargetArch: spec.Arch,
		Backend:    b.backend,
		CreatedAt:  &now,
	}, nil
}
