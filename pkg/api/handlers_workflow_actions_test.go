package api

import (
	"bytes"
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"testing"

	"github.com/el-j/run-zero/pkg/state"
)

func TestHandleWorkflowAction_RequestsHistoryRefreshAfterRetry(t *testing.T) {
	st := state.NewState(3, "test", nil)

	payload := WorkflowActionPayload{
		Repo:   "el-j/run-zero",
		RunID:  42,
		Action: "rerun-failed",
	}
	raw, _ := json.Marshal(payload)
	req := httptest.NewRequest(http.MethodPost, "/api/actions/workflow", bytes.NewReader(raw))
	rec := httptest.NewRecorder()

	handleWorkflowAction(st).ServeHTTP(rec, req)

	if rec.Code != http.StatusOK {
		t.Fatalf("expected 200, got %d", rec.Code)
	}
	if !st.ConsumeHistoryRefresh() {
		t.Fatalf("expected retry action to request history refresh")
	}
}

func TestHandleWorkflowAction_DoesNotRefreshHistoryOnCancel(t *testing.T) {
	st := state.NewState(3, "test", nil)

	payload := WorkflowActionPayload{
		Repo:   "el-j/run-zero",
		RunID:  42,
		Action: "cancel",
	}
	raw, _ := json.Marshal(payload)
	req := httptest.NewRequest(http.MethodPost, "/api/actions/workflow", bytes.NewReader(raw))
	rec := httptest.NewRecorder()

	handleWorkflowAction(st).ServeHTTP(rec, req)

	if rec.Code != http.StatusOK {
		t.Fatalf("expected 200, got %d", rec.Code)
	}
	if st.ConsumeHistoryRefresh() {
		t.Fatalf("did not expect cancel action to request history refresh")
	}
}
