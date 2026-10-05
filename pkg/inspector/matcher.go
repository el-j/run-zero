package inspector

import "strings"

func jobMatchesTarget(target string, jobID string, jobName string) bool {
	targetTrimmed := strings.TrimSpace(target)
	targetBase := MatrixBase(targetTrimmed)

	candidates := []string{jobID}
	if jobName != "" {
		candidates = append(candidates, jobName)
	}

	for _, cand := range candidates {
		candTrimmed := strings.TrimSpace(cand)
		candBase := MatrixBase(candTrimmed)

		if targetTrimmed == candTrimmed || targetBase == candTrimmed || targetBase == candBase {
			return true
		}
	}
	return false
}

// JobUsesServicesOrContainer checks whether the specified job declares services: or container:.
// Returns nil if the job cannot be found in the workflow text.
func JobUsesServicesOrContainer(workflowText string, targetJobName string) *bool {
	if strings.TrimSpace(workflowText) == "" || strings.TrimSpace(targetJobName) == "" {
		return nil
	}

	jobs := ParseWorkflowJobs(workflowText)
	if len(jobs) == 0 {
		return nil
	}

	for _, j := range jobs {
		if jobMatchesTarget(targetJobName, j.JobID, j.JobName) {
			val := j.HasServices
			return &val
		}
	}

	return nil
}
