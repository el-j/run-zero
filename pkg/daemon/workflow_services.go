package daemon

import (
	"context"
	"fmt"

	"github.com/el-j/run-zero/pkg/inspector"
	"github.com/el-j/run-zero/pkg/scheduling"
	"github.com/el-j/run-zero/pkg/state"
)

// maxCachedWorkflows bounds the workflow-file cache; it is cleared when full.
const maxCachedWorkflows = 500

// resolveJobBackend picks docker or orbstack for a job of repo. Labels and
// names decide first; a job they leave in a container is still routed to a VM
// when its workflow gives it services: or a container:, which need a VM's
// Docker daemon.
func (s *Scaler) resolveJobBackend(ctx context.Context, repo string, job state.QueuedJob) string {
	p := s.policy()
	sj := schedJob(job, repo)
	backend, _ := scheduling.Backend(p, sj)
	if backend != "docker" || !p.AutoRouteVM || (p.Backend != "" && p.Backend != "auto") || job.ID == 0 {
		return backend
	}
	if sj.DeclaresServices = s.jobDeclaresServices(ctx, repo, job); sj.DeclaresServices {
		backend, _ = scheduling.Backend(p, sj)
		s.state.AppendLog(fmt.Sprintf("[Autoscaler] 🧭 Routing %s job '%s' to a VM: its workflow declares services or a container", repo, job.Name))
	}
	return backend
}

// jobDeclaresServices reports whether job's workflow file (at the run's
// commit) gives the job services: or a container:. Each workflow version is
// fetched once; a fetch error counts as "no" and is retried on the next spawn.
func (s *Scaler) jobDeclaresServices(ctx context.Context, repo string, job state.QueuedJob) bool {
	if job.WorkflowPath == "" || job.HeadSHA == "" || s.ghClient == nil {
		return false
	}
	if s.workflows == nil {
		s.workflows = inspector.NewWorkflowCache()
	}
	key := repo + "@" + job.HeadSHA + ":" + job.WorkflowPath
	resultKey := key + "#" + job.Name
	if res, ok := s.workflows.GetJobResult(resultKey); ok {
		return res != nil && *res
	}
	text, ok := s.workflows.GetWorkflow(key)
	if !ok {
		var err error
		if text, err = s.ghClient.GetWorkflowFile(ctx, repo, job.WorkflowPath, job.HeadSHA); err != nil {
			return false
		}
		if s.cachedWorkflows >= maxCachedWorkflows {
			s.workflows.Clear()
			s.cachedWorkflows = 0
		}
		s.workflows.SetWorkflow(key, text)
		s.cachedWorkflows++
	}
	res := inspector.JobUsesServicesOrContainer(text, job.Name)
	s.workflows.SetJobResult(resultKey, res)
	return res != nil && *res
}
