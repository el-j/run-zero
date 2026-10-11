package driver

import (
	"fmt"
	"strings"
)

func sanitizeNamePart(value string) string {
	value = strings.ToLower(strings.TrimSpace(value))
	if value == "" {
		return ""
	}
	var b strings.Builder
	lastDash := false
	for _, r := range value {
		isAlphaNum := (r >= 'a' && r <= 'z') || (r >= '0' && r <= '9')
		if isAlphaNum || r == '-' || r == '_' || r == '.' {
			b.WriteRune(r)
			lastDash = false
			continue
		}
		if !lastDash {
			b.WriteByte('-')
			lastDash = true
		}
	}
	out := strings.Trim(b.String(), "-")
	if out == "" {
		return "unknown"
	}
	return out
}

func repoToken(repo string) string {
	parts := strings.SplitN(strings.TrimSpace(repo), "/", 2)
	if len(parts) == 2 {
		owner := sanitizeNamePart(parts[0])
		name := sanitizeNamePart(parts[1])
		return fmt.Sprintf("%s__%s", owner, name)
	}
	return sanitizeNamePart(repo)
}

func parseRepoToken(token string) string {
	parts := strings.SplitN(token, "__", 2)
	if len(parts) == 2 && parts[0] != "" && parts[1] != "" {
		return fmt.Sprintf("%s/%s", parts[0], parts[1])
	}
	return token
}

// JobScopedRunnerName builds a deterministic, job-correlated runner name.
func JobScopedRunnerName(repo, arch string, runID, jobID int64, entropy string) string {
	archToken := sanitizeNamePart(arch)
	if archToken == "" || archToken == "unknown" {
		archToken = "amd64"
	}
	repoPart := repoToken(repo)
	entropyPart := sanitizeNamePart(entropy)
	if entropyPart == "" || entropyPart == "unknown" {
		entropyPart = "rand"
	}
	name := fmt.Sprintf("runzero-j%d-r%d-%s-%s-%s", jobID, runID, archToken, repoPart, entropyPart)
	if len(name) <= 120 {
		return name
	}
	trimmedRepo := repoPart
	if len(trimmedRepo) > 32 {
		trimmedRepo = trimmedRepo[:32]
		trimmedRepo = strings.Trim(trimmedRepo, "-")
	}
	return fmt.Sprintf("runzero-j%d-r%d-%s-%s-%s", jobID, runID, archToken, trimmedRepo, entropyPart)
}

// ManualRunnerName builds a clear manually-started runner name.
func ManualRunnerName(repo, arch, entropy string) string {
	archToken := sanitizeNamePart(arch)
	if archToken == "" || archToken == "unknown" {
		archToken = "amd64"
	}
	repoPart := repoToken(repo)
	entropyPart := sanitizeNamePart(entropy)
	if entropyPart == "" || entropyPart == "unknown" {
		entropyPart = "rand"
	}
	name := fmt.Sprintf("runzero-manual-%s-%s-%s", archToken, repoPart, entropyPart)
	if len(name) <= 120 {
		return name
	}
	trimmedRepo := repoPart
	if len(trimmedRepo) > 40 {
		trimmedRepo = trimmedRepo[:40]
		trimmedRepo = strings.Trim(trimmedRepo, "-")
	}
	return fmt.Sprintf("runzero-manual-%s-%s-%s", archToken, trimmedRepo, entropyPart)
}
