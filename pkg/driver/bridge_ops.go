package driver

import (
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"net/http"

	"github.com/el-j/run-zero/pkg/state"
)

// ListRunners queries GET /api/drivers/{backend}/runners on the bridge.
func (b *BridgeDriver) ListRunners(ctx context.Context) ([]state.RunnerInfo, error) {
	url := fmt.Sprintf("%s/api/drivers/%s/runners", b.baseURL, b.backend)
	req, err := http.NewRequestWithContext(ctx, http.MethodGet, url, nil)
	if err != nil {
		return nil, err
	}
	if b.token != "" {
		req.Header.Set("Authorization", "Bearer "+b.token)
	}

	resp, err := b.client.Do(req)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	var res struct {
		Runners []state.RunnerInfo `json:"runners"`
		Error   string             `json:"error"`
	}
	if err := json.NewDecoder(resp.Body).Decode(&res); err != nil {
		return nil, err
	}
	return res.Runners, nil
}

// StopRunner calls POST /api/drivers/{backend}/stop on the bridge.
func (b *BridgeDriver) StopRunner(ctx context.Context, runnerID string) error {
	url := fmt.Sprintf("%s/api/drivers/%s/stop", b.baseURL, b.backend)
	body, _ := json.Marshal(map[string]string{"runner_id": runnerID})
	req, err := http.NewRequestWithContext(ctx, http.MethodPost, url, bytes.NewReader(body))
	if err != nil {
		return err
	}
	req.Header.Set("Content-Type", "application/json")
	if b.token != "" {
		req.Header.Set("Authorization", "Bearer "+b.token)
	}

	resp, err := b.client.Do(req)
	if err != nil {
		return err
	}
	defer resp.Body.Close()
	return nil
}

// CleanupAll calls POST /api/drivers/{backend}/cleanup on the bridge.
func (b *BridgeDriver) CleanupAll(ctx context.Context) error {
	url := fmt.Sprintf("%s/api/drivers/%s/cleanup", b.baseURL, b.backend)
	req, err := http.NewRequestWithContext(ctx, http.MethodPost, url, nil)
	if err != nil {
		return err
	}
	if b.token != "" {
		req.Header.Set("Authorization", "Bearer "+b.token)
	}
	resp, err := b.client.Do(req)
	if err != nil {
		return err
	}
	defer resp.Body.Close()
	return nil
}
