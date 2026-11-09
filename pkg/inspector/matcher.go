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

// JobVMReason says why the job named target needs a VM (one of the Reason
// constants, "" when a container runner will do) and whether the job was
// found in the workflow at all.
func JobVMReason(workflowText string, target string) (reason string, found bool) {
	if strings.TrimSpace(target) == "" {
		return "", false
	}
	for _, j := range ParseWorkflowJobs(workflowText) {
		if jobMatchesTarget(target, j.JobID, j.JobName) {
			return j.VMReason, true
		}
	}
	return "", false
}
