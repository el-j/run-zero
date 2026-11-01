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
		return parseRepoList(reposConfig), nil
	}

	if !autoDiscover || c.token == "" {
		return []string{}, nil
	}

	target := strings.TrimSpace(org)
	if target == "" {
		target = strings.TrimSpace(owner)
	}
	endpoint := c.reposEndpoint(ctx, target)

	if activeDays <= 0 {
		activeDays = 60
	}
	cutoff := time.Now().UTC().AddDate(0, 0, -activeDays)

	seen := make(map[string]bool)
	var repos []string
	for page := 1; ; page++ {
		pageEndpoint := fmt.Sprintf("%s&per_page=100&page=%d", endpoint, page)
		var items []repositoryItem
		if _, err := c.DoRequest(ctx, "GET", pageEndpoint, nil, &items); err != nil {
			if len(repos) > 0 {
				break
			}
			return nil, fmt.Errorf("failed discovering repositories on page %d: %w", page, err)
		}

		var reachedCutoff bool
		repos, reachedCutoff = appendRecentRepos(repos, seen, items, target, cutoff)
		if reachedCutoff || len(items) < 100 {
			break
		}
	}

	sort.Strings(repos)
	return repos, nil
}

// parseRepoList turns a comma-separated repo list into a sorted, de-duplicated slice.
func parseRepoList(reposConfig string) []string {
	seen := make(map[string]bool)
	var result []string
	for _, p := range strings.Split(reposConfig, ",") {
		clean := strings.TrimSpace(p)
		if clean != "" && !seen[clean] {
			seen[clean] = true
			result = append(result, clean)
		}
	}
	sort.Strings(result)
	return result
}

// reposEndpoint lists an organization's repos when target is one, and the
// authenticated user's own repos otherwise.
func (c *Client) reposEndpoint(ctx context.Context, target string) string {
	if target != "" {
		var acc userAccountResponse
		if _, err := c.DoRequest(ctx, "GET", "/users/"+target, nil, &acc); err == nil && strings.EqualFold(acc.Type, "Organization") {
			return fmt.Sprintf("/orgs/%s/repos?type=all&sort=pushed&direction=desc", target)
		}
	}
	return "/user/repos?affiliation=owner&sort=pushed&direction=desc"
}

// appendRecentRepos adds the unarchived repos of one page (sorted by last push)
// owned by target. It reports true once it reaches a repo pushed before cutoff,
// since every later repo is older.
func appendRecentRepos(repos []string, seen map[string]bool, items []repositoryItem, target string, cutoff time.Time) ([]string, bool) {
	prefix := strings.ToLower(target) + "/"
	for _, item := range items {
		if item.Archived || (target != "" && !strings.HasPrefix(strings.ToLower(item.FullName), prefix)) {
			continue
		}
		if item.PushedAt != nil && *item.PushedAt != "" {
			if t, err := time.Parse(time.RFC3339, *item.PushedAt); err == nil && t.Before(cutoff) {
				return repos, true
			}
		}
		if !seen[item.FullName] {
			seen[item.FullName] = true
			repos = append(repos, item.FullName)
		}
	}
	return repos, false
}
