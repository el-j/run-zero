package github

import (
	"context"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"strconv"
	"strings"
	"sync"
	"time"
)

// RateLimit holds GitHub API rate limit status.
type RateLimit struct {
	Remaining int
	Limit     int
	Reset     time.Time
}

// Client interacts with the GitHub REST API.
type Client struct {
	baseURL    string
	token      string
	httpClient *http.Client
	mu         sync.RWMutex
	rateLimit  RateLimit
}

// NewClient creates an authenticated GitHub API client.
func NewClient(token string, baseURL string, httpClient *http.Client) *Client {
	if httpClient == nil {
		httpClient = &http.Client{Timeout: 15 * time.Second}
	}
	if baseURL == "" {
		baseURL = "https://api.github.com"
	}
	return &Client{
		baseURL:    strings.TrimSuffix(baseURL, "/"),
		token:      strings.TrimSpace(token),
		httpClient: httpClient,
	}
}

// RateLimit returns the last observed rate limit counters.
func (c *Client) RateLimit() RateLimit {
	c.mu.RLock()
	defer c.mu.RUnlock()
	return c.rateLimit
}

func (c *Client) updateRateLimit(header http.Header) {
	remStr := header.Get("X-RateLimit-Remaining")
	limStr := header.Get("X-RateLimit-Limit")
	resetStr := header.Get("X-RateLimit-Reset")

	if remStr == "" || limStr == "" {
		return
	}

	rem, err1 := strconv.Atoi(remStr)
	lim, err2 := strconv.Atoi(limStr)
	resetUnix, _ := strconv.ParseInt(resetStr, 10, 64)

	if err1 == nil && err2 == nil {
		c.mu.Lock()
		c.rateLimit = RateLimit{
			Remaining: rem,
			Limit:     lim,
			Reset:     time.Unix(resetUnix, 0).UTC(),
		}
		c.mu.Unlock()
	}
}

// DoRequest performs an authenticated HTTP request against GitHub REST API and parses JSON response.
func (c *Client) DoRequest(ctx context.Context, method, endpoint string, body io.Reader, out interface{}) (*http.Response, error) {
	url := endpoint
	if !strings.HasPrefix(url, "http://") && !strings.HasPrefix(url, "https://") {
		url = c.baseURL + "/" + strings.TrimPrefix(endpoint, "/")
	}

	req, err := http.NewRequestWithContext(ctx, method, url, body)
	if err != nil {
		return nil, err
	}

	req.Header.Set("Accept", "application/vnd.github+json")
	req.Header.Set("X-GitHub-Api-Version", "2022-11-28")
	if c.token != "" {
		req.Header.Set("Authorization", "Bearer "+c.token)
	}
	if body != nil {
		req.Header.Set("Content-Type", "application/json")
	}

	resp, err := c.httpClient.Do(req)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	c.updateRateLimit(resp.Header)

	if resp.StatusCode < 200 || resp.StatusCode >= 300 {
		respBody, _ := io.ReadAll(resp.Body)
		return resp, fmt.Errorf("github api error (%d): %s", resp.StatusCode, string(respBody))
	}

	if out != nil {
		if err := json.NewDecoder(resp.Body).Decode(out); err != nil {
			return resp, fmt.Errorf("failed decoding response: %w", err)
		}
	}

	return resp, nil
}
