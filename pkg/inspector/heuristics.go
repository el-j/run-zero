package inspector

import (
	"regexp"
	"sort"
	"strings"
)

var vmTriggerSet = map[string]bool{
	"vm":          true,
	"orbstack":    true,
	"wsl":         true,
	"multipass":   true,
	"e2e":         true,
	"browser":     true,
	"chrome":      true,
	"lighthouse":  true,
	"systemd":     true,
	"postgres":    true,
	"mysql":       true,
	"redis":       true,
	"db":          true,
	"database":    true,
	"service":     true,
	"services":    true,
	"integration": true,
	"dind":        true,
}

var tokenRegex = regexp.MustCompile(`[a-z0-9]+`)

// JobNeedsVM determines if a job requires a VM based on AST services declaration, labels, or name.
func JobNeedsVM(labels []string, jobName string, declaresServices *bool) (bool, string) {
	if declaresServices != nil && *declaresServices {
		return true, "services"
	}

	for _, label := range labels {
		l := strings.ToLower(strings.TrimSpace(label))
		if vmTriggerSet[l] {
			return true, "label:" + l
		}
	}

	nameLower := strings.ToLower(jobName)
	tokens := tokenRegex.FindAllString(nameLower, -1)
	var matchedTokens []string
	for _, tok := range tokens {
		if vmTriggerSet[tok] {
			matchedTokens = append(matchedTokens, tok)
		}
	}

	if len(matchedTokens) > 0 {
		sort.Strings(matchedTokens)
		return true, "name:" + matchedTokens[0]
	}

	return false, "container"
}
