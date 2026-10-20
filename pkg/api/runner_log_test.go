package api

import (
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"testing"

	"github.com/el-j/run-zero/pkg/state"
)

func TestHandleRunnerLog(t *testing.T) {
	st := state.NewState(2, "test", nil)
	st.SetRunnerLog("runzero-a", "line1\nline2")
	h := handleRunnerLog(st)

	rec := httptest.NewRecorder()
	h(rec, httptest.NewRequest(http.MethodGet, "/api/runner-log?name=runzero-a", nil))
	if rec.Code != http.StatusOK {
		t.Fatalf("expected 200, got %d", rec.Code)
	}
	var body map[string]string
	if err := json.Unmarshal(rec.Body.Bytes(), &body); err != nil || body["log"] != "line1\nline2" {
		t.Fatalf("unexpected body %q (err=%v)", rec.Body.String(), err)
	}

	for url, want := range map[string]int{
		"/api/runner-log":                http.StatusBadRequest,
		"/api/runner-log?name=runzero-b": http.StatusNotFound,
	} {
		rec := httptest.NewRecorder()
		h(rec, httptest.NewRequest(http.MethodGet, url, nil))
		if rec.Code != want {
			t.Errorf("%s: expected %d, got %d", url, want, rec.Code)
		}
	}
}
