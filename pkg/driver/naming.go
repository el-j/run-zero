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
	prefix := fmt.Sprintf("runzero-j%d-r%d-%s-", jobID, runID, archToken)
	return prefix + fitRepoPart(repoPart, len(prefix)+1+len(entropyPart)) + "-" + entropyPart
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
	prefix := fmt.Sprintf("runzero-manual-%s-", archToken)
	return prefix + fitRepoPart(repoPart, len(prefix)+1+len(entropyPart)) + "-" + entropyPart
}

// maxRunnerNameLen is GitHub's limit for a self-hosted runner name.
const maxRunnerNameLen = 64

// fitRepoPart trims the owner/repo token so the whole runner name stays within
// maxRunnerNameLen, given the length of everything else in the name.
func fitRepoPart(repoPart string, otherLen int) string {
	allowed := maxRunnerNameLen - otherLen
	if allowed < 8 {
		allowed = 8
	}
	if len(repoPart) <= allowed {
		return repoPart
	}
	return strings.Trim(repoPart[:allowed], "-_.")
}
