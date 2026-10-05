package api

import (
	"bytes"
	"context"
	"encoding/json"
	"net/http"
	"strings"
	"testing"
)

func TestServer_Settings(t *testing.T) {
	srv, cfg, _, _, _ := setupTestServer(t)
	defer func() { _ = srv.Shutdown(context.Background()) }()

	addr := srv.Addr()
	url := "http://" + addr + "/api/settings"

	resp, err := http.Get(url)
	if err != nil || resp.StatusCode != http.StatusOK {
		t.Fatalf("GET /api/settings failed: %v", err)
	}

	newMax := 8
	newMin := 2
	newPoll := 15
	payload := SettingsPayload{
		MaxRunners:   &newMax,
		MinRunners:   &newMin,
		PollInterval: &newPoll,
	}
	body, _ := json.Marshal(payload)
	respPost, err := http.Post(url, "application/json", bytes.NewReader(body))
	if err != nil || respPost.StatusCode != http.StatusOK {
		t.Fatalf("POST /api/settings failed: %v, code=%d", err, respPost.StatusCode)
	}
	if cfg.MaxRunners != 8 || cfg.MinRunners != 2 || cfg.PollInterval != 15 {
		t.Errorf("expected updated config values, got max=%d, min=%d, poll=%d", cfg.MaxRunners, cfg.MinRunners, cfg.PollInterval)
	}

	badMax := 0
	badBody, _ := json.Marshal(SettingsPayload{MaxRunners: &badMax})
	respBadMax, _ := http.Post(url, "application/json", bytes.NewReader(badBody))
	if respBadMax.StatusCode != http.StatusBadRequest {
		t.Errorf("expected 400 for max_runners < 1, got %d", respBadMax.StatusCode)
	}

	badMin := 10
	badBody2, _ := json.Marshal(SettingsPayload{MinRunners: &badMin})
	respBadMin, _ := http.Post(url, "application/json", bytes.NewReader(badBody2))
	if respBadMin.StatusCode != http.StatusBadRequest {
		t.Errorf("expected 400 for min > max, got %d", respBadMin.StatusCode)
	}

	negMin := -1
	badBodyNeg, _ := json.Marshal(SettingsPayload{MinRunners: &negMin})
	respBadNeg, _ := http.Post(url, "application/json", bytes.NewReader(badBodyNeg))
	if respBadNeg.StatusCode != http.StatusBadRequest {
		t.Errorf("expected 400 for min < 0, got %d", respBadNeg.StatusCode)
	}

	badPoll := 5000
	badBody3, _ := json.Marshal(SettingsPayload{PollInterval: &badPoll})
	respBadPoll, _ := http.Post(url, "application/json", bytes.NewReader(badBody3))
	if respBadPoll.StatusCode != http.StatusBadRequest {
		t.Errorf("expected 400 for poll > 3600, got %d", respBadPoll.StatusCode)
	}

	autoDisc := false
	autoRoute := false
	proxies := false
	cache := false
	otherPayload := SettingsPayload{
		AutoDiscover:   &autoDisc,
		AutoRouteVM:    &autoRoute,
		ProxiesEnabled: &proxies,
		CacheEnabled:   &cache,
	}
	otherBody, _ := json.Marshal(otherPayload)
	respOther, _ := http.Post(url, "application/json", bytes.NewReader(otherBody))
	if respOther.StatusCode != http.StatusOK {
		t.Errorf("expected 200 for other fields update, got %d", respOther.StatusCode)
	}

	respBadJSON, _ := http.Post(url, "application/json", strings.NewReader("bad-json{"))
	if respBadJSON.StatusCode != http.StatusBadRequest {
		t.Errorf("expected 400 for bad json, got %d", respBadJSON.StatusCode)
	}

	reqDel, _ := http.NewRequest(http.MethodDelete, url, nil)
	respDel, _ := http.DefaultClient.Do(reqDel)
	if respDel.StatusCode != http.StatusMethodNotAllowed {
		t.Errorf("expected 405 on DELETE, got %d", respDel.StatusCode)
	}
}
