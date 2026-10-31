package inspector

import "testing"

func TestParseWorkflowJobs_StopsAtNextTopLevelKey(t *testing.T) {
	jobs := ParseWorkflowJobs("on: push\njobs:\n  a:\n    runs-on: ubuntu-latest\nenv:\n  A: b\n")
	if len(jobs) != 1 {
		t.Errorf("got %+v", jobs)
	}
}
