package inspector

import "testing"

func TestMatrixBase_EdgeCases(t *testing.T) {
	for in, want := range map[string]string{
		" (1, 2)":     "",
		"Test (1, 2)": "Test",
		"Test":        "Test",
	} {
		if got := MatrixBase(in); got != want {
			t.Errorf("MatrixBase(%q) = %q, want %q", in, got, want)
		}
	}
}

func TestUnquote_EmptyQuotedString(t *testing.T) {
	for in, want := range map[string]string{`""`: "", `''`: "", `"a"`: "a", `"`: `"`} {
		if got := unquote(in); got != want {
			t.Errorf("unquote(%q) = %q, want %q", in, got, want)
		}
	}
}

func TestParseWorkflowJobs_OnlyReadsTheJobsBlock(t *testing.T) {
	if jobs := ParseWorkflowJobs("on:\n  push:\n  pull_request:\n"); jobs != nil {
		t.Fatalf("a workflow without jobs: has no jobs, got %+v", jobs)
	}
	jobs := ParseWorkflowJobs("jobs:\n  build:\n    runs-on: x\nconcurrency:\n  notajob:\n")
	if len(jobs) != 1 || jobs[0].JobID != "build" {
		t.Fatalf("parsing must stop at the next top-level key, got %+v", jobs)
	}
}
