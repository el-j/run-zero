package inspector

import (
	"strings"
)

// JobInfo holds parsed metadata from a workflow job block.
type JobInfo struct {
	JobID       string
	JobName     string
	HasServices bool
	RunsOn      []string
}

// MatrixBase strips matrix parameter suffixes like "Test (1, 2)" -> "Test".
func MatrixBase(name string) string {
	idx := strings.Index(name, " (")
	if idx >= 0 {
		return strings.TrimSpace(name[:idx])
	}
	return strings.TrimSpace(name)
}

func unquote(val string) string {
	s := strings.TrimSpace(val)
	if len(s) >= 2 {
		if (s[0] == '\'' && s[len(s)-1] == '\'') || (s[0] == '"' && s[len(s)-1] == '"') {
			return s[1 : len(s)-1]
		}
	}
	return s
}

func countLeadingSpaces(s string) int {
	return len(s) - len(strings.TrimLeft(s, " "))
}

// ParseWorkflowJobs parses top-level jobs from GitHub Actions YAML text.
func ParseWorkflowJobs(workflowText string) []JobInfo {
	lines := strings.Split(workflowText, "\n")
	jobsIdx := -1
	jobsIndent := 0

	for i, line := range lines {
		trimmed := strings.TrimSpace(line)
		if strings.HasPrefix(trimmed, "jobs:") {
			jobsIdx = i
			jobsIndent = countLeadingSpaces(line)
			break
		}
	}
	if jobsIdx == -1 {
		return nil
	}

	var jobs []JobInfo
	childIndent := jobsIndent + 2
	i := jobsIdx + 1

	for i < len(lines) {
		line := lines[i]
		trimmed := strings.TrimSpace(line)
		if trimmed == "" || strings.HasPrefix(trimmed, "#") {
			i++
			continue
		}
		if countLeadingSpaces(line) <= jobsIndent {
			break
		}
		if countLeadingSpaces(line) != childIndent || strings.HasPrefix(trimmed, "-") || !strings.HasSuffix(trimmed, ":") {
			i++
			continue
		}

		jobKey := strings.TrimSuffix(trimmed, ":")
		if strings.Contains(jobKey, " ") {
			i++
			continue
		}

		info, nextIdx := parseJobBlock(lines, i+1, childIndent)
		info.JobID = jobKey
		jobs = append(jobs, info)
		i = nextIdx
	}

	return jobs
}

func parseJobBlock(lines []string, startIdx, parentIndent int) (JobInfo, int) {
	var info JobInfo
	j := startIdx

	for j < len(lines) {
		line := lines[j]
		trimmed := strings.TrimSpace(line)
		if trimmed != "" && !strings.HasPrefix(trimmed, "#") && countLeadingSpaces(line) <= parentIndent {
			break
		}
		if countLeadingSpaces(line) == parentIndent+2 {
			if strings.HasPrefix(trimmed, "name:") {
				info.JobName = unquote(strings.TrimPrefix(trimmed, "name:"))
			} else if strings.HasPrefix(trimmed, "services:") || strings.HasPrefix(trimmed, "container:") {
				info.HasServices = true
			}
		}
		j++
	}
	return info, j
}
