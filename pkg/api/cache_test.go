package api

import (
	"bytes"
	"context"
	"encoding/json"
	"net/http"
	"strings"
	"testing"
)

func TestServer_CacheHandlers(t *testing.T) {
	srv, _, _, _, _ := setupTestServer(t)
	defer func() { _ = srv.Shutdown(context.Background()) }()

	addr := srv.Addr()

	resp, err := http.Get("http://" + addr + "/api/cache")
	if err != nil || resp.StatusCode != http.StatusOK {
		t.Fatalf("GET /api/cache failed: %v", err)
	}

	respCacheBad, _ := http.Post("http://"+addr+"/api/cache", "application/json", nil)
	if respCacheBad.StatusCode != http.StatusMethodNotAllowed {
		t.Errorf("expected 405 on POST /api/cache, got %d", respCacheBad.StatusCode)
	}

	purgeBody, _ := json.Marshal(CachePurgePayload{Category: "npm"})
	respPurge, err := http.Post("http://"+addr+"/api/cache/purge", "application/json", bytes.NewReader(purgeBody))
	if err != nil || respPurge.StatusCode != http.StatusOK {
		t.Fatalf("POST /api/cache/purge failed: %v", err)
	}

	purgeAll, _ := json.Marshal(CachePurgePayload{All: true})
	respPurgeAll, _ := http.Post("http://"+addr+"/api/cache/purge", "application/json", bytes.NewReader(purgeAll))
	if respPurgeAll.StatusCode != http.StatusOK {
		t.Errorf("expected 200 on purge all, got %d", respPurgeAll.StatusCode)
	}

	respPurgeBad, _ := http.Get("http://" + addr + "/api/cache/purge")
	if respPurgeBad.StatusCode != http.StatusMethodNotAllowed {
		t.Errorf("expected 405 on GET /api/cache/purge, got %d", respPurgeBad.StatusCode)
	}

	cleanBody, _ := json.Marshal(map[string]string{"category": "npm"})
	respClean, _ := http.Post("http://"+addr+"/api/actions/clean-cache", "application/json", bytes.NewReader(cleanBody))
	if respClean.StatusCode != http.StatusOK {
		t.Errorf("expected 200 on clean-cache, got %d", respClean.StatusCode)
	}

	badCleanBody, _ := json.Marshal(map[string]int{"category": 123})
	respBadClean, _ := http.Post("http://"+addr+"/api/actions/clean-cache", "application/json", bytes.NewReader(badCleanBody))
	if respBadClean.StatusCode != http.StatusBadRequest {
		t.Errorf("expected 400 for non-string category, got %d", respBadClean.StatusCode)
	}

	respBadCleanJSON, _ := http.Post("http://"+addr+"/api/actions/clean-cache", "application/json", strings.NewReader("bad{{{"))
	if respBadCleanJSON.StatusCode != http.StatusBadRequest {
		t.Errorf("expected 400 for bad json in clean-cache, got %d", respBadCleanJSON.StatusCode)
	}

	respCleanBadMethod, _ := http.Get("http://" + addr + "/api/actions/clean-cache")
	if respCleanBadMethod.StatusCode != http.StatusMethodNotAllowed {
		t.Errorf("expected 405 on GET clean-cache, got %d", respCleanBadMethod.StatusCode)
	}
}
