package api

import (
	"bytes"
	"context"
	"encoding/json"
	"io"
	"net/http"
	"strings"
	"testing"
)

func TestServer_Actions(t *testing.T) {
	srv, _, _, _, _ := setupTestServer(t)
	defer func() { _ = srv.Shutdown(context.Background()) }()

	addr := srv.Addr()

	prioBody, _ := json.Marshal(RepoPriorityPayload{Priority: []string{"repo1"}, Paused: []string{"repo2"}})
	respPrio, _ := http.Post("http://"+addr+"/api/actions/repo-priority", "application/json", bytes.NewReader(prioBody))
	if respPrio.StatusCode != http.StatusOK {
		t.Errorf("expected 200 on repo-priority, got %d", respPrio.StatusCode)
	}
	respPrioBadJSON, _ := http.Post("http://"+addr+"/api/actions/repo-priority", "application/json", strings.NewReader("bad"))
	if respPrioBadJSON.StatusCode != http.StatusBadRequest {
		t.Errorf("expected 400 on bad json repo-priority, got %d", respPrioBadJSON.StatusCode)
	}
	respPrioBadMethod, _ := http.Get("http://" + addr + "/api/actions/repo-priority")
	if respPrioBadMethod.StatusCode != http.StatusMethodNotAllowed {
		t.Errorf("expected 405 on GET repo-priority, got %d", respPrioBadMethod.StatusCode)
	}

	wfBody, _ := json.Marshal(WorkflowActionPayload{Repo: "org/repo", RunID: 101, Action: "rerun"})
	respWf, _ := http.Post("http://"+addr+"/api/actions/workflow", "application/json", bytes.NewReader(wfBody))
	if respWf.StatusCode != http.StatusOK {
		t.Errorf("expected 200 on workflow rerun, got %d", respWf.StatusCode)
	}
	wfBadRepo, _ := json.Marshal(WorkflowActionPayload{Repo: "", RunID: 101, Action: "rerun"})
	respWfBadRepo, _ := http.Post("http://"+addr+"/api/actions/workflow", "application/json", bytes.NewReader(wfBadRepo))
	if respWfBadRepo.StatusCode != http.StatusBadRequest {
		t.Errorf("expected 400 on empty repo, got %d", respWfBadRepo.StatusCode)
	}
	wfBadAction, _ := json.Marshal(WorkflowActionPayload{Repo: "org/repo", RunID: 101, Action: "destroy"})
	respWfBadAction, _ := http.Post("http://"+addr+"/api/actions/workflow", "application/json", bytes.NewReader(wfBadAction))
	if respWfBadAction.StatusCode != http.StatusBadRequest {
		t.Errorf("expected 400 on bad workflow action, got %d", respWfBadAction.StatusCode)
	}
	respWfBadJSON, _ := http.Post("http://"+addr+"/api/actions/workflow", "application/json", strings.NewReader("bad"))
	if respWfBadJSON.StatusCode != http.StatusBadRequest {
		t.Errorf("expected 400 on bad json workflow, got %d", respWfBadJSON.StatusCode)
	}
	respWfBadMethod, _ := http.Get("http://" + addr + "/api/actions/workflow")
	if respWfBadMethod.StatusCode != http.StatusMethodNotAllowed {
		t.Errorf("expected 405 on GET workflow, got %d", respWfBadMethod.StatusCode)
	}

	for _, act := range []string{"start", "stop", "pause", "resume", "drain"} {
		rBody, _ := json.Marshal(RunnerActionPayload{Action: act, RunnerID: "r-1"})
		respR, _ := http.Post("http://"+addr+"/api/actions/runner", "application/json", bytes.NewReader(rBody))
		if respR.StatusCode != http.StatusOK {
			t.Errorf("expected 200 on runner action %s, got %d", act, respR.StatusCode)
		}
	}
	badRunnerAction, _ := json.Marshal(RunnerActionPayload{Action: "terminate"})
	respBadRunner, _ := http.Post("http://"+addr+"/api/actions/runner", "application/json", bytes.NewReader(badRunnerAction))
	if respBadRunner.StatusCode != http.StatusBadRequest {
		t.Errorf("expected 400 for bad runner action, got %d", respBadRunner.StatusCode)
	}
	respBadRunnerJSON, _ := http.Post("http://"+addr+"/api/actions/runner", "application/json", strings.NewReader("bad"))
	if respBadRunnerJSON.StatusCode != http.StatusBadRequest {
		t.Errorf("expected 400 for bad json runner action, got %d", respBadRunnerJSON.StatusCode)
	}
	respRunnerBadMethod, _ := http.Get("http://" + addr + "/api/actions/runner")
	if respRunnerBadMethod.StatusCode != http.StatusMethodNotAllowed {
		t.Errorf("expected 405 on GET runner action, got %d", respRunnerBadMethod.StatusCode)
	}

	respPrune, _ := http.Post("http://"+addr+"/api/actions/prune", "application/json", nil)
	if respPrune.StatusCode != http.StatusOK {
		t.Errorf("expected 200 on prune, got %d", respPrune.StatusCode)
	}
	respPruneBadMethod, _ := http.Get("http://" + addr + "/api/actions/prune")
	if respPruneBadMethod.StatusCode != http.StatusMethodNotAllowed {
		t.Errorf("expected 405 on GET prune, got %d", respPruneBadMethod.StatusCode)
	}
}

func TestServer_SSEStreaming(t *testing.T) {
	srv, _, st, _, _ := setupTestServer(t)
	defer func() { _ = srv.Shutdown(context.Background()) }()

	addr := srv.Addr()

	req, _ := http.NewRequest(http.MethodGet, "http://"+addr+"/api/stream", nil)
	ctx, cancel := context.WithCancel(context.Background())
	defer cancel()
	req = req.WithContext(ctx)

	resp, err := http.DefaultClient.Do(req)
	if err != nil || resp.StatusCode != http.StatusOK {
		t.Fatalf("failed to connect SSE stream: %v", err)
	}
	defer resp.Body.Close()

	buf := make([]byte, 1024)
	n, err := resp.Body.Read(buf)
	if err != nil && err != io.EOF {
		t.Fatalf("failed reading SSE initial event: %v", err)
	}
	dataStr := string(buf[:n])
	if !strings.Contains(dataStr, "event: state") {
		t.Errorf("expected initial state event, got: %s", dataStr)
	}

	st.AppendLog("realtime sse event")

	n2, _ := resp.Body.Read(buf)
	dataStr2 := string(buf[:n2])
	if !strings.Contains(dataStr2, "realtime sse event") && !strings.Contains(dataStr2, ": ping") {
		t.Logf("received chunk: %s", dataStr2)
	}
}
