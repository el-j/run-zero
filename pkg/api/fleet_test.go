package api

import (
	"context"
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"testing"

	"github.com/el-j/run-zero/pkg/state"
)

func TestServer_HostHeaderAndCORS(t *testing.T) {
	srv, _, _, _, _ := setupTestServer(t)
	defer func() { _ = srv.Shutdown(context.Background()) }()

	addr := srv.Addr()
	url := "http://" + addr + "/api/status"

	reqOpt, _ := http.NewRequest(http.MethodOptions, url, nil)
	respOpt, err := http.DefaultClient.Do(reqOpt)
	if err != nil || respOpt.StatusCode != http.StatusNoContent {
		t.Fatalf("expected 204 for OPTIONS, got err=%v, code=%v", err, respOpt.StatusCode)
	}

	reqOk, _ := http.NewRequest(http.MethodGet, url, nil)
	respOk, err := http.DefaultClient.Do(reqOk)
	if err != nil || respOk.StatusCode != http.StatusOK {
		t.Fatalf("expected 200 for allowed host, got err=%v, code=%v", err, respOk.StatusCode)
	}

	reqBad, _ := http.NewRequest(http.MethodGet, url, nil)
	reqBad.Host = "evil.attacker.com"
	respBad, err := http.DefaultClient.Do(reqBad)
	if err != nil || respBad.StatusCode != http.StatusMisdirectedRequest {
		t.Fatalf("expected 421 for rejected host, got err=%v, code=%v", err, respBad.StatusCode)
	}

	h := CheckHostHeader(nil)(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		w.WriteHeader(http.StatusOK)
	}))

	rec1 := httptest.NewRecorder()
	reqLoopback := httptest.NewRequest("GET", "/api/status", nil)
	reqLoopback.Host = "127.0.0.1:49505"
	h.ServeHTTP(rec1, reqLoopback)
	if rec1.Code != http.StatusOK {
		t.Errorf("expected 200 for 127.0.0.1 loopback default, got %d", rec1.Code)
	}

	rec2 := httptest.NewRecorder()
	reqBadHost := httptest.NewRequest("GET", "/api/status", nil)
	reqBadHost.Host = "random.domain.com"
	h.ServeHTTP(rec2, reqBadHost)
	if rec2.Code != http.StatusMisdirectedRequest {
		t.Errorf("expected 421 for random host, got %d", rec2.Code)
	}
}

func TestServer_FleetAndLogs(t *testing.T) {
	srv, _, st, _, _ := setupTestServer(t)
	defer func() { _ = srv.Shutdown(context.Background()) }()

	addr := srv.Addr()

	resp, err := http.Get("http://" + addr + "/api/fleet")
	if err != nil || resp.StatusCode != http.StatusOK {
		t.Fatalf("GET /api/fleet failed: %v, code=%d", err, resp.StatusCode)
	}
	var fleet state.FleetState
	_ = json.NewDecoder(resp.Body).Decode(&fleet)
	if fleet.MaxRunners != 4 {
		t.Errorf("expected max_runners=4, got %d", fleet.MaxRunners)
	}

	respPost, _ := http.Post("http://"+addr+"/api/fleet", "application/json", nil)
	if respPost.StatusCode != http.StatusMethodNotAllowed {
		t.Errorf("expected 405 on POST /api/fleet, got %d", respPost.StatusCode)
	}

	st.AppendLog("system test log")
	respLogs, err := http.Get("http://" + addr + "/api/logs")
	if err != nil || respLogs.StatusCode != http.StatusOK {
		t.Fatalf("GET /api/logs failed: %v", err)
	}
	var logsResp map[string][]state.LogEntry
	_ = json.NewDecoder(respLogs.Body).Decode(&logsResp)
	if len(logsResp["logs"]) == 0 {
		t.Errorf("expected logs, got none")
	}

	respLogsBad, _ := http.Post("http://"+addr+"/api/logs", "application/json", nil)
	if respLogsBad.StatusCode != http.StatusMethodNotAllowed {
		t.Errorf("expected 405 on POST /api/logs, got %d", respLogsBad.StatusCode)
	}
}
