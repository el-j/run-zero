package gitlab

import (
	"context"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"strings"
	"sync"
	"time"
)

// Client interacts with the GitLab REST API v4.
type Client struct {
	baseURL    string
	token      string
	httpClient *http.Client
	mu         sync.RWMutex
}

// NewClient creates an authenticated GitLab API client.
func NewClient(token string, baseURL string, httpClient *http.Client) *Client {
	if httpClient == nil {
		httpClient = &http.Client{Timeout: 15 * time.Second}
	}
	if baseURL == "" {
		baseURL = "https://gitlab.com"
	}
	baseURL = strings.TrimSuffix(baseURL, "/")
	if !strings.HasSuffix(baseURL, "/api/v4") {
		baseURL = baseURL + "/api/v4"
	}
	return &Client{
		baseURL:    baseURL,
		token:      strings.TrimSpace(token),
		httpClient: httpClient,
	}
}

// BaseURL returns the configured API root endpoint.
func (c *Client) BaseURL() string {
	return c.baseURL
}

// DoRequest performs an authenticated HTTP request against the GitLab REST API and parses JSON response.
func (c *Client) DoRequest(ctx context.Context, method, endpoint string, body io.Reader, out interface{}) (*http.Response, error) {
	url := endpoint
	if !strings.HasPrefix(url, "http://") && !strings.HasPrefix(url, "https://") {
		url = c.baseURL + "/" + strings.TrimPrefix(endpoint, "/")
	}

	req, err := http.NewRequestWithContext(ctx, method, url, body)
	if err != nil {
		return nil, fmt.Errorf("create request failed: %w", err)
	}

	if c.token != "" {
		req.Header.Set("PRIVATE-TOKEN", c.token)
	}
	req.Header.Set("Accept", "application/json")
	if body != nil {
		req.Header.Set("Content-Type", "application/json")
	}

	resp, err := c.httpClient.Do(req)
	if err != nil {
		return nil, fmt.Errorf("http request failed: %w", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode >= 400 {
		respBytes, _ := io.ReadAll(resp.Body)
		return resp, fmt.Errorf("gitlab api error HTTP %d: %s", resp.StatusCode, string(respBytes))
	}

	if out != nil && resp.StatusCode != http.StatusNoContent {
		respBytes, err := io.ReadAll(resp.Body)
		if err != nil {
			return resp, fmt.Errorf("read response failed: %w", err)
		}
		if err := json.Unmarshal(respBytes, out); err != nil {
			return resp, fmt.Errorf("parse json failed: %w", err)
		}
	}

	return resp, nil
}
