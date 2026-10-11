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

	etagMu sync.Mutex
	etags  map[string]cachedResponse
}

// cachedResponse is a GET response remembered for ETag revalidation. GitHub does
// not count 304 Not Modified responses against the primary rate limit.
type cachedResponse struct {
	etag string
	body []byte
}

// maxETagEntries bounds the revalidation cache; it is reset when exceeded.
const maxETagEntries = 4000

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
		etags:      make(map[string]cachedResponse),
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

	cacheable := method == http.MethodGet && body == nil && out != nil
	if rl := c.RateLimit(); rl.Limit > 0 && rl.Remaining <= 0 && time.Now().Before(rl.Reset) {
		// Quota exhausted: do not hammer GitHub (and extend the lockout) until reset.
		return nil, fmt.Errorf("github api rate limit exhausted until %s", rl.Reset.Format(time.RFC3339))
	}

	req, err := http.NewRequestWithContext(ctx, method, url, body)
	if err != nil {
		return nil, err
	}
	if cacheable {
		c.etagMu.Lock()
		cached, ok := c.etags[url]
		c.etagMu.Unlock()
		if ok {
			req.Header.Set("If-None-Match", cached.etag)
		}
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

	if cacheable && resp.StatusCode == http.StatusNotModified {
		c.etagMu.Lock()
		cached, ok := c.etags[url]
		c.etagMu.Unlock()
		if ok {
			if err := json.Unmarshal(cached.body, out); err != nil {
				return resp, fmt.Errorf("failed decoding cached response: %w", err)
			}
			return resp, nil
		}
	}

	if resp.StatusCode < 200 || resp.StatusCode >= 300 {
		respBody, _ := io.ReadAll(resp.Body)
		return resp, fmt.Errorf("github api error (%d): %s", resp.StatusCode, string(respBody))
	}

	if out != nil {
		raw, err := io.ReadAll(resp.Body)
		if err != nil {
			return resp, fmt.Errorf("failed reading response: %w", err)
		}
		if err := json.Unmarshal(raw, out); err != nil {
			return resp, fmt.Errorf("failed decoding response: %w", err)
		}
		if etag := resp.Header.Get("ETag"); cacheable && etag != "" {
			c.etagMu.Lock()
			if len(c.etags) >= maxETagEntries {
				c.etags = make(map[string]cachedResponse)
			}
			c.etags[url] = cachedResponse{etag: etag, body: raw}
			c.etagMu.Unlock()
		}
	}

	return resp, nil
}
