package driver

import (
	"fmt"
	"strconv"
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

// jobScopedName holds the fields encoded in a job-scoped runner name.
type jobScopedName struct {
	jobID, runID   *int64
	arch, repo, id string
}

// parseJobScopedName decodes runzero-j<jobID>-r<runID>-<arch>-<owner__repo>-<id>.
func parseJobScopedName(name string) (jobScopedName, bool) {
	trimmed, ok := strings.CutPrefix(name, "runzero-")
	tokens := strings.Split(trimmed, "-")
	if !ok || len(tokens) < 5 || !strings.HasPrefix(tokens[0], "j") || !strings.HasPrefix(tokens[1], "r") {
		return jobScopedName{}, false
	}
	return jobScopedName{
		jobID: parseIDPtr(tokens[0][1:]),
		runID: parseIDPtr(tokens[1][1:]),
		arch:  tokens[2],
		repo:  parseRepoToken(strings.Join(tokens[3:len(tokens)-1], "-")),
		id:    tokens[len(tokens)-1],
	}, true
}

func parseIDPtr(s string) *int64 {
	if v, err := strconv.ParseInt(s, 10, 64); err == nil {
		return &v
	}
	return nil
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

// ResolveRepoFromMachineName maps a runner name whose repo token is lossy (OrbStack
// machine names must be hostnames, so "el-j__landing.inquam-services" becomes
// "el-j-landing-in") back to the "owner/repo" in repos whose spawn-time name
// reproduces it exactly. It returns "" when no repo matches.
func ResolveRepoFromMachineName(name string, repos []string) string {
	tokens := strings.Split(strings.TrimPrefix(name, "runzero-"), "-")
	if len(tokens) < 4 || !strings.HasPrefix(name, "runzero-") {
		return ""
	}
	entropy := tokens[len(tokens)-1]
	var build func(repo string) string
	if tokens[0] == "manual" {
		build = func(repo string) string { return ManualRunnerName(repo, tokens[1], entropy) }
	} else if len(tokens) >= 5 && strings.HasPrefix(tokens[0], "j") && strings.HasPrefix(tokens[1], "r") {
		jobID, errJ := strconv.ParseInt(tokens[0][1:], 10, 64)
		runID, errR := strconv.ParseInt(tokens[1][1:], 10, 64)
		if errJ != nil || errR != nil {
			return ""
		}
		build = func(repo string) string { return JobScopedRunnerName(repo, tokens[2], runID, jobID, entropy) }
	} else {
		return ""
	}
	for _, repo := range repos {
		candidate := build(repo)
		if candidate == name || orbstackMachineName(candidate) == name {
			return repo
		}
	}
	return ""
}
