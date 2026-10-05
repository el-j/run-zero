package github

import (
	"fmt"
	"sort"
	"strings"

	"github.com/el-j/run-zero/pkg/state"
)

// Reconciler computes priority-weighted runner slot allocations and queue positions.
type Reconciler struct {
	pm *PriorityManager
}

// NewReconciler creates a scheduler reconciler using the given PriorityManager.
func NewReconciler(pm *PriorityManager) *Reconciler {
	return &Reconciler{pm: pm}
}

// Reconcile calculates queue order and waiting reasons for all queued jobs based on priority and slot capacity.
func (r *Reconciler) Reconcile(jobs []state.QueuedJob, busyRunners, maxRunners int) []state.QueuedJob {
	freeSlots := maxRunners - busyRunners
	if freeSlots < 0 {
		freeSlots = 0
	}

	prioList, pausedList := r.pm.GetState()
	prioMap := make(map[string]int)
	for idx, name := range prioList {
		prioMap[strings.ToLower(name)] = idx
	}

	pausedMap := make(map[string]bool)
	for _, name := range pausedList {
		pausedMap[strings.ToLower(name)] = true
	}

	var active []state.QueuedJob
	var paused []state.QueuedJob

	for _, j := range jobs {
		jobCopy := j
		if pausedMap[strings.ToLower(j.Repo)] {
			reason := "repository paused by administrator"
			jobCopy.QueuePosition = nil
			jobCopy.WaitingReason = &reason
			paused = append(paused, jobCopy)
		} else {
			active = append(active, jobCopy)
		}
	}

	sort.SliceStable(active, func(i, j int) bool {
		idxI, okI := prioMap[strings.ToLower(active[i].Repo)]
		idxJ, okJ := prioMap[strings.ToLower(active[j].Repo)]

		if okI && okJ {
			if idxI != idxJ {
				return idxI < idxJ
			}
		} else if okI && !okJ {
			return true
		} else if !okI && okJ {
			return false
		}

		timeI := ""
		if active[i].CreatedAt != nil {
			timeI = *active[i].CreatedAt
		}
		timeJ := ""
		if active[j].CreatedAt != nil {
			timeJ = *active[j].CreatedAt
		}
		if timeI != timeJ && timeI != "" && timeJ != "" {
			return timeI < timeJ
		}
		return active[i].ID < active[j].ID
	})

	for i := range active {
		pos := i + 1
		active[i].QueuePosition = &pos
		if i < freeSlots {
			active[i].WaitingReason = nil
		} else {
			reason := fmt.Sprintf("runner capacity reached (position %d)", pos)
			active[i].WaitingReason = &reason
		}
	}

	result := make([]state.QueuedJob, 0, len(active)+len(paused))
	result = append(result, active...)
	result = append(result, paused...)
	return result
}
