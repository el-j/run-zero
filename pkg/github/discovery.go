package github

import (
	"context"
	"fmt"
	"sort"
	"strings"
	"time"
)

type userAccountResponse struct {
	Type string `json:"type"`
}

type repositoryItem struct {
	FullName string  `json:"full_name"`
	Archived bool    `json:"archived"`
	PushedAt *string `json:"pushed_at"`
}

// DiscoverRepositories retrieves the active repositories for the given owner or reposConfig list.
func (c *Client) DiscoverRepositories(
	ctx context.Context,
	owner, org string,
	activeDays int,
	autoDiscover bool,
	reposConfig string,
) ([]string, error) {
	// If explicit repos configured, use them
	if strings.TrimSpace(reposConfig) != "" {
		parts := strings.Split(reposConfig, ",")
		seen := make(map[string]bool)
		var result []string
		for _, p := range parts {
			clean := strings.TrimSpace(p)
			if clean != "" && !seen[clean] {
				seen[clean] = true
				result = append(result, clean)
			}
		}
		sort.Strings(result)
		return result, nil
	}

	if !autoDiscover || c.token == "" {
		return []string{}, nil
	}

	target := strings.TrimSpace(org)
	if target == "" {
		target = strings.TrimSpace(owner)
	}

	endpoint := "/user/repos?affiliation=owner&sort=pushed&direction=desc"
	if target != "" {
		var acc userAccountResponse
		if _, err := c.DoRequest(ctx, "GET", "/users/"+target, nil, &acc); err == nil {
			if strings.EqualFold(acc.Type, "Organization") {
				endpoint = fmt.Sprintf("/orgs/%s/repos?type=all&sort=pushed&direction=desc", target)
			}
		}
	}

	if activeDays <= 0 {
		activeDays = 60
	}
	cutoff := time.Now().UTC().AddDate(0, 0, -activeDays)

	seen := make(map[string]bool)
	var repos []string

	page := 1
	for {
		pageEndpoint := fmt.Sprintf("%s&per_page=100&page=%d", endpoint, page)
		var items []repositoryItem
		if _, err := c.DoRequest(ctx, "GET", pageEndpoint, nil, &items); err != nil {
			if len(repos) > 0 {
				break
			}
			return nil, fmt.Errorf("failed discovering repositories on page %d: %w", page, err)
		}

		if len(items) == 0 {
			break
		}

		stopPagination := false
		for _, item := range items {
			if item.Archived {
				continue
			}

			if target != "" && !strings.HasPrefix(strings.ToLower(item.FullName), strings.ToLower(target)+"/") {
				continue
			}

			if item.PushedAt != nil && *item.PushedAt != "" {
				t, err := time.Parse(time.RFC3339, *item.PushedAt)
				if err == nil && t.Before(cutoff) {
					stopPagination = true
					break
				}
			}

			if !seen[item.FullName] {
				seen[item.FullName] = true
				repos = append(repos, item.FullName)
			}
		}

		if stopPagination || len(items) < 100 {
			break
		}
		page++
	}

	sort.Strings(repos)
	return repos, nil
}
